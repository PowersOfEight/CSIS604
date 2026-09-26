# Author: James Daniel Johnson
# CWID: 20183229
# Course: CSIS 604 - Distributed Systems
# Assignment: 2.1 Python REST service

import os
import socket

from flask import Flask, Response, jsonify

app = Flask(__name__)

# Use the environment variables to set node identity
NODE_ID = os.environ.get("NODE_ID", "default-node")
PORT = int(os.environ.get("PORT", "5000"))


@app.route("/", methods=["GET"])
def index() -> tuple[Response, int]:
    return jsonify(
        {
            "status": "online",  # aka "up"
            "node_id": NODE_ID,
            "hostname": socket.gethostname(),
        }
    ), 200


@app.route("/health", methods=["GET"])
def health() -> tuple[Response, int]:
    return jsonify({"status": "healthy"}), 200


if __name__ == ("__main__"):
    app.run(host="0.0.0.0", port=PORT)  # Listens on all available addresses
