# Class 4

## Assignment 1 QA

### What kind of problems can I do for MapReduce?

- MergeSort
- Maze
- Sudoku Solver
- Word Count
- Deduplication

The Reduce can be pretty much any reduction ($O(n)$)

## Assignment 2

- <a href="#containers">Containerizing</a> a micronode service!!!
- Can use [Flask](https://flask.palletsprojects.com/en/stable/) or [FastAPI](https://fastapi.tiangolo.com/)
- Create a `requirements.txt` to make sure all dependencies are downloaded
- [Docker Compose](https://docs.docker.com/compose/) or [Dockerfile](https://docs.docker.com/reference/dockerfile/) (though docker compose is overkill for this one)
- Also OK to use [Singularity](https://docs.sylabs.io/guides/3.5/user-guide/introduction.html)
  - Singularity uses a higher level of Isolation
  - does not borrow the kernel, all work is done in user-space
  - for this reason, it is often used in High Performance Computing (HCI)

## <span id="containers">Containers</span>

- <span id="namespace">**Namespaces**:</span>a collection of processes in a container given their own view of identifiers
- <span id="union-filesystem">**Union file system**:</span> combine several file systems into a layered fashion with the highest layer allowing for `write` operations
- <span id="control-groups">**Control groups:**</span>resource restrictions can be imposed upon a collection of processes

The <a href="#namespace">Namespaces</a> and <a href="#control-groups">Control Groups</a> offer an increased level of **Isolation**

The [Union filesystem](#union-filesystem)

## Chapter 05 - Coordination

It's _likely_ the third assignment will be from this chapter.

This is where we get into most _**algorithms**_ and thus the most technically challenging part of the course. We have the problem of reliably forming a [consensus](#consensus)

### <span id="consensus">Consensus</span>

### Physical Clocks

#### Problem

Sometimes we simply need the exact time, not just an ordering

#### Solution: Universal Coordinated Time (UTC)

- based on the number of transitions per second of the cesium 133 atom
- at present, the real time is taken as the average of some 50 cesium clocks around the world
- introduces a **leap second** from time to time to compensate that days are getting longer

- **NOTE**: UTC is broadcast through short-wave radio and satellite. Satellites can give an accuracy of about plus/minus $\pm$ 0.5 ms

#### Precision

The goal is to keep the deviation between two clocks on any two machines within a specified bound, known as the precision $\pi$:

$$
  \forall C
$$

#### Clock Drift

##### Clock specifications

- A clock comes specified with it's maximum clock drift rate $\rho$
- $F(t)$ denotes oscillator frequency of the hardware clock at time $t$
- $F$ is the clock's ideal (constant) frequency $\implies$ living up to specifications:

$$
  \forall\ t:(1-\rho) \leq \frac{F(t)}{F} \leq (1-\rho)
$$

#### Detecting and adjusting incorrect times

#### Network Time Protocol

#### The Happened-before relationship

##### Issue

What usually matters is not that all processes agree on exactly what time it is but that they agree on the _order in which events occur_, which requires a _notion of ordering_.

- If $a$ and $b$ are two events in the same process, and $a$ comes before $b$, then $a \to b$
- If $a$ is sending a message, and $b$ is the receipt of that message, then $a \to b$
- If $a \to b$ and $b \to c$ then $a \to c$

##### Logical Clocks

#### Problem

How do we maintain a global view of the system's behavior that is consistent with the Happened-before relationship

Attach a timestamp $C(e)$ to each event $e$, satisfying the following properties

P1 - If $a$ and $b$ are two events in the same process, and $a \to b$ then we demand that $C(a) \lt C(b)$

P2 - If $a$ corresponds to sending a message $m$, and $b$ to the receipt of that message, then also $C(a) \lt C(b)$

#### Problem

How to attach a timestamp to an event when there's no global clock $\implies$ maintain a consistent set of logical clocks, one per process

#### Logical Clocks: solution

Each process $P_i$ maintains a local counter $C_i$ and adjusts this counter

1. <span id="sol-1"></span>For each new event that takes place within $P_i,\ C_i$ is incremented by 1
2. Each time a message $m$ is send by process $P_i$, the message receives a timestamp $ts(m) = C_i$.
3. Whenever a message $m$ is received by a process $P_j,\ P_j$ adjusts its local counter $C_j$ to $max(C_j, ts(m))$; then executes step 1 before passing $m$ to the application.

**NOTES**:

- Property $P_1$ is satisfied by [(1)](#sol-1)
- It can still occur that two events happen at the same time. Avoid this by breaking ties through process IDs

#### Logical Clocks: where implemented

Adjusgements implemented in middleware

##### Example: totally ordered multicast

Concurrent updates on a replicated database are seen in the same order everywhere

- $P_1$ adds \$100 to an account (initial value \$1000)
- $P_2$ increments account by 1\%
- There are two replicas

##### Result

In absence of proper synchronization:
replica \#1 $\leftarrow$ \$1111, while replica \#2 $\leftarrow$ \$1110

##### Solution

- Process $P_i$ sends timestamped message $m_i$ to all others. The message itself is put in a local queue $q_i$.
- Any incoming message at $P_j$ is queued in $q_j$, according to its timestamp, and acknowledge

#### Lamport's clocks for mutual exclusion

Analogy with totally ordered multicast

- With totally ordered multicast, all processes build identical queues, delivering messages in the same order
- Mutual exclusion is about agreeing in which order processes are allowed to enter the critical section
