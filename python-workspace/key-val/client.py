"""

[TODO:description]
"""

import argparse
from collections.abc import Iterator
import logging
from grpc import RpcError, StatusCode, insecure_channel
from key_val_pb2 import (
    GetResponse,
    PutRequest,
    GetRequest,
    DeleteResponse,
    DeleteRequest,
    PutResponse,
    WatchRequest,
    WatchResponse,
)
from key_val_pb2_grpc import KeyValueStoreStub


class KeyValueClient:
    def __init__(self):
        self.channel = insecure_channel("localhost:50051")
        self.stub = KeyValueStoreStub(self.channel)

    def doPut(self, key, value) -> PutResponse:
        request = PutRequest(key=key, value=value)
        return self.stub.PutKey(request)

    def doGet(self, key) -> GetResponse:
        request = GetRequest(key=key)
        return self.stub.GetKey(request=request)

    def doDelete(self, key) -> DeleteResponse:
        request = DeleteRequest(key=key)
        return self.stub.DeleteKey(request=request)

    def doWatch(self, key: str, timeout: float | None) -> Iterator[WatchResponse]:
        deadline = timeout if timeout is not None else 30.0
        request = WatchRequest(key=key)
        return self.stub.WatchKey(request=request, timeout=deadline)

    def close(self) -> None:
        self.channel.close()


def run():
    watch_timeout = 30.0  # Default watch period is 30 seconds
    client = KeyValueClient()
    parser = argparse.ArgumentParser(description="Key-Value Store Client CLI")

    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available commands"
    )

    put_parser = subparsers.add_parser("put", help="Upload a key-value pair")
    put_parser.add_argument("key", type=str, help="The key to store")
    put_parser.add_argument("value", type=str, help="The value to store")

    get_parser = subparsers.add_parser(
        "get", help="Get the value associated with a key"
    )
    get_parser.add_argument("key", type=str, help="The key to search for")

    delete_parser = subparsers.add_parser(
        "delete", help="Delete a key (and its associated value)"
    )
    delete_parser.add_argument(
        "key", type=str, help="The key of the key-value pair to delete"
    )

    watch_parser = subparsers.add_parser("watch", help="Watch a given key for updates")
    watch_parser.add_argument("key", type=str, help="The key to watch")
    watch_parser.add_argument(
        "--timeout",
        type=float,
        default=watch_timeout,
        help=f"The timeout for the watcher. Default wait time is {watch_timeout} seconds",
    )

    args = parser.parse_args()

    match args.command:
        case "put":
            response = client.doPut(key=args.key, value=args.value)
            print(f"{response.message}")
        case "get":
            response = client.doGet(key=args.key)
            if response.value == "":
                print("[null]")
            else:
                print(f'"{response.value}"')
        case "delete":
            response = client.doDelete(key=args.key)
            print(f"{response.message}")
        case "watch":
            timeout = args.timeout if args.timeout is not None else watch_timeout
            try:
                stream = client.doWatch(key=args.key, timeout=timeout)
                for response in stream:
                    update = response.update
                    old = update.old
                    new = update.new
                    if old.exists and not new.exists:  # delete
                        print(
                            f"Deleted entry '{old.key}' from the store.\nUpdate: {old.key}:{old.value}->None"
                        )
                    elif new.exists and not old.exists:  # Upserted
                        print(
                            f"Added entry '{new.key}' to the store.\nUpdate: None -> {new.key}:{new.value}"
                        )
                    else:  # Update
                        print(
                            f"Updated entry '{new.key}'.\nUpdate: {old.key}:{old.value}->{new.key}:{new.value}"
                        )
            except RpcError as e:
                if e.code() == StatusCode.DEADLINE_EXCEEDED:
                    print(f"Watcher stopped because the timeout has been reached")
                else:
                    print(f"Stream error: {e.details()}")

    client.close()


if __name__ == "__main__":
    logging.basicConfig()
    run()
