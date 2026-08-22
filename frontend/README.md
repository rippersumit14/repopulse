# RepoPulse Frontend

React, TypeScript, Vite, and Tailwind CSS frontend for RepoPulse.

## What Is Implemented

The current frontend contains the first repository analysis flow:

1. User enters a public GitHub repository URL.
2. Frontend does a quick browser-side URL check.
3. Frontend calls the FastAPI validation endpoint.
4. If valid, frontend fetches metadata, language composition, and commit activity.
5. The returned data is displayed as a repository analysis dashboard.

No authentication, health scoring, analytics, AI analysis, or fake data is
implemented yet.

## Library Usage

- `react`: Builds the UI with components and state.
- `react-dom`: Mounts the React app into `index.html`.
- `vite`: Runs the frontend dev server and builds production files.
- `typescript`: Adds type checking so request/response shapes are clearer.
- `tailwindcss`: Provides utility classes for styling the UI.
- `@tailwindcss/vite`: Connects Tailwind CSS to Vite.
- `@vitejs/plugin-react`: Lets Vite compile React JSX.
- `oxlint`: Runs fast lint checks for common code issues.

## Local Development

For local development, leave `VITE_API_BASE_URL` empty so Vite proxies `/api`
requests to the FastAPI backend and avoids browser CORS issues:

```bash
VITE_API_BASE_URL=
```

Set `VITE_API_BASE_URL` only when the deployed frontend needs to call a
separate backend origin that has CORS enabled.

Run the frontend:

```bash
npm install
npm run dev
```

## Scripts

- `npm run dev`: start Vite locally.
- `npm run build`: run TypeScript checks and build production assets.
- `npm run lint`: run Oxlint.

## File Guide

- `src/main.tsx`: React entry point. It renders the app into the browser.
- `src/App.tsx`: Top-level app component. It currently renders the lookup page.
- `src/index.css`: Global CSS and Tailwind import.
- `src/api/config.ts`: Central place for API base URL configuration.
- `src/api/repositories.ts`: API functions that call the FastAPI backend.
- `src/api/errors.ts`: Converts backend/network errors into friendly messages.
- `src/types/repository.ts`: TypeScript types matching backend repository JSON.
- `src/utils/format.ts`: Small helpers for formatting numbers, dates, bytes, percentages, and booleans.
- `src/features/repository-lookup/RepositoryLookupPage.tsx`: Main page logic.
- `src/features/repository-lookup/components/RepositoryLookupForm.tsx`: URL input form.
- `src/features/repository-analysis/RepositoryAnalysisDashboard.tsx`: Dashboard container for successful analysis results.
- `src/features/repository-analysis/components/RepositoryHeader.tsx`: Repository identity, description, badges, topics, and GitHub link.
- `src/features/repository-analysis/components/RepositoryStatsGrid.tsx`: Compact stars/forks/watchers/issues cards.
- `src/features/repository-analysis/components/LanguageAnalysisSection.tsx`: Language composition bar and exact language list.
- `src/features/repository-analysis/components/CommitActivitySection.tsx`: Recent commit activity summary from backend aggregate fields.
- `src/features/repository-analysis/components/RepositoryInfoSection.tsx`: Secondary repository facts and timestamps.

## Backend Endpoints Used

```http
POST /api/v1/repositories/validate
POST /api/v1/repositories/metadata
POST /api/v1/repositories/languages
POST /api/v1/repositories/activity
```

React components do not call `fetch()` directly. Components call functions from
`src/api/repositories.ts`, and that file handles communication with FastAPI.

If metadata succeeds but language or activity analysis fails, the dashboard still
shows the successful metadata and clearly marks the failed section.
