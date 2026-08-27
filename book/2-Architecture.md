# Chapter 2 - Architecture

---

## Introduction

Distributed systems are often complex pieces of software of which the components
are by definition dispersed across multiple machines. To master their complexity,
it is crucial that these systems are properly organized.  There are different ways
to view the organization of a distributed system, and we focus on two specific ways
to do this.

- **Software Architecture** describes the intended interaction and organization of the
software components of a distributed system.
  - **Middleware** exists to separate the applications from the underlying platforms
  - Engineering trade-offs must be made to achieve transparency while allowing application
  utility.
  - **System Architecture** is the final instantiation of **software architecture**

The focus of this chapter will be **centralized architectures** where the server
implements most or all of the software components and functionality while remote
clients access the server (server-client architectures) and **decentralized** or
**peer-to-peer (P2P)** architectures in which each vertex in the graph is of an
equivalent class.  We will also include examples of real-world **hybrid architectures**.
