import type {
  RepositoryCommitActivityResponse,
  RepositoryLanguagesResponse,
  RepositoryMetadata,
} from '../../types/repository'
import { CommitActivitySection } from './components/CommitActivitySection'
import { LanguageAnalysisSection } from './components/LanguageAnalysisSection'
import { RepositoryHeader } from './components/RepositoryHeader'
import { RepositoryInfoSection } from './components/RepositoryInfoSection'
import { RepositoryStatsGrid } from './components/RepositoryStatsGrid'

export interface RepositoryAnalysisResult {
  repository: RepositoryMetadata
  languages: RepositoryLanguagesResponse | null
  activity: RepositoryCommitActivityResponse | null
  errors: {
    languages: string | null
    activity: string | null
  }
}

interface RepositoryAnalysisDashboardProps {
  analysis: RepositoryAnalysisResult
}

export function RepositoryAnalysisDashboard({
  analysis,
}: RepositoryAnalysisDashboardProps) {
  return (
    <div className="flex flex-col gap-5">
      <RepositoryHeader repository={analysis.repository} />
      <RepositoryStatsGrid repository={analysis.repository} />

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1.15fr)_minmax(360px,0.85fr)]">
        <LanguageAnalysisSection
          languages={analysis.languages}
          error={analysis.errors.languages}
        />
        <CommitActivitySection
          activity={analysis.activity}
          error={analysis.errors.activity}
        />
      </div>

      <RepositoryInfoSection repository={analysis.repository} />
    </div>
  )
}
