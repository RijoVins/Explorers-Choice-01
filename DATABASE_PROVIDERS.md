# Database providers (MySQL / Supabase)

The backend talks to exactly one database at a time, chosen by a single
server-side setting. This document explains how to select a provider, what
each one does, and what you must do before switching back.

The active MySQL schema is **`explorers_choice_app`**, created with the 19
tables the ORM expects. It is populated only by your own data — no records
were copied and no administrator account was created. The older
`Explorers_Choice_db` schema is a separate, unrelated database that this
application no longer uses and has not been modified.

---

## Selecting a provider

Set `DATABASE_PROVIDER` in the backend's local, git-ignored `backend/.env`
(or in your host's environment settings) and restart the backend.

```bash
# MySQL / TiDB Cloud — the active provider
DATABASE_PROVIDER=mysql

# Supabase-hosted PostgreSQL — the retained, inactive provider
DATABASE_PROVIDER=supabase
```

Only `mysql` and `supabase` are accepted. Anything else fails at startup
rather than guessing.

### There is no fallback, by design

If the selected database is unreachable, the backend **refuses to start**
(`SystemExit`) and the API returns `503` for in-flight requests. It never
retries against the other provider.

This matters: a silent fallback would let reads succeed from one database
while writes landed in another, and nobody would notice until the data
disagreed. Failing loudly is the only safe behaviour.

---

## MySQL provider

### Configuration

Discrete variables, so a password containing `@ : / ? # &` cannot corrupt the
URL (each component is percent-encoded when the connection URL is built):

```bash
DATABASE_PROVIDER=mysql
MYSQL_HOST=<host>
MYSQL_PORT=3306            # TiDB Cloud serverless uses 4000
MYSQL_DATABASE=<database>
MYSQL_USER=<username>
MYSQL_PASSWORD=<password>
MYSQL_SSL_MODE=verify-full
MYSQL_SSL_CA=/abs/path/to/ca-certificate.pem

MYSQL_POOL_SIZE=10
MYSQL_MAX_OVERFLOW=20
MYSQL_POOL_RECYCLE=1800
```

Or set `MYSQL_URL` instead of those four. The URL form takes precedence.

### TLS is mandatory

`MYSQL_SSL_MODE` accepts only `verify-ca` or `verify-full`. Unverified TLS is
rejected by configuration validation — you cannot accidentally ship a
connection that encrypts without proving the server's identity.

- `verify-full` — **the default.** Verifies the server certificate against
  `MYSQL_SSL_CA` *and* checks the hostname. Omitting the variable still gets
  you hostname verification.
- `verify-ca` — verifies the certificate chain but not the hostname.

#### Which CA certificate to use (TiDB Cloud)

**TiDB Cloud publishes no downloadable CA certificate of its own.** PingCAP
states the issuer is Let's Encrypt and that the CA may change in future, so
they deliberately do not ship one. The documented approach is to trust the
**system root CA store**, and, per their guidance, to use a full CA *bundle*
rather than a single root so a future CA change does not break you.

That is what `backend/certs/tidb-cloud-ca.pem` contains here: a copy of the
host's `/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem` (121 roots,
including ISRG Root X1). It is git-ignored. Re-copy the system bundle if you
move to another machine:

```bash
cp /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem \
   backend/certs/tidb-cloud-ca.pem     # Fedora/RHEL
# Debian/Ubuntu: /etc/ssl/certs/ca-certificates.crt
# macOS:         /etc/ssl/cert.pem
```

Verified for `gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000`: the
server certificate chains to this bundle and the hostname matches, so both
`verify-ca` and `verify-full` complete the TLS handshake.

If hostname verification ever fails against a rotated certificate, drop to
`MYSQL_SSL_MODE=verify-ca`. That still verifies the certificate chain — it is
never "no verification".

### Connection pooling

A SQLAlchemy `QueuePool` is used, with `pool_pre_ping` (drops stale
connections before handing them out) and `pool_recycle` so connections are
recycled before the server or a proxy times them out. Tune
`MYSQL_POOL_SIZE` / `MYSQL_MAX_OVERFLOW` down if your host caps concurrent
connections.

