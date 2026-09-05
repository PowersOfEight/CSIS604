# Author: James Daniel Johnson
# Course: CSIS 604 - Distributed Systems
# Instructor: Leclerc
# Assigment: Assignment 1 - Key Value Server
#

"""
The Python implementation of the in-memory key value store.
Utilizes `protobuf` generated code to store key-value pairs
"""

import logging
from concurrent import futures

import grpc
import key_val_pb2
import key_val_pb2_grpc


class KeyValueServer(key_val_pb2_grpc.KeyValueStoreServicer):
    def __init__(self):
        self.store = {}

    def PutKey(self, request, context):
        key = request.key
        value = request.value
        self.store[key] = value

        return key_val_pb2.PutResponse(
            message=f"Successfully put {key}:{value} into the store!"
        )


def serve():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    key_val_pb2_grpc.add_KeyValueStoreServicer_to_server(KeyValueServer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Server listening on port {port}")
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
