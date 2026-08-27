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

---

## 2.1 Architectural Styles

**Def: _Software Architecture_**: the logical organization of a distributed system
into software components

**Def: _Architectural Style_**: the way that software components are connected to each
other, how they exchange data, and how they are configured into a system

**Component**: A modular unit with well-defined required and provided **interfaces**
such that it is _replaceable_ within its environment.

- _replacement_ must be able to occur while the rest of the system runs
- **interfaces** must not change
- It is often impossible to shut down the system for maintenance

**Connector**: a mechanism that mediates communication, coordination, or cooperation
among components

### Key Architectural Styles

- Layered Architectures
- Object-based architectures
- Resource-centered architectures
- Event-based architectures
