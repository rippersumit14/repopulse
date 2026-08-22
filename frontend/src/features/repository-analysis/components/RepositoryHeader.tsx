import type { RepositoryMetadata } from '../../../types/repository'
import { formatDateTime } from '../../../utils/format'

interface RepositoryHeaderProps {
  repository: RepositoryMetadata
}

export function RepositoryHeader({ repository }: RepositoryHeaderProps) {
  const [ownerName, repositoryName] = repository.full_name.split('/')

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex min-w-0 flex-col gap-4 sm:flex-row">
          <img
            src={repository.owner_avatar_url}
            alt={`${repository.owner} avatar`}
            className="h-16 w-16 rounded-lg border border-slate-200 bg-slate-100"
          />

          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="break-words text-2xl font-semibold tracking-tight text-slate-950">
                <span className="text-slate-500">{ownerName}</span>
                <span className="px-1 text-slate-400">/</span>
                {repositoryName ?? repository.name}
              </h2>
              <span className="rounded-full border border-slate-200 px-2.5 py-1 text-xs font-medium capitalize text-slate-600">
                {repository.visibility}
              </span>
            </div>

            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              {repository.description || 'No repository description provided.'}
            </p>

            <div className="mt-4 flex flex-wrap gap-2">
              {repository.language ? (
                <span className="rounded-full bg-cyan-50 px-3 py-1 text-xs font-medium text-cyan-800">
                  {repository.language}
                </span>
              ) : null}
              {repository.license ? (
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                  {repository.license}
                </span>
              ) : null}
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                {repository.default_branch}
              </span>
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-3 text-sm lg:items-end">
          <a
            href={repository.repository_url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex w-fit rounded-md border border-slate-300 px-3 py-2 font-medium text-slate-800 transition hover:border-slate-400 hover:bg-slate-50"
          >
            Open on GitHub
          </a>
          <p className="text-slate-500">
            Last pushed {formatDateTime(repository.pushed_at)}
          </p>
        </div>
      </div>

      {repository.topics.length > 0 ? (
        <div className="mt-5 flex flex-wrap gap-2 border-t border-slate-200 pt-4">
          {repository.topics.map((topic) => (
            <span
              key={topic}
              className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700"
            >
              {topic}
            </span>
          ))}
        </div>
      ) : null}
    </section>
  )
}
