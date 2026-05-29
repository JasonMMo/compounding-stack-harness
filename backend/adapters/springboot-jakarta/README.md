# Backend Adapter: springboot-jakarta

Spring Boot 3.2.x (Jakarta EE namespace), Java 17, Gradle Kotlin DSL.
Serves all 8 wire keys defined in `middle/contract/wire-v1.yaml`.

## Wire Key → HTTP Mapping

| Wire key       | Method | Path                                  | Notes                          |
|----------------|--------|---------------------------------------|--------------------------------|
| auth.login     | POST   | /api/auth/login                       | Body: {username, password, remember_me?} |
| auth.logout    | POST   | /api/auth/logout                      | Body: {token}; idempotent      |
| entity.read    | GET    | /api/entities/{entity_type}/{id}      |                                |
| entity.list    | GET    | /api/entities/{entity_type}           | Query: page, size, sort.field, sort.direction, filter fields |
| entity.create  | POST   | /api/entities/{entity_type}           | Body: {data: {...}} or flat map|
| entity.update  | PATCH  | /api/entities/{entity_type}/{id}      | PATCH semantics; absent fields unchanged |
| entity.delete  | DELETE | /api/entities/{entity_type}/{id}      | Idempotent; missing id → success |
| status.health  | GET    | /api/status/health                    |                                |

## How to Run

Requirements: Java 17+, Gradle 8+ (or use `./gradlew`).

```bash
# From this directory
./gradlew bootRun

# Or build a fat jar
./gradlew build
java -jar build/libs/springboot-jakarta-adapter.jar
```

Default port: `8080`. Override with `--server.port=9090`.

## How to Test

```bash
./gradlew test
```

Smoke tests live in `src/test/java/com/compounding/adapter/springboot/EntitySmokeTest.java`.

## Contract Loading (G-1 Compliance)

`build.gradle.kts` copies `middle/contract/` from the repo root into the build classpath
at `resources/contract/` via `processResources`. At startup, `ContractLoader` reads
`contract/wire-v1.yaml` and `contract/error/codes.yaml` from the classpath.

Error code → HTTP status mapping is driven entirely from `codes.yaml` at runtime.
No error codes are hardcoded as Java constants — this satisfies the G-1 single-source principle.

## Persistence

M1: generic in-memory store (`InMemoryEntityStore`). Thread-safe, keyed by
`entity_type → (id → field map)`. UUIDs generated on create. Restart clears all data.

DDL-axis integration (real database) is a later Growth.

## Known Gaps

| Gap | Reason | Future Growth |
|-----|--------|---------------|
| cursor paging returns BAD_REQUEST | Not implemented; offset mode fully works | Growth-N: cursor paging spec |
| No real credential store | Demo user only (username=demo, password=demo) | Growth-N: JWT / OAuth2 |
| Token validation not enforced on entity endpoints | Auth is stub-grade M1 | Growth-N: security filter |
| No DDL-schema validation on create/update | In-memory only, no catalog wired | Growth-N: DDL-axis integration |
| No multi-tenancy | Single in-memory store, not tenant-scoped | M5 gate |

## Auth Demo Credentials

```
username: demo
password: demo
```

POST /api/auth/login → returns token. Token is valid until server restart or logout.
