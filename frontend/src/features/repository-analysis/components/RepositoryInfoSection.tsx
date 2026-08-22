import type { RepositoryMetadata } from '../../../types/repository'
import { formatBoolean, formatDateTime } from '../../../utils/format'

interface RepositoryInfoSectionProps {
  repository: RepositoryMetadata
}

const buildInfo = (repository: RepositoryMetadata) => [
  { label: 'Created', value: formatDateTime(repository.created_at) },
  { label: 'Last updated', value: formatDateTime(repository.updated_at) },
  { label: 'Last pushed', value: formatDateTime(repository.pushed_at) },
  { label: 'Default branch', value: repository.default_branch },
  { label: 'License', value: repository.license ?? 'Not specified' },
  { label: 'Visibility', value: repository.visibility },
  { label: 'Fork', value: formatBoolean(repository.is_fork) },
  { label: 'Archived', value: formatBoolean(repository.archived) },
]

export function RepositoryInfoSection({ repository }: RepositoryInfoSectionProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-950">
        Repository information
      </h2>
      <dl className="mt-4 grid gap-3 sm:grid-cols-2">
        {buildInfo(repository).map((item) => (
          <div
            key={item.label}
            className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2"
          >
            <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
              {item.label}
            </dt>
            <dd className="mt-1 break-words text-sm font-medium text-slate-900">
              {item.value}
            </dd>
          </div>
        ))}
      </dl>
    </section>
  )
}
