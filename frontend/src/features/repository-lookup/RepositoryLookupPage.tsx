import { useState } from 'react'
import { ApiError, toUserMessage } from '../../api/errors'
import {
  fetchRepositoryMetadata,
  validateRepositoryUrl,
} from '../../api/repositories'
import type { RepositoryMetadata } from '../../types/repository'
import { RepositoryLookupForm } from './components/RepositoryLookupForm'
import { RepositoryMetadataCard } from './components/RepositoryMetadataCard'

// This quick client-side check gives instant feedback before calling the
// backend. The backend is still the source of truth for final validation.
const isGitHubRepositoryUrl = (value: string): boolean => {
  try {
    const url = new URL(value)
    const pathParts = url.pathname.split('/').filter(Boolean)

    return url.hostname === 'github.com' && pathParts.length >= 2
  } catch {
    return false
  }
}

export function RepositoryLookupPage() {
  // React state stores the current screen data. Updating state causes React to
  // re-render the component with the latest values.
  const [repositoryUrl, setRepositoryUrl] = useState('')
  const [repository, setRepository] = useState<RepositoryMetadata | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  // This function owns the full submit flow for the page:
  // validate locally, validate with backend, then fetch metadata.
  const handleSubmit = async () => {
    const trimmedUrl = repositoryUrl.trim()

    // Clear old UI state so the next result starts from a clean screen.
    setError(null)
    setRepository(null)

    if (!isGitHubRepositoryUrl(trimmedUrl)) {
      setError(
        'Enter a valid GitHub repository URL, such as https://github.com/fastapi/fastapi.',
      )
      return
    }

    setIsLoading(true)

    try {
      // First backend call: check that the URL matches the backend contract.
      const validation = await validateRepositoryUrl(trimmedUrl)

      if (!validation.valid) {
        throw new ApiError(
          'That URL does not look like a valid public GitHub repository.',
          'invalid_repository_url',
        )
      }

      // Second backend call: fetch the real repository metadata only after the
      // validation endpoint says the URL is valid.
      const metadata = await fetchRepositoryMetadata(validation.repository_url)
      setRepository(metadata)
    } catch (caughtError) {
      // Convert technical errors into a message a user can understand.
      setError(toUserMessage(caughtError))
    } finally {
      // finally always runs, whether the request succeeds or fails.
      setIsLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-slate-100 text-slate-900">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-8 sm:px-6 lg:px-8">
        <header className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-wide text-cyan-700">
            RepoPulse
          </p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">
            GitHub repository lookup
          </h1>
          <p className="mt-3 text-base leading-7 text-slate-600">
            Enter a public GitHub repository URL to validate it and fetch the
            repository metadata available from the RepoPulse backend.
          </p>
        </header>

        <RepositoryLookupForm
          repositoryUrl={repositoryUrl}
          error={error}
          isLoading={isLoading}
          // Passing setters/callbacks down keeps this page in control of state,
          // while the form stays focused only on rendering form UI.
          onRepositoryUrlChange={setRepositoryUrl}
          onSubmit={handleSubmit}
        />

        {/* Skeleton loading UI gives feedback while the backend request runs. */}
        {isLoading ? (
          <section
            aria-live="polite"
            className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
          >
            <div className="h-4 w-40 animate-pulse rounded bg-slate-200" />
            <div className="mt-5 grid gap-4 sm:grid-cols-4">
              {['stars', 'forks', 'watchers', 'issues'].map((item) => (
                <div key={item} className="rounded-md bg-slate-100 p-4">
                  <div className="h-3 w-16 animate-pulse rounded bg-slate-200" />
                  <div className="mt-3 h-6 w-20 animate-pulse rounded bg-slate-200" />
                </div>
              ))}
            </div>
          </section>
        ) : null}

        {/* Success state: show structured metadata after a successful lookup. */}
        {!isLoading && repository ? (
          <RepositoryMetadataCard repository={repository} />
        ) : null}

        {/* Empty state: shown before the first successful repository lookup. */}
        {!isLoading && !repository ? (
          <section className="rounded-lg border border-dashed border-slate-300 bg-white/70 p-8 text-center">
            <h2 className="text-lg font-semibold text-slate-950">
              No repository loaded yet
            </h2>
            <p className="mt-2 text-sm text-slate-600">
              Metadata will appear here after a successful lookup.
            </p>
          </section>
        ) : null}
      </div>
    </main>
  )
}
