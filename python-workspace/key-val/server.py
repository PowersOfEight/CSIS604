# Author: James Daniel Johnson
# Course: CSIS 604 - Distributed Systems
# Instructor: Leclerc
# Assigment: Assignment 1 - Key Value Server
#

"""
The Python implementation of the in-memory key value store.
Utilizes `protobuf` generated code to store key-value pairs
"""

import signal
import sys
from collections import deque
from collections.abc import Callable
from concurrent import futures
from logging import DEBUG, Logger, basicConfig, getLogger
from threading import Condition, Event, Lock, RLock

import grpc
import key_val_pb2
import key_val_pb2_grpc
from key_val_pb2 import EntryState, UpdateEvent, WatchResponse


class UpdatePublisher:
    """
    Publisher component used to publish
    event updates to listening threads
    """

    def __init__(self) -> None:
        self.subscriptions: dict[str, list[Callable[[UpdateEvent], None]]] = {}
        self._lock: Lock = Lock()
        self.logger: Logger = getLogger(self.__class__.__name__)

    def subscribe(self, key: str, listener: Callable[[UpdateEvent], None]):
        """
        Registers a listener with the publisher
        """
        self.logger.info(
            "Subscribing listener id=%d to listen for updates to key=%s",
            id(listener),
            key,
        )
        with self._lock:
            if key not in self.subscriptions:
                self.logger.debug("Adding key=%s to subscriptions", key)
                self.subscriptions[key] = []
            self.subscriptions[key].append(listener)

    def unsubscribe(self, key: str, listener: Callable[[UpdateEvent], None]):
        """
        Removes a listener from the publisher
        """
        self.logger.info(
            "Attempting to unsubscribe listener id=%d from watching key=%s",
            id(listener),
            key,
        )
        with self._lock:
            if key in self.subscriptions:
                try:
                    self.subscriptions[key].remove(listener)
                    if len(self.subscriptions[key]) == 0:
                        self.logger.debug(
                            "No more subscrptions for key=%s, removing key from watchlist",
                            key,
                        )
                        self.subscriptions.pop(key)
                except ValueError as e:
                    self.logger.error(
                        "Error removing listener id=%d from subscription to key=%s: %s",
                        id(listener),
                        key,
                        e,
                    )
            else:
                self.logger.warning(
                    "No subscriptions found for key=%s, could not unsubscribe", key
                )

    def publish(self, key: str, update: UpdateEvent):
        """
        Publishes UpdateEvent to listeners
        """
        self.logger.info("Publishing update for key=%s", key)
        with self._lock:
            listeners = list(self.subscriptions.get(key, []))
        for listener in listeners:
            self.logger.debug("Activating listener id=%d with update", id(listener))
            listener(update)


class KeyValueService(key_val_pb2_grpc.KeyValueStoreServicer):
    def __init__(self, shutdown_event: Event):
        self.store: dict = {}
        self.publisher: UpdatePublisher = UpdatePublisher()
        self._store_lock: RLock = RLock()
        self.shutdown_event: Event = shutdown_event
        self.logger: Logger = getLogger(self.__class__.__name__)

    def state(self, key) -> EntryState:
        """
        Returns the state of the store. Use of Reentrant Lock (`RLock`)
        allows the caller to have the key so long as it's on the same thread
        """
        with self._store_lock:
            exists = key in self.store
            return EntryState(
                exists=exists, key=key, value=self.store[key] if exists else None
            )

    def PutKey(self, request, context):
        # Preamble with defaults
        key = request.key
        value = request.value
        is_update = False
        prev_state = None
        curr_state = None

        self.logger.info("Putting entry {%s:%s}", key, value)
        # Obtain key prior to mutating state
        with self._store_lock:
            prev_state = self.state(key)
            self.store[key] = value
            is_update = not prev_state.exists or prev_state.value != value
            curr_state = self.state(key)

        # Publish if update occurred
        if is_update:
            self.logger.debug("Publishing update to key %s", key)
            self.publisher.publish(
                key=key,
                update=UpdateEvent(
                    old=prev_state,
                    new=curr_state,
                ),
            )

        return key_val_pb2.PutResponse(
            message=f"Successfully put {key}:{value} into the store!", success=True
        )

    def GetKey(self, request, context):
        key = request.key
        state = None
        with self._store_lock:
            state = self.state(key=key)
        value = state.value if state != None and state.exists else None
        return key_val_pb2.GetResponse(value=value, state=state)

    def DeleteKey(self, request, context):
        key = request.key
        prev_state = None
        curr_state = None
        is_update = False

        self.logger.info("Deleting entry with key %s", key)
        with self._store_lock:
            prev_state = self.state(key)
            if prev_state != None and prev_state.exists:
                self.logger.debug("Found entry with key %s, deleting...")
                self.store.pop(key, None)
                curr_state = self.state(key)
                is_update = True
                response = key_val_pb2.DeleteResponse(
                    message=f"Successfully removed key {key} from the store.",
                    success=True,
                )
            else:
                self.logger.warning("Could not find key %s in the store to delete", key)
                response = key_val_pb2.DeleteResponse(
                    message=f"Key {key} not found in the store.",
                    success=False,
                )
        if is_update:
            self.logger.debug(
                "Deletion of key %s successful, publishing update...", key
            )
            self.publisher.publish(
                key=key, update=UpdateEvent(old=prev_state, new=curr_state)
            )

        return response

    def WatchKey(self, request, context):
        key = request.key
        condition = Condition()
        event_queue = deque()

        def listener(update: UpdateEvent):
            self.logger.debug("Recieved update event, appending to queue")
            with condition:
                event_queue.append(update)
                condition.notify_all()

        self.publisher.subscribe(key=key, listener=listener)

        try:
            while context.is_active() and not self.shutdown_event.is_set():
                events = []
                with condition:
                    while (
                        not event_queue
                        and context.is_active()
                        and not self.shutdown_event.is_set()
                    ):
                        # Wait for up to one second
                        condition.wait(timeout=1.0)

                    while event_queue:
                        events.append(event_queue.popleft())

                if len(events) > 0:
                    self.logger.debug(
                        "Found %d updates in event queue, sending updates...",
                        len(events),
                    )
                for update in events:
                    yield WatchResponse(update=update)

        except grpc.RpcError as e:
            self.logger.error(
                "WatchKey stream terminated for key '%s'.\nCause: %s", key, e
            )
            context.set_code(grpc.StatusCode.CANCELLED)
            context.set_details(f"Stream interrupted.\nCause: {e!s}")
        finally:
            self.logger.info(
                "Unsubscribing listener id=%d from watching key %s in WatchKey",
                id(listener),
                key,
            )
            self.publisher.unsubscribe(key=key, listener=listener)


def serve():
    port = "50051"
    shutdown_event = Event()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    key_val_pb2_grpc.add_KeyValueStoreServicer_to_server(
        KeyValueService(shutdown_event=shutdown_event), server
    )
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Server listening on port {port}")

    def shutdown_handler(signum, frame):
        shutdown_event.set()

        cleanup = server.stop(grace=10.0)
        cleanup.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    server.wait_for_termination()


if __name__ == "__main__":
    basicConfig(level=DEBUG)
    serve()
