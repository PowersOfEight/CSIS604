"""

[TODO:description]
"""

import argparse
import logging
from grpc import insecure_channel
from key_val_pb2 import (
    GetResponse,
    PutRequest,
    GetRequest,
    DeleteResponse,
    DeleteRequest,
    PutResponse,
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


def run():
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


if __name__ == "__main__":
    logging.basicConfig()
    run()