### Migrations never run automatically

When `DATABASE_PROVIDER=mysql`:

- `alembic upgrade head` is **skipped** at startup (`backend/app/main.py`).
- The PostgreSQL `backend/app/migrations/env.py` raises `RuntimeError` if
  Alembic is invoked against MySQL.
- MySQL has its own environment, `backend/app/migrations_mysql/env.py`, which
  raises `RuntimeError` unless `DATABASE_PROVIDER=mysql`. Neither environment
  can touch the other backend.
- Startup runs a read-only `SELECT 1` connectivity check instead
  (`check_database_connectivity`).

Apply MySQL migrations explicitly, never on boot:

```bash
cd backend
python -m alembic -c alembic_mysql.ini upgrade head
```

`backend/alembic_mysql.ini` leaves `sqlalchemy.url` empty on purpose — the
environment takes the URL from the resolved provider, so a migration can never
land in a different database than the application. Preview the SQL first with
`--sql`.

`0001_mysql_initial` creates all 19 ORM tables. It is generated from
`app/models.py`, so the schema matches what the application actually queries.
Deliberate PostgreSQL → MySQL differences:

| PostgreSQL | MySQL | Why |
| --- | --- | --- |
| `JSONB` / `JSON` | `my.JSON()` | TiDB has no `JSONB` |
| `timestamptz` | `my.DATETIME(fsp=6)`, naive UTC | re-attached as UTC on read by `app.db.types.UTCDateTime` |
| `TEXT` | `my.LONGTEXT()` | MySQL `TEXT` caps at 64 KiB and errors |
| `boolean` | `my.BOOLEAN` (`TINYINT(1)`), `0`/`1` defaults | native boolean |
| string defaults | quoted literals (`DEFAULT ''`, `DEFAULT 'CUSTOMER'`) | |
| timestamps | `DEFAULT CURRENT_TIMESTAMP(6)` | |
| `TEXT` / `JSON` defaults | **no server default** | TiDB rejects `DEFAULT` on `BLOB`/`TEXT`/`JSON` columns; the ORM supplies these in Python (`default=""` / `default=list`) |

Because MySQL DDL is non-transactional, a failed migration leaves partial
tables behind. Drop them in the target schema and re-run; never re-run against
a schema that holds data.

### Verifying the connection

Read-only. Issues only `SELECT` / `SHOW` / `DESCRIBE`, plus `information_schema`
reads. It cannot modify data.

```bash
backend/.venv/bin/python backend/scripts/db_check.py
```

It reports the server version, every table with its real columns / foreign
keys / unique constraints / indexes, read-only row counts, and a diff of the
live schema against `backend/app/models.py` (missing or extra tables and
columns).

---

## Supabase provider (retained, inactive)

Nothing about Supabase was removed. To reactivate it:

```bash
DATABASE_PROVIDER=supabase
DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:5432/<db>
```

Then restart. Alembic runs at startup exactly as it always did, and the
psycopg driver is still in `requirements.txt`.

Do not pause or delete the hosted Supabase project. Nothing in this codebase
uses Supabase Auth, Storage, Realtime, Edge Functions or RLS — see below.

---

## ⚠️ Switching back to Supabase requires manual reconciliation

**MySQL changes are not synced to Supabase, in either direction.**

There is no dual write, no replication and no failover between the two
databases. If you make changes while MySQL is active, the Supabase database
still holds whatever it held when you switched away.

Before switching back to `supabase`, you must bring Supabase's schema **and**
data up to date yourself:

1. Apply any schema changes made to MySQL to the Supabase database.
2. Reconcile the data. Nothing does this for you, and there is no conflict
   detection. Decide which side wins, per table, deliberately.
3. Re-run `alembic upgrade head` against Supabase so its `alembic_version`
   matches the migration history.

If you switch back without doing this, the application will read stale data —
or fail — with no warning.

