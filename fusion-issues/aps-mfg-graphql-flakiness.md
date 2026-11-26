# APS Manufacturing Data Model GraphQL — Intermittent NOT_FOUND on Valid Hub

| | |
|---|---|
| **Reporter** | Kevin Schneider (FusionDataCLI) |
| **Date observed** | 2026-05-02 |
| **Date filed** | 2026-05-16 |
| **Endpoint** | `POST https://developer.api.autodesk.com/mfg/graphql` |
| **Severity** | High — blocks navigation in any client that paginates `hub(hubId).projects` |
| **Status** | Open, awaiting APS triage |

---

## Summary

The Manufacturing Data Model GraphQL endpoint intermittently returns
`code:NOT_FOUND, errorType:UNKNOWN` for the **same hub URN** that it
successfully serves seconds earlier and seconds later. The same access
token, same hub ID, and same query body produce different results across
back-to-back calls.

Hub URN format: `urn:adsk.ace:prod.scope:<guid>` — the new ACE/scope-style
URNs returned by the `hubs` query.

The failure can occur:

1. On the **first** `GetProjects` call (no cursor, only `hubId`), or
2. On a **subsequent** `GetProjectsNext` call mid-pagination.

In either case, the hub is reachable via the `hubs` list query and is
demonstrably navigable on a different attempt seconds later.

This is not a client-side bug. The behavior reproduces with both a shared
`*http.Client` (HTTP/2, connection pooling) and Go's stock
`http.DefaultClient`, from a single long-lived process and from a
freshly-started one.

---

## Reproduction

### Request

```
POST https://developer.api.autodesk.com/mfg/graphql
Authorization: Bearer <user-access-token, scopes data:read user-profile:read>
Content-Type: application/json
```

### Query (first page, no cursor)

```graphql
query GetProjects($hubId: ID!) {
  hub(hubId: $hubId) {
    projects(pagination: { limit: 50 }) {
      pagination { cursor }
      results {
        id name fusionWebUrl projectStatus projectType
        alternativeIdentifiers { dataManagementAPIProjectId }
      }
    }
  }
}
```

Variables:

```json
{ "hubId": "urn:adsk.ace:prod.scope:08d7f863-23fa-47e7-8a61-b235a3c5d578" }
```

This hub is the user's "Industrial Machine Arts LLC" hub. It is returned
by the `hubs` query with the same URN as its `id` field.

### Successful response (HTTP 200)

```json
{
  "data": {
    "hub": {
      "projects": {
        "pagination": { "cursor": "dXJuOmFkc2sud29ya3NwYWNlOnByb2QucHJvamVjdDphYTBlOWIzYS01MjEyLTRkZmEtYjBmYS05YzdkOGIxMWQ1YWZ-NTA" },
        "results": [ /* 50 project records */ ]
      }
    }
  },
  "extensions": { "pointValue": { "requestedQueryPointValue": 366, "responseQueryPointValue": 0 } }
}
```

### Failure response (also HTTP 200)

```json
{
  "data": { "hub": { "projects": null } },
  "errors": [
    {
      "message": "Requested resource not found. Hub with id urn:adsk.ace:prod.scope:08d7f863-23fa-47e7-8a61-b235a3c5d578not found.",
      "locations": [ { "line": 1, "column": 84 } ],
      "path": [ "hub", "projects" ],
      "extensions": {
        "code": "NOT_FOUND",
        "correlation_id": "c303d828-6602-44f8-86f6-b7daca5d084b",
        "errorType": "UNKNOWN",
        "service": "cw"
      }
    }
  ],
  "extensions": { "pointValue": { "requestedQueryPointValue": 366, "responseQueryPointValue": 0 } }
}
```

Note the missing space in the error string — `b235a3c5d578not found` —
which suggests templated string concatenation upstream (`<id>not found.`)
rather than a parameterised diagnostic.

---

## Reproduction trace

Six back-to-back invocations of `GetProjects` from a single process,
same access token, same hub URN, under two HTTP-client configurations.

### Configuration A — shared `*http.Client` (HTTP/2, keep-alive)

```
RUN 1  FAIL  after=604ms     err=GraphQL errors: Requested resource not found. Hub with id urn:adsk.ace:prod.scope:08d7f863-...not found.
RUN 2  OK    after=16.577s   items=70  (4 pages)
RUN 3  FAIL  after=4.255s    err=GraphQL errors: Requested resource not found. Hub with id urn:adsk.ace:prod.scope:08d7f863-...not found.
```

### Configuration B — Go's stock `http.DefaultClient`

```
RUN 1  OK    after=11.687s   items=70  (4 pages)
RUN 2  FAIL  after=423ms     err=GraphQL errors: Requested resource not found. Hub with id urn:adsk.ace:prod.scope:08d7f863-...not found.
RUN 3  FAIL  after=4.04s     err=GraphQL errors: Requested resource not found. Hub with id urn:adsk.ace:prod.scope:08d7f863-...not found.
```

### Observations

