import { useState } from 'react'
import { ApiError, toUserMessage } from '../../api/errors'
import {
  fetchRepositoryActivity,
  fetchRepositoryLanguages,
  fetchRepositoryMetadata,
  validateRepositoryUrl,
} from '../../api/repositories'
import {
  RepositoryAnalysisDashboard,
  type RepositoryAnalysisResult,
} from '../repository-analysis/RepositoryAnalysisDashboard'
import { RepositoryLookupForm } from './components/RepositoryLookupForm'

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
  const [analysis, setAnalysis] = useState<RepositoryAnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [loadingStep, setLoadingStep] = useState('')

  // This function owns the full submit flow for the page:
  // validate locally, validate with backend, then fetch metadata.
  const handleSubmit = async () => {
    const trimmedUrl = repositoryUrl.trim()

    // Clear old UI state so the next result starts from a clean screen.
    setError(null)
    setAnalysis(null)
    setLoadingStep('')

    if (!isGitHubRepositoryUrl(trimmedUrl)) {
      setError(
        'Enter a valid GitHub repository URL, such as https://github.com/fastapi/fastapi.',
      )
      return
    }

    setIsLoading(true)

    try {
      setLoadingStep('Validating repository URL...')

      // First backend call: check that the URL matches the backend contract.
      const validation = await validateRepositoryUrl(trimmedUrl)

      if (!validation.valid) {
        throw new ApiError(
          'That URL does not look like a valid public GitHub repository.',
          'invalid_repository_url',
        )
      }

      setLoadingStep('Fetching metadata, languages, and commit activity...')

      // These calls are independent after validation, so they can run together.
      // Promise.allSettled lets us keep successful sections even if one analysis
      // endpoint fails.
      const [metadataResult, languagesResult, activityResult] =
        await Promise.allSettled([
          fetchRepositoryMetadata(validation.repository_url),
          fetchRepositoryLanguages(validation.repository_url),
          fetchRepositoryActivity(validation.repository_url),
        ])

      if (metadataResult.status === 'rejected') {
        throw metadataResult.reason
      }

      setAnalysis({
        repository: metadataResult.value,
        languages:
          languagesResult.status === 'fulfilled' ? languagesResult.value : null,
        activity:
          activityResult.status === 'fulfilled' ? activityResult.value : null,
        errors: {
          languages:
            languagesResult.status === 'rejected'
              ? toUserMessage(languagesResult.reason)
              : null,
          activity:
            activityResult.status === 'rejected'
              ? toUserMessage(activityResult.reason)
              : null,
        },
      })
    } catch (caughtError) {
      // Convert technical errors into a message a user can understand.
      setError(toUserMessage(caughtError))
    } finally {
      // finally always runs, whether the request succeeds or fails.
      setIsLoading(false)
      setLoadingStep('')
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
            Repository analysis dashboard
          </h1>
          <p className="mt-3 text-base leading-7 text-slate-600">
            Enter a public GitHub repository URL to validate it, fetch metadata,
            analyze language composition, and summarize recent commit activity.
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
            <p className="text-sm font-medium text-cyan-700">
              {loadingStep || 'Analyzing repository...'}
            </p>
            <div className="mt-4 h-4 w-52 animate-pulse rounded bg-slate-200" />
            <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {['stars', 'forks', 'watchers', 'issues'].map((item) => (
                <div key={item} className="rounded-md bg-slate-100 p-4">
                  <div className="h-3 w-16 animate-pulse rounded bg-slate-200" />
                  <div className="mt-3 h-6 w-20 animate-pulse rounded bg-slate-200" />
                </div>
              ))}
            </div>
          </section>
        ) : null}

        {/* Success state: show the analysis dashboard after metadata loads. */}
        {!isLoading && analysis ? (
          <RepositoryAnalysisDashboard analysis={analysis} />
        ) : null}

        {/* Empty state: shown before the first successful repository lookup. */}
        {!isLoading && !analysis ? (
          <section className="rounded-lg border border-dashed border-slate-300 bg-white/70 p-8 text-center">
            <h2 className="text-lg font-semibold text-slate-950">
              No repository loaded yet
            </h2>
            <p className="mt-2 text-sm text-slate-600">
              Repository analysis will appear here after a successful lookup.
            </p>
          </section>
        ) : null}
      </div>
    </main>
  )
}