---

## Supabase features in use

Verified by searching the whole repository:

| Feature | In use? | Notes |
|---|---|---|
| Supabase Auth | No | The app has its own auth: bcrypt + `python-jose` JWT sessions (`backend/app/security.py`), plus Google OAuth. |
| Supabase Storage | No | No bucket references, no signed-URL handling. |
| Realtime | No | No channels, no subscriptions. The frontend fetches over HTTP. |
| Edge Functions | No | None. |
| RLS policies | No | Access control is enforced in the backend, not in the database. |
| Database triggers | No | Not defined in the repository. |
| Background jobs | No | No scheduler, cron or worker in the backend. |

### The RLS question

Because there are no RLS policies, there is nothing to reimplement. The
equivalent protections already exist and are **provider-independent** — they
live in the FastAPI dependency layer and in the ORM query layer, not in the
database:

- `security.get_current_user` / `optional_current_user` — JWT session
  validation, including `token_version` checks so a password change or reset
  invalidates existing sessions.
- `security.require_admin`, `require_roles`, `require_hotel_owner` —
  authorization.
- Ownership scoping in queries: bookings filtered by `user_id`
  (`crud.py:396`, `crud.py:934`), hotels by `owner_id` (`crud.py:985`),
  cab/train bookings by the session user (`routes/cabs.py:160`,
  `routes/trains.py:251`).
- CSRF origin checks for cookie-authenticated writes
  (`main.py::csrf_protection_middleware`).

These keep working unchanged on MySQL because they never depended on the
database enforcing anything.

---

## How the code is organised

```
backend/app/db/
  __init__.py      Resolves the provider once; owns `engine`, `SessionLocal`, `get_db`
  base.py          Declarative `Base`
  providers.py     MySQLProvider | SupabaseProvider + get_provider()
  types.py         Dialect-neutral column types
backend/app/database.py   Thin re-export shim (imports still work)
```

`get_provider(settings)` returns exactly one provider based on
`DATABASE_PROVIDER`. Each provider owns its connection URL, engine options
(pool sizing, `pool_pre_ping`, `pool_recycle`, timeouts), whether startup may
run migrations, and how connectivity is checked.

Route handlers and `crud.py` contain no provider-specific code. They call
`get_db()` and get a session on the selected database. Switching providers is
a configuration change, not a code change.

All queries go through the SQLAlchemy ORM, so statements are parameterised.
`IntegrityError` becomes `409`; `OperationalError` and other `DBAPIError`s
become `503` with the provider name and no internal detail leaked.

### Dialect-neutral types (`backend/app/db/types.py`)

Two MySQL/PostgreSQL differences are handled in shared column types so the
models, the JSON response format and the UI behave identically on both:

- **`UTCDateTime`** — PostgreSQL `TIMESTAMP WITH TIME ZONE` stores the instant
  directly. MySQL `DATETIME` has no offset, so values are normalised to naive
  UTC on write and re-attached as `timezone.utc` on read. The API therefore
  emits the same timezone-aware JSON on both providers.
- **`LongText`** — MySQL `TEXT` is capped at 64 KiB and *errors* rather than
  truncating, so long itineraries, stories or internal notes would fail
  mid-write. This maps to `LONGTEXT` on MySQL and plain `TEXT` on PostgreSQL.

### Behaviour preserved on both providers

Filtering, sorting, pagination, relationships, validation, transactions and
response formats are unchanged, because they are expressed through the ORM
rather than in dialect-specific SQL. The repository contains no `ILIKE`,
`ON CONFLICT` or raw PostgreSQL-only SQL in request paths.

---

## Tests

```bash
cd backend && ./.venv/bin/python -m pytest tests/ -q
```

`backend/tests/test_provider_selection.py` runs entirely offline (the engine
is lazy and nothing connects). It covers provider selection and validation,
TLS enforcement, password encoding, migration gating, the absence of
fallback, and that the shared models compile to valid DDL for both MySQL and
PostgreSQL.