1. Failure is **non-deterministic** — the same hub URN succeeds and fails
   within the same process, seconds apart.
2. Failure timing falls into two clean buckets:
   - `~400–600ms`: failure on **page 1** (no cursor, just `hubId`).
   - `~4s`: failure on **page 3** (after two successful paginated responses).
3. When successful, total time for ~70 projects across 4 pages is
   **11–16 seconds** — roughly 3–5 seconds per paginated call. The endpoint
   appears to be under heavy load at the time of testing.
4. The identical pattern reproduces under both connection-pooling
   configurations, which rules out client-side HTTP/2 or keep-alive
   misbehavior.
5. The hub URN is **unconditionally returned** by the `hubs` query in
   every run — it is part of the user's account.

---

## Affected URN format

All three of the user's hubs use the new scope URN format:

```
urn:adsk.ace:prod.scope:483d1f3d-7c6f-4c81-9046-4fc9e812528b   (Foo1schneik)
urn:adsk.ace:prod.scope:1687600e-001a-4fdd-9e81-2c1159cfb872   (IMA-Alt)
urn:adsk.ace:prod.scope:08d7f863-23fa-47e7-8a61-b235a3c5d578   (Industrial Machine Arts LLC)
```

Each carries a legacy data-management ID under
`alternativeIdentifiers.dataManagementAPIHubId` of the form
`a.<base64-account-name>` (e.g. `a.YnVzaW5lc3M6aW1hbGxj`).

Whether passing the legacy `a.` form as `$hubId` exhibits the same
intermittent NOT_FOUND is not yet known — worth testing on the APS side.

---

## Error metadata

Every observed failure carries identical extension metadata except for
`correlation_id`:

| Field | Value |
|---|---|
| `extensions.code` | `NOT_FOUND` |
| `extensions.errorType` | `UNKNOWN` |
| `extensions.service` | `cw` |
| `extensions.correlation_id` | varies per request |
| HTTP status | `200` (errors carried in body, not status) |

`service: cw` likely identifies the upstream service (Common Workspace?)
that the gateway delegated to. The `errorType: UNKNOWN` suggests the
gateway itself does not understand why the upstream returned 404.

A correlation ID from the trace, in case APS can pull the upstream logs:

```
c303d828-6602-44f8-86f6-b7daca5d084b   (failure on page 3)
```

More correlation IDs are available on request — every failed call has one.

---

## Why this looks server-side

- The same query body, same token, and same hub ID succeed and fail
  within a few seconds, with no state change on the client.
- Failure can occur on the very first call, before any cursor is involved,
  so it is not a cursor-encoding problem.
- HTTP transport configuration does not affect reproduction — both pooled
  HTTP/2 and stock `http.DefaultClient` show the same pattern.
- The error type is literally `UNKNOWN` from the gateway's perspective.
- The 4-second pre-failure latency on page-3 failures matches the average
  latency of successful page-3 responses, which suggests the upstream is
  taking the full request, doing work, and *then* returning NOT_FOUND.

---

## Client-side workaround (FusionDataCLI)

Pending an APS-side fix, FusionDataCLI retries `gqlQuery` on responses
carrying `extensions.errorType: UNKNOWN`, with bounded backoff
(500 ms → 1.5 s, 3 attempts total) inside the existing 30-second
per-call context. Real semantic errors (HTTP 4xx other than the retriable
408/429, GraphQL errors with concrete `errorType` values) are surfaced
immediately without retry.

This makes the symptom disappear in practice, but it should not be
necessary — the gateway should not return NOT_FOUND for a hub it has
just enumerated.

---

## Suggested investigation on the APS side

1. Look up the correlation IDs above in the `cw` service logs — what does
   the upstream actually see for these requests?
2. Confirm whether `urn:adsk.ace:prod.scope:<guid>` hub URNs are handled
   uniformly across all replicas and regions. The flakiness pattern smells
   like one replica behind the LB lacks the hub mapping.
3. Determine whether the response template behind
   `Hub with id <id>not found.` (note the missing space) is the same code
   path for both transient lookup misses and genuine "hub does not exist"
   cases. If so, clients cannot distinguish the two.
4. If an alternate canonical form (e.g. the legacy `a.<base64>`
   `dataManagementAPIHubId`) does not exhibit this flakiness, document it
   so clients can prefer it.

---

## Environment

| | |
|---|---|
| **Client** | FusionDataCLI (Go) |
| **HTTP stacks tested** | `net/http` with shared `*http.Client` (HTTP/2 + keep-alive); `http.DefaultClient` |
| **Auth** | 3-legged OAuth user token, scopes `data:read user-profile:read` |
| **Region** | US (default routing) |
| **Reproduction window** | 2026-05-02, multiple runs over ~30 minutes |

---

## Contact

Kevin Schneider — `claude@schneik.fastmail.com`
FusionDataCLI maintainer. Happy to re-run with additional instrumentation
(extra correlation IDs, alternate URN form, region pinning) on request.
