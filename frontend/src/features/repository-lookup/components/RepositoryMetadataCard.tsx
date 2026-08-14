import type { RepositoryMetadata } from '../../../types/repository'
import { formatBoolean, formatDateTime, formatNumber } from '../../../utils/format'

interface RepositoryMetadataCardProps {
  repository: RepositoryMetadata
}

interface StatItem {
  label: string
  value: string
}

// Convert raw backend fields into display-ready stat rows. Keeping this outside
// JSX makes the component easier to read and easier to change later.
const buildStats = (repository: RepositoryMetadata): StatItem[] => [
  { label: 'Stars', value: formatNumber(repository.stars) },
  { label: 'Forks', value: formatNumber(repository.forks) },
  { label: 'Watchers', value: formatNumber(repository.watchers) },
  { label: 'Open issues', value: formatNumber(repository.open_issues) },
]

// Details are prepared as label/value pairs so the UI can render them with one
// reusable map instead of repeating similar JSX many times.
const buildDetails = (repository: RepositoryMetadata): StatItem[] => [
  { label: 'Owner', value: repository.owner },
  { label: 'Language', value: repository.language ?? 'Not specified' },
  { label: 'License', value: repository.license ?? 'Not specified' },
  { label: 'Default branch', value: repository.default_branch },
  { label: 'Visibility', value: repository.visibility },
  { label: 'Fork', value: formatBoolean(repository.is_fork) },
  { label: 'Archived', value: formatBoolean(repository.archived) },
  { label: 'Created', value: formatDateTime(repository.created_at) },
  { label: 'Last updated', value: formatDateTime(repository.updated_at) },
  { label: 'Last pushed', value: formatDateTime(repository.pushed_at) },
]

export function RepositoryMetadataCard({
  repository,
}: RepositoryMetadataCardProps) {
  const stats = buildStats(repository)
  const details = buildDetails(repository)

  return (
    // Semantic section: this card is one complete block of repository metadata.
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 p-5">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
          <img
            src={repository.owner_avatar_url}
            alt={`${repository.owner} avatar`}
            className="h-14 w-14 rounded-md border border-slate-200 bg-slate-100"
          />
          <div className="min-w-0">
            <p className="text-sm font-medium text-cyan-700">
              {repository.full_name}
            </p>
            <h2 className="mt-1 text-2xl font-semibold text-slate-950">
              {repository.name}
            </h2>
          </div>
        </div>
        <p className="mt-4 max-w-3xl text-sm leading-6 text-slate-600">
          {repository.description || 'No repository description provided.'}
        </p>
        <a
          href={repository.repository_url}
          target="_blank"
          rel="noreferrer"
          className="mt-4 inline-flex text-sm font-medium text-cyan-700 underline-offset-4 hover:underline"
        >
          Open on GitHub
        </a>
      </div>

      <div className="grid grid-cols-2 border-b border-slate-200 sm:grid-cols-4">
        {/* Array.map renders one stat card per item. The key helps React track
            each rendered element efficiently. */}
        {stats.map((stat) => (
          <div key={stat.label} className="border-slate-200 p-5 sm:border-r">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
              {stat.label}
            </p>
            <p className="mt-2 text-2xl font-semibold text-slate-950">
              {stat.value}
            </p>
          </div>
        ))}
      </div>

      <div className="grid gap-4 p-5 lg:grid-cols-[1fr_2fr]">
        <div>
          <h3 className="text-sm font-semibold text-slate-950">Topics</h3>
          {repository.topics.length > 0 ? (
            <div className="mt-3 flex flex-wrap gap-2">
              {/* Topics are dynamic, so they are rendered from the backend array. */}
              {repository.topics.map((topic) => (
                <span
                  key={topic}
                  className="rounded-full bg-cyan-50 px-3 py-1 text-xs font-medium text-cyan-800"
                >
                  {topic}
                </span>
              ))}
            </div>
          ) : (
            <p className="mt-3 text-sm text-slate-500">No topics listed.</p>
          )}
        </div>

        <dl className="grid gap-3 sm:grid-cols-2">
          {/* A definition list is good semantic HTML for label/value metadata. */}
          {details.map((detail) => (
            <div
              key={detail.label}
              className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2"
            >
              <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
                {detail.label}
              </dt>
              <dd className="mt-1 break-words text-sm font-medium text-slate-900">
                {detail.value}
              </dd>
            </div>
          ))}
        </dl>
      </div>
    </section>
  )
}
