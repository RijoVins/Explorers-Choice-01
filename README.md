This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Development setup (team)

The app is a Next.js frontend + a FastAPI backend on a shared database. The
backend supports two database providers, selected with one server-side
setting: `DATABASE_PROVIDER=mysql` (MySQL 8 / MariaDB / TiDB) or
`DATABASE_PROVIDER=supabase` (Supabase-hosted PostgreSQL).

**See [DATABASE_PROVIDERS.md](DATABASE_PROVIDERS.md)** for provider selection,
TLS requirements, verification commands, and what to do before switching back
to Supabase.

**Backend** (from the repo root, once):

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment, then install the backend dependencies:

```bash
# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
python -m pip install -r requirements.txt
cp .env.example .env            # set DATABASE_PROVIDER, then the matching credentials
```

For the PostgreSQL provider, apply the schema:

```bash
# only when DATABASE_PROVIDER=supabase
python -m alembic upgrade head
```

```bash
# only when DATABASE_PROVIDER=mysql
cd backend && python -m alembic -c alembic_mysql.ini upgrade head
```

The two providers use separate Alembic environments and each refuses to run
against the other backend. Migrations are **never** applied automatically at
startup: the backend only performs a read-only connectivity check, so apply
them explicitly as above.

All developers must use the same shared database. Do not use `localhost` or
`127.0.0.1` as the database host unless that address is a shared database
service reachable by the whole team. The `.env` file is ignored by Git; share
variable names and approved connection details through your team's
secret-sharing process, never through the repository.

To check a MySQL connection read-only before starting the app:

```bash
backend/.venv/bin/python backend/scripts/db_check.py
```

Run the backend tests with:

```bash
cd backend && ./.venv/bin/python -m pytest tests/ -q
```

Then start both servers:

```bash
npm run dev                                      # frontend → http://localhost:3000
npm run server:dev                               # backend  → http://localhost:8000
```

- The frontend calls the API at `http://localhost:8000/api` by default. If your API runs elsewhere, set `NEXT_PUBLIC_EXPLORERS_API_URL`.
- CORS is open (`["*"]`) for local development because each developer's `next dev` may pick a different port (3000, 3001, 3100…). If login fails with **"Failed to fetch"**, you are almost certainly hitting CORS — the backend must see your frontend origin. Point the backend at your real API host, or verify the origin in the browser's Network tab.
- Use `http://localhost:3000`, not `http://127.0.0.1:3000`, so the session cookie is treated as same-site.

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
