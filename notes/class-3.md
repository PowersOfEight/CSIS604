# Class 3 - 2026-09-07

## <span id="Q/A">Homework Q/A</span>

### <span id="submissions">Submissions</span>

**Q:** How do you want this turned in? Tarball? Github repo?

**A:** Artifacts are a folder and several subfolders. Preference is to create a `*.tar.gz` (or `*.tgz`) file for the archive.

**Q:** What does the submitted directory need to include?

**A:** Just need the artifacts created; the `grpc_tools` `pip` installation dependencies is unnecessary, but the generated `*.pyi?` files will prevent having to recompile it from source.
We **do** want the `README.md` for running the files appropriately

Suggested List of Files:

- `*.proto` protobuf definitions
- `README.md` as documentation
- `*.pyi?` files with implementations
- generated `*pb2*` files for convenience

## Chapter 3 : Processes

Everything running running in the cloud is running as a process

### Context Switching

#### Contexts

- Processor context: the minimal collection of values stored in the registers of a processor used for the execution of a series of instructions (e.g. stack pointer, addressing registers, program counter)
- Thread context: the minimal collection of values stored in registers and memory, used for the execution of a series of instructions (i.e. processor context, state)
- Process context: the minimal collection of values stored in registers and memory, used for the execution of a thread (i.e. the thread context)

### Why Use Threads

- Avoids needless blocking
- Exploit parallelism
- Avoid process switching

### Threads and Operating Systems

**Most** people doing threading are using OS for threading for _true_ parallelism.

### Using Threads at the Client Side

- Multithreaded web Client

Thread level parallelism: TLP

$$
  TLP=\frac{\sum_{i=1}^{N}i \cdot c_i}{1 - c_0}
$$

### Mimicking Interfaces

### Out-of-band communication

#### Issue

Is it possible to _interrupt_ a server once it has accepted (or is in the process of accepting) a service request?

#### Solution 1: Use a separate port for urgent data

## Chapter 4 - Communication

### Low-level Layers

- Physical Layers
- Data Link layer
- Network Layer

### Transport Layer

- TCP: connection-oriented, reliable, stream-oriented communication
- UDP: unreliable (best-effort) datagram communication

### Middleware Layer

Middleware is invented to provide _common_ services and protocols that can be used by many _different_ applications.

- A rich set of **communication protocols**
- (Un)marshalling of data

### MPI: When lots of flexibility is needed

> [!NOTE]
> MPI is cpu intensive as opposed to gpu intesnsive

- Often used in high-performance clusters

### AMQP

### Multicasting

- Often a _tree_
- Also mesh networks requiring a form a routing
