-- KEYS[1]: per-user sorted set; ARGV: limit, window (ms), unique request ID
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2]) * 1000
local t = redis.call('TIME')
local now = tonumber(t[1]) * 1000000 + tonumber(t[2])
local function integer_string(n)
    return string.format('%.0f', n)
end

-- Remove all accepted requests at or before the expiry boundary.
redis.call('ZREMRANGEBYSCORE', key, '-inf', integer_string(now - window))
local count = redis.call('ZCARD', key)
if count >= limit then
    local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
    local retry = math.max(1, math.ceil((tonumber(oldest[2]) + window - now) / 1000000))
    return {0, retry}
end

redis.call('ZADD', key, integer_string(now), ARGV[3])
-- TTL reclaims idle keys. Exact expiry is checked above.
redis.call('PEXPIRE', key, tonumber(ARGV[2]) + 1)
return {1, 0}
