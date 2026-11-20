# Algorithm and complexity analysis

Let `L` be the maximum accepted requests per user per window, `U` the number of retained user keys, `N` the number of timestamps in the user's current stored collection, and `K` the number removed during a particular expiry operation. Assume ordered explicit timestamps for local tests, bounded input sizes, and expected constant-time hash-table operations.

| Operation | In-memory deque | Redis sorted set (server-side) |
|---|---|---|
| Remove expired timestamps | O(K) | O(log N + K) |
| Count | O(1) | O(1) |
| Insert accepted timestamp | O(1) | O(log N) |
| Read oldest timestamp | O(1) | O(log N + 1) for ZRANGE |
| Worst single decision | O(L) | O(log(L+1) + K), K <= L |
| Amortized decision | Expected O(1) | O(log(L+1)) amortized under the usual sorted-set bounds |

For the deque, each accepted timestamp is inserted once and removed once, so expiry work can be charged to prior insertions. Redis likewise removes each inserted timestamp at most once, but sorted-set indexing introduces logarithmic work. These are algorithmic bounds, not HTTP latency guarantees. Redis may use compact sorted-set encodings for small sets; physical costs depend on implementation and configuration.

Stored timestamp space is O(U × L), plus O(U) keys/metadata. Idle keys in the in-memory implementation may persist until explicit cleanup. A full sweep takes O(U + K_total) time and O(U) auxiliary space for a snapshot of dictionary entries. Redis TTL reclaims idle keys, but total memory still depends on the number of distinct identities submitted. A global lock or the Redis command execution path can serialize decisions and add queueing latency. Network/client overhead and server memory overhead are excluded from these abstract bounds.

## References

- Redis ZREMRANGEBYSCORE: https://redis.io/docs/latest/commands/zremrangebyscore/
- Redis ZADD: https://redis.io/docs/latest/commands/zadd/
- Redis ZRANGE: https://redis.io/docs/latest/commands/zrange/
- Redis ZCARD: https://redis.io/docs/latest/commands/zcard/
- Redis scripting: https://redis.io/docs/latest/develop/programmability/eval-intro/
