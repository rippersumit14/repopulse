// These TypeScript interfaces describe the JSON contract shared with FastAPI.
// Keep them close to the backend response shape, and avoid adding UI-only
// fields here unless the backend really sends them.

export interface RepositoryUrlRequest {
  repository_url: string
}

export interface RepositoryValidationResponse {
  repository_url: string
  valid: boolean
}

export interface RepositoryMetadata {
  id: number
  name: string
  full_name: string
  description: string | null
  repository_url: string
  owner: string
  owner_avatar_url: string
  stars: number
  forks: number
  watchers: number
  open_issues: number
  language: string | null
  topics: string[]
  default_branch: string
  license: string | null
  is_fork: boolean
  archived: boolean
  visibility: string
  created_at: string
  updated_at: string
  pushed_at: string
}

export interface RepositoryLanguageBreakdown {
  name: string
  bytes: number
  percentage: number
}

export interface RepositoryLanguagesResponse {
  total_bytes: number
  languages: RepositoryLanguageBreakdown[]
}

export interface RepositoryCommitActivityResponse {
  total_recent_commits: number
  commits_last_7_days: number
  commits_last_30_days: number
  last_commit_at: string | null
  days_since_last_commit: number | null
  activity_level: string
}
