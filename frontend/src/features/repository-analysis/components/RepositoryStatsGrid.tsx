import type { RepositoryMetadata } from '../../../types/repository'
import { formatNumber } from '../../../utils/format'

interface RepositoryStatsGridProps {
  repository: RepositoryMetadata
}

const statItems = (repository: RepositoryMetadata) => [
  { label: 'Stars', value: formatNumber(repository.stars) },
  { label: 'Forks', value: formatNumber(repository.forks) },
  { label: 'Watchers', value: formatNumber(repository.watchers) },
  { label: 'Open issues', value: formatNumber(repository.open_issues) },
]

export function RepositoryStatsGrid({ repository }: RepositoryStatsGridProps) {
  return (
    <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {statItems(repository).map((stat) => (
        <div
          key={stat.label}
          className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
        >
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
            {stat.label}
          </p>
          <p className="mt-2 text-2xl font-semibold text-slate-950">
            {stat.value}
          </p>
        </div>
      ))}
    </section>
  )
}
