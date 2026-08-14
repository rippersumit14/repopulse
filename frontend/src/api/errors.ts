
// Centralized API errors make UI handling simpler. Components can catch one
// error shape instead of checking raw fetch responses everywhere.
export type ApiErrorKind =
  | 'invalid_repository_url'
  | 'not_found'
  | 'network'
  | 'validation'
  | 'unexpected'

// Custom Error class that carries a friendly category and optional HTTP status.
export class ApiError extends Error {
  readonly kind: ApiErrorKind
  readonly status?: number

  constructor(message: string, kind: ApiErrorKind, status?: number) {
    super(message)
    this.name = 'ApiError'
    this.kind = kind
    this.status = status
  }
}

interface FastApiValidationIssue {
  msg?: string
  loc?: Array<string | number>
}

// Small runtime checks are used because data from fetch is `unknown` until we
// inspect it. This avoids unsafe `any` usage.
const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null

const isValidationIssue = (value: unknown): value is FastApiValidationIssue =>
  isRecord(value)

// FastAPI often returns `{ detail: "..." }` for simple errors like 404.
const getStringDetail = (payload: unknown): string | null => {
  if (!isRecord(payload)) {
    return null
  }

  return typeof payload.detail === 'string' ? payload.detail : null
}

// FastAPI/Pydantic validation errors usually return `{ detail: [...] }`.
// We pull the first message so the UI can show something understandable.
const getValidationMessage = (payload: unknown): string | null => {
  if (!isRecord(payload) || !Array.isArray(payload.detail)) {
    return null
  }

  const firstIssue = payload.detail.find(isValidationIssue)
  if (!firstIssue?.msg) {
    return null
  }

  return firstIssue.msg
}

// Converts backend HTTP errors into frontend-friendly ApiError objects.
export const mapApiError = (status: number, payload: unknown): ApiError => {
  if (status === 404) {
    return new ApiError(
      getStringDetail(payload) ?? 'That GitHub repository was not found.',
      'not_found',
      status,
    )
  }

  if (status === 422) {
    return new ApiError(
      getValidationMessage(payload) ??
        'The repository URL could not be validated. Check the URL and try again.',
      'validation',
      status,
    )
  }

  return new ApiError(
    getStringDetail(payload) ?? 'The backend returned an unexpected error.',
    'unexpected',
    status,
  )
}

// This is the final adapter for React components. It turns any thrown value into
// a plain sentence that can be shown safely in the UI.
export const toUserMessage = (error: unknown): string => {
  if (error instanceof ApiError) {
    return error.message
  }

  return 'Something went wrong while looking up the repository.'
}
