# Caching: <name>

## Overview
- what caching pattern this is
- what problem it solves

## Placement
- client
- CDN / edge
- application
- database-adjacent cache tier

## Read path
- how reads interact with the cache

## Write path
- how writes affect cache and source of truth

## Invalidation and freshness
- TTL
- invalidation triggers
- consistency expectations
- stale-read behavior

## Tradeoffs
- latency benefits
- load reduction
- freshness risks
- operational complexity

## Failure modes
- stale data
- cache stampede
- hot keys
- cache penetration
- data loss or inconsistency

## Mitigations
- request coalescing
- prewarming
- backoff or fallback
- hot key protection
- monitoring and alerts

## Use cases
- where this pattern is a good fit
- where it is not

## Related patterns
- cache-aside
- write-through
- write-back
- read-through
