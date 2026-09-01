# Class 2

First project -> `gRPC` with `protobuff`

## What the heck is protobuff?

---
So `JSON` is like key-value pairs, evidently protobuff is some similar type of key-value pairs.

Looks like it stands for _protocol buffers_.

**URI**: _uniform resource identifier_

```openapi.yaml
version: 3.0

```

```body.json
{
  "id": 10,
  "name": "doggie",
  "category": {
    "id": 1,
    "name": "Dogs"
  },
  "photoUrls": [
    "string"
  ],
  "tags": [
    {
      "id": 0,
      "name": "string"
    }
  ],
  "status": "available"
}
```

## Protocol Buffers are

Like an _improved_ version of `JSON`.  They have types and they're better

- faster (de)?serialization into binary
- strong typing
- Runs on HTTP/2

### Goal of the coordinator is to **keep the worker's busy (optimize utilization)**

#### Idempotency

Let $S$ be the set of states a system can hold, and let an operation $Op: S \to S$ such that
$$
\forall s \in S, n \geq 1, Op^n(s) = Op(s)
$$

We call $Op$ an **idempotent** operation.

---

## Architecture (Because, ya know)
