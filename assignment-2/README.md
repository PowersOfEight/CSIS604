# Assignment 2

**Summary:** Create a containerized micro-service component by building and deploying a base image.

---

## Attribution

<table>
  <tr><th align="left">Author</th><td>James Daniel Johnson</td></tr>
  <tr><th align="left">CWID</th><td>20183229</td></tr>
  <tr><th align="left">Course</th><td>CSIS 604 - Distributed Systems</td></tr>
  <tr><th align="left">Assignment</th><td>2 - Containerizing a Distributed Micro-Node Service</td></tr>
</table>

## Discussion

### Prompt

> In 2–3 sentences, explain why we set `host="0.0.0.0"`
> in `app.py` instead of host="127.0.0.1" when binding a server inside a Docker container.

### Answer

The _semantic meaning_ of setting a host to the _wildcard address_ (aka `"0.0.0.0"` in IPv4 or `[::]` in IPv6) is "this host listens on all available addresses assigned to this machine". Since this application is containerized, its loopback address (resolved from `localhost`, `127.0.0.1` using IPv4, `::1` using IPv6) only point to the process running _inside the container_. Hence, if we want to be able to reach it from the host machine (or an outside network via port forwarding), we need it to listen to all of its available addresses, so we set it to the wildcard address.
