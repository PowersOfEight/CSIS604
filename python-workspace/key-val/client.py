import argparse
import logging
from grpc import insecure_channel
from key_val_pb2 import PutRequest, PutResponse
from key_val_pb2_grpc import KeyValueStoreStub


def doPut(key, value):
    with insecure_channel("localhost:50051") as channel:
        stub = KeyValueStoreStub(channel)
        request = PutRequest(key=key, value=value)
        response = stub.PutKey(request)
        print(f"{response.message}")


def run():
    parser = argparse.ArgumentParser(description="Key-Value Store Client CLI")

    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available commands"
    )

    put_parser = subparsers.add_parser("put", help="Upload a key-value pair")
    put_parser.add_argument("key", type=str, help="The key to store")
    put_parser.add_argument("value", type=str, help="The value to store")

    args = parser.parse_args()

    match args.command:
        case "put":
            doPut(key=args.key, value=args.value)


if __name__ == "__main__":
    logging.basicConfig()
    run()
