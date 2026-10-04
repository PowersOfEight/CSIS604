# Peer To Peer (P2P) Notes

## Essence

### Slide notes

- Each data item is associated with unique _key_ which is obtained through hashing,
  e.g. _key(data item) = hash(data item value)_
- The P2P system stores _(key,value)_ ordered pairs T
- Lookups follow a predefined routing path from the _requesting node_ to the _service node_

### Thoughts on how key-ing makes distribution possible

The core problem in a distributed system is **_location independence_**, i.e. how does a node
know where to send or look for data without a _centralized_ database saying that
"_file L is on server R_"? Keying helps solve this riddle by mapping both the **data** and
**network nodes** into the same mathematical space. The system doesn't just hash the data,
it hashes the node properties (such as IP address) to give each node a unique-identifier.

This allows for **deterministic routing**, where the system uses a distance metrix (like XOR in kademlia)
to decide which node is responsible for storing which key. This allows the requesting node to search
for a data packet without flooding the network blindly.

A key feature of the hashing protocol (using the hashed value of the data as the key) is that is
difficult to _alter the data_ since the underlying key is _necessarily dependent on the value_.
This means that if some malicious actor hosts a node with altered data, it is easy enough (efficient)
to validate against the data packet. This means that the integrity of the data can be reassured
even though the data is distributed amongst many nodes.

## Overlays

- A peer to peer network is constructed as an **_overlay_**
  - A node is formed by a process (software defined)
  - A TCP connection handles message-passing between the software processes
  - Connections can change over time - who knows who?

### Thoughts on how these peer to peer overlays affect the robustness of peer to peer systems

## The Chord Network

### Basic Organization

- Chord _nodes_ store files. Each file receives a _unique_ $m$-bit key
- Each _node_ also receives a unique $m$-bit identifier (key...?)
- File $f$ with key $k$ is stored by node $p$ with smallest
  $id(p) \geq k$ called the **_successor_** or $succ(k)$.
- Node $p$ is assumed to have id $p$
- Each node $p$ maintains a **_finger table_** $FT_p[]$ with **_no more than_** $m$ entries

$$
  FT_p[i] = succ(p + 2^{i-1})
$$

- The $i$-th entry points to the first node succeeding $p$ by at least $2^{i-1}
- To look up a key $k$, node $p$ forwards the request to a node $q$ with index $j$
  satisfying

$$
  q = FT_p[j] \leq k \lt FT_p[j+1]
$$

- If $p \lt k \lt FT_p[1]$, the request is also forwarded to $FT_p[1]$
