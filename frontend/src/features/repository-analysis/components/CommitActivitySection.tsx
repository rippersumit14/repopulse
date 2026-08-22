import type { RepositoryCommitActivityResponse } from '../../../types/repository'
import { formatDateTime, formatNumber } from '../../../utils/format'

interface CommitActivitySectionProps {
  activity: RepositoryCommitActivityResponse | null
  error: string | null
}

const activityTone = (level: string): string => {
  if (level === 'high') {
    return 'bg-emerald-50 text-emerald-700 ring-emerald-200'
  }

  if (level === 'medium') {
    return 'bg-amber-50 text-amber-700 ring-amber-200'
  }

  return 'bg-slate-100 text-slate-700 ring-slate-200'
}

export function CommitActivitySection({
  activity,
  error,
}: CommitActivitySectionProps) {
  const sevenDayShare =
    activity && activity.commits_last_30_days > 0
      ? (activity.commits_last_7_days / activity.commits_last_30_days) * 100
      : 0

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-950">
            Commit activity
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            Recent activity based on the backend&apos;s 30-day commit window.
          </p>
        </div>
        {activity ? (
          <span
            className={`w-fit rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wide ring-1 ${activityTone(
              activity.activity_level,
            )}`}
          >
            {activity.activity_level}
          </span>
        ) : null}
      </div>

      {error ? (
        <p className="mt-4 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
          {error}
        </p>
      ) : null}

      {!error && activity ? (
        <div className="mt-5">
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-md bg-slate-50 p-4">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Recent commits
              </p>
              <p className="mt-2 text-2xl font-semibold text-slate-950">
                {formatNumber(activity.total_recent_commits)}
              </p>
            </div>
            <div className="rounded-md bg-slate-50 p-4">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Last 30 days
              </p>
              <p className="mt-2 text-2xl font-semibold text-slate-950">
                {formatNumber(activity.commits_last_30_days)}
              </p>
            </div>
            <div className="rounded-md bg-slate-50 p-4">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Last 7 days
              </p>
              <p className="mt-2 text-2xl font-semibold text-slate-950">
                {formatNumber(activity.commits_last_7_days)}
              </p>
            </div>
          </div>

          <div className="mt-5">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium text-slate-700">
                Last 7 days compared with 30-day activity
              </span>
              <span className="text-slate-500">
                {activity.commits_last_7_days}/{activity.commits_last_30_days}
              </span>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-cyan-500"
                style={{ width: `${Math.min(sevenDayShare, 100)}%` }}
              />
            </div>
          </div>

          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            <div className="rounded-md border border-slate-200 px-3 py-2">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Last commit
              </p>
              <p className="mt-1 text-sm font-medium text-slate-900">
                {activity.last_commit_at
                  ? formatDateTime(activity.last_commit_at)
                  : 'No recent commit found'}
              </p>
            </div>
            <div className="rounded-md border border-slate-200 px-3 py-2">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Days since last commit
              </p>
              <p className="mt-1 text-sm font-medium text-slate-900">
                {activity.days_since_last_commit ?? 'Unknown'}
              </p>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  )
}
