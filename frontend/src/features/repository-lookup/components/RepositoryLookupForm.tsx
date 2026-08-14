// Props are inputs passed from a parent component. This form does not own the
// lookup state; it receives values and callbacks from RepositoryLookupPage.
interface RepositoryLookupFormProps {
  repositoryUrl: string
  error: string | null
  isLoading: boolean
  onRepositoryUrlChange: (repositoryUrl: string) => void
  onSubmit: () => void
}

export function RepositoryLookupForm({
  repositoryUrl,
  error,
  isLoading,
  onRepositoryUrlChange,
  onSubmit,
}: RepositoryLookupFormProps) {
  return (
    <form
      className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
      onSubmit={(event) => {
        // Prevent the browser's default full-page form refresh. React handles
        // the submit with JavaScript instead.
        event.preventDefault()
        onSubmit()
      }}
    >
      <label
        htmlFor="repository-url"
        className="block text-sm font-medium text-slate-900"
      >
        GitHub repository URL
      </label>
      <div className="mt-3 flex flex-col gap-3 sm:flex-row">
        <input
          id="repository-url"
          name="repository-url"
          type="url"
          // Controlled input: React state is the source of truth for this value.
          value={repositoryUrl}
          placeholder="https://github.com/fastapi/fastapi"
          disabled={isLoading}
          // Connects the input to the error message for screen readers.
          aria-describedby={error ? 'repository-url-error' : undefined}
          className="min-h-11 flex-1 rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-cyan-600 focus:ring-2 focus:ring-cyan-100 disabled:cursor-not-allowed disabled:bg-slate-100"
          onChange={(event) => onRepositoryUrlChange(event.target.value)}
        />
        <button
          type="submit"
          disabled={isLoading}
          className="min-h-11 rounded-md bg-slate-950 px-5 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-cyan-300 focus:ring-offset-2 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {/* The button text reflects the async request state. */}
          {isLoading ? 'Looking up...' : 'Analyze repository'}
        </button>
      </div>
      {error ? (
        <p id="repository-url-error" className="mt-3 text-sm text-red-700">
          {error}
        </p>
      ) : null}
    </form>
  )
}
