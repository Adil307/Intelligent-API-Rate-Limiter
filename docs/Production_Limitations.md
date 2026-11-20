# Production limitations and future work

This is an educational local prototype. A shared Redis instance corrects the observed separate-process quota violation, but it is a single point of failure.

- Replace the client-controlled demo header with trusted, authenticated identity and enforce authorization.
- Bound identity cardinality and input lengths; plan Redis memory capacity, eviction and key policy. Evicted or lost quota state can permit additional requests.
- Secure Redis access with network isolation, authentication and TLS where appropriate. Do not expose a development Redis instance to public networks.
- Evaluate durability, persistence, failover, ambiguous request outcomes and time changes. Redis TIME is wall-clock time; it can move. Stop/restart response testing does not establish preserved quota history or safe failover.
- Test true multi-machine deployments, replicas/failover, repeated controlled benchmarks, soak tests and latency measurements under realistic traffic.
- Add observability for 429/503 counts, backend latency, saturation and memory. Consider retries carefully and do not automatically bypass the global quota.
- The term Intelligent is the project name; this design is deterministic and does not use ML or AI.
