# Dashboard Web

`dashboard-web/` is the read-only React dashboard for the open-source `private-os` repository.
It presents the local backend as an editorial interface for:

- dashboard snapshots
- operations
- entity detail views across tasks, approvals, follow-ups, panels, and logs

The frontend is built with React, TypeScript, Vite, Tailwind, and Zustand.

## Prerequisites

- Node.js 22 or newer
- npm
- the local backend available from the repository root

By default, the Vite dev server proxies `/api` requests to `http://127.0.0.1:8765`.

## Development

Install dependencies:

```bash
npm install
```

Start the dev server:

```bash
npm run dev
```

## Commands

- `npm run dev`: start the Vite dev server
- `npm run lint`: run ESLint
- `npm run check`: run TypeScript type-checking
- `npm run build`: create a production build
- `npm run test`: run the Vitest suite
- `npm run preview`: serve the production build locally

## Backend Integration

The frontend expects the Python backend from the repository root to expose the local API.

Typical flow:

1. Start the backend from the repository root.
2. Start the frontend from `dashboard-web/`.
3. Open the Vite URL and let `/api` requests flow through the local proxy.

For production packaging, the backend can serve the built frontend bundle directly.

## Project Structure

- `src/App.tsx`: application shell and route composition
- `src/pages/`: top-level route screens
- `src/components/`: reusable UI building blocks
- `src/store/`: Zustand state and refresh actions
- `src/hooks/`: cross-cutting client hooks such as realtime updates
- `src/utils/`: API helpers and utility functions
- `src/test/`: frontend test setup

## Testing

The current automated coverage is intentionally minimal and focused on smoke testing.

The first frontend test verifies that the main routes render without crashing:

- `/`
- `/operations`

This is a baseline safety net, not full UI coverage.
