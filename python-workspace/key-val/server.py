# Author: James Daniel Johnson
# Course: CSIS 604 - Distributed Systems
# Instructor: Leclerc
# Assigment: Assignment 1 - Key Value Server
#

"""
The Python implementation of the in-memory key value store.
Utilizes `protobuf` generated code to store key-value pairs
"""

from collections import deque
import logging
from collections.abc import Callable
from concurrent import futures
from threading import Condition, RLock, Lock

import grpc
import key_val_pb2
import key_val_pb2_grpc
from key_val_pb2 import EntryState, UpdateEvent, WatchResponse


class UpdatePublisher:
    def __init__(self) -> None:
        self.subscriptions: dict[str, list[Callable[[UpdateEvent], None]]] = {}
        self._lock: Lock = Lock()

    def subscribe(self, key: str, listener: Callable[[UpdateEvent], None]):
        with self._lock:
            if key not in self.subscriptions:
                self.subscriptions[key] = []
            self.subscriptions[key].append(listener)

    def unsubscribe(self, key: str, listener: Callable[[UpdateEvent], None]):
        with self._lock:
            if key in self.subscriptions:
                try:
                    self.subscriptions[key].remove(listener)
                    if len(self.subscriptions[key]) == 0:
                        self.subscriptions.pop(key)
                except ValueError:
                    pass

    def publish(self, key: str, update: UpdateEvent):
        with self._lock:
            listeners = list(self.subscriptions.get(key, []))

        for listener in listeners:
            listener(update)


class KeyValueService(key_val_pb2_grpc.KeyValueStoreServicer):
    def __init__(self):
        self.store = {}
        self.publisher = UpdatePublisher()
        self._store_lock = RLock()

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

        # Obtain key prior to mutating state
        with self._store_lock:
            prev_state = self.state(key)
            self.store[key] = value
            is_update = not prev_state.exists or prev_state.value != value
            curr_state = self.state(key)

        # Publish if update occurred
        if is_update:
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

        with self._store_lock:
            prev_state = self.state(key)
            if prev_state != None and prev_state.exists:
                self.store.pop(key, None)
                curr_state = self.state(key)
                is_update = True
                response = key_val_pb2.DeleteResponse(
                    message=f"Successfully removed key {key} from the store.",
                    success=True,
                )
            else:
                response = key_val_pb2.DeleteResponse(
                    message=f"Key {key} not found in the store.",
                    success=False,
                )
        if is_update:
            self.publisher.publish(
                key=key, update=UpdateEvent(old=prev_state, new=curr_state)
            )

        return response

    def WatchKey(self, request, context):
        key = request.key
        condition = Condition()
        event_queue = deque()

        def listener(update: UpdateEvent):
            with condition:
                event_queue.append(update)
                condition.notify_all()

        self.publisher.subscribe(key=key, listener=listener)

        try:
            while context.is_active():
                with condition:
                    while not event_queue and context.is_active():
                        # Wait for up to one second
                        condition.wait(timeout=1.0)

                    while event_queue:
                        update = event_queue.popleft()
                        yield WatchResponse(update=update)

        except Exception as e:
            print(f"WatchKey stream terminated for key '{key}'.\nCause: {e}")
            context.set_code(grpc.StatusCode.CANCELLED)
            context.set_details(f"Stream interrupted.\nCause: {str(e)}")
        finally:
            self.publisher.unsubscribe(key=key, listener=listener)


def serve():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    key_val_pb2_grpc.add_KeyValueStoreServicer_to_server(KeyValueService(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Server listening on port {port}")
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
