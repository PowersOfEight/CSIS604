# Introduction

## Distributed vs Decentralized

* A **decentralized system** is a networked computer system in which processes and resources are _necessarily_ spread across multiple computers
* A **distributed system** is a networked computer in which processes and resources are _sufficiently_ spread across mutliple computers

### Two Views - Integritive vs. Expansive

* [ ] - todo

---

## Misconceptions

### Logically vs Physically centralized

* DNS
  * logically centralized
  * physically distributed
  * decentralized across several organizations

* **Centralized solutions have a single point of failure**

---

## Design Goals

* Sharing of resources
* Distribution transparency (not always desirable)
* Openness - as in openness of policy and specification
  * It's generally desirable to have policy and specification be configurable by the
  end-user rather than the vendor (lock-in)
  * Regulatory market capture can hamper business operations
* Scalability

---

## Sharing Resources

### Canonical Examples

* Cloud-based shared storage and files
* P2P assisted multimedia streaming
* Shared mail services
* Shared Web hosting

### Observation

> "The network is the computer" - John Gage

---

## Distribution Transparency

### Types

| Transparency | Description |
| --- | --- |
| Access | Hide differences in data representation and how an object is accessed |
| Location | hide where an object is located |
| Relocation | Hide that an object may be moved to another location while in use |
| Migration | hide that an object may move to another location |
| Replication | Hide that an object is replicated |
| Concurrency | Hide that an object may be shared by several users simultaneously |

---

## Openness of distributed systems

### Open distributed system

_A system that offers..._

---

## Policies versus mechanisms

### Policy $\to$ Requirements

### Mechanism $\to$ Implementation

---

## Dependability

### Basics

A **component** provides **services** to **clients**.  **_Graceful Degradation_** is the ability to
maintain the function of a system in the case of some fault of the components,
where functionality is maintained while performance may suffer

---

## Terminology

### Failure vs Error vs Fault

| Term | Description | Example |
|---|---|---|
|Fault Prevention | Prevent the occurrence of a fault | Proactive validation |

---

## On Security

### Observation

A distributed system that is not secure is not dependable

---

## Security Mechanisms

### Symmetric Cryptosystem

With encryption key $E_k(\text{data})$ and decryption key $D_k(\text{data})$ :

```python
if E_k(data) :
```

---

## Problems with administrative Scalability

### Essence

conflicting policies concerning usage (and thus payment), managemnet, and Security

#### Examples

* computational grids: share expensive resource between different domains
* shared equipment: how to control manage and use shared radio, telescope

---

## Techniques for scaling

### Hide Communication latencies

### Caching

---

## Pitfalls of developing distributed systems

### Observation

Many distributed systems are needlessly complex, caused by mistakes that required patching
later on.  Many **false assumptions** are often made

#### False assumptions
* The network is reliable
* the network is secure
* the network is homogenous
