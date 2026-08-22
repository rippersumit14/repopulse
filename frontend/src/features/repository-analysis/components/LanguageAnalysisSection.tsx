import type { RepositoryLanguagesResponse } from '../../../types/repository'
import { formatBytes, formatPercent } from '../../../utils/format'

interface LanguageAnalysisSectionProps {
  languages: RepositoryLanguagesResponse | null
  error: string | null
}

const languageColors = [
  'bg-cyan-500',
  'bg-emerald-500',
  'bg-amber-500',
  'bg-violet-500',
  'bg-rose-500',
  'bg-blue-500',
  'bg-lime-500',
  'bg-slate-500',
]

export function LanguageAnalysisSection({
  languages,
  error,
}: LanguageAnalysisSectionProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-950">
            Language analysis
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            Complete language composition reported by the backend.
          </p>
        </div>
        {languages ? (
          <p className="text-sm font-medium text-slate-600">
            {formatBytes(languages.total_bytes)} analyzed
          </p>
        ) : null}
      </div>

      {error ? (
        <p className="mt-4 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
          {error}
        </p>
      ) : null}

      {!error && languages?.languages.length === 0 ? (
        <p className="mt-4 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600">
          No programming languages were detected for this repository.
        </p>
      ) : null}

      {!error && languages && languages.languages.length > 0 ? (
        <div className="mt-5">
          <div
            className="flex h-3 overflow-hidden rounded-full bg-slate-100"
            aria-label="Repository language composition"
          >
            {languages.languages.map((language, index) => (
              <div
                key={language.name}
                title={`${language.name}: ${formatPercent(language.percentage)}`}
                className={languageColors[index % languageColors.length]}
                style={{ width: `${language.percentage}%` }}
              />
            ))}
          </div>

          <div className="mt-5 divide-y divide-slate-100">
            {languages.languages.map((language, index) => (
              <div
                key={language.name}
                className="grid gap-3 py-3 sm:grid-cols-[1fr_auto_auto]"
              >
                <div className="flex min-w-0 items-center gap-2">
                  <span
                    className={`h-2.5 w-2.5 rounded-full ${
                      languageColors[index % languageColors.length]
                    }`}
                  />
                  <span className="truncate text-sm font-medium text-slate-900">
                    {language.name}
                  </span>
                </div>
                <span className="text-sm text-slate-600">
                  {formatPercent(language.percentage)}
                </span>
                <span className="text-sm text-slate-500">
                  {formatBytes(language.bytes)}
                </span>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </section>
  )
}
