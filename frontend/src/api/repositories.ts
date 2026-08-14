import { apiConfig } from './config'
import { ApiError, mapApiError } from './errors'
import type {
  RepositoryMetadata,
  RepositoryUrlRequest,
  RepositoryValidationResponse,
} from '../types/repository'

// Generic helper for POST requests that send and receive JSON.
// TRequest is the TypeScript type for the request body.
// TResponse is the TypeScript type we expect back from FastAPI.
const postJson = async <TResponse, TRequest>(
  path: string,
  body: TRequest,
): Promise<TResponse> => {
  let response: Response

  try {
    // Components should not call fetch directly. This API layer keeps backend
    // communication in one predictable place.
    response = await fetch(`${apiConfig.baseUrl}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
  } catch {
    // Fetch throws here for network-level failures, such as backend not running
    // or a blocked CORS/proxy request.
    throw new ApiError(
      'RepoPulse backend is unavailable. Make sure the FastAPI server is running.',
      'network',
    )
  }

  // Not every error response is guaranteed to contain valid JSON, so parsing is
  // protected with catch. That keeps error handling stable.
  const payload: unknown = await response.json().catch(() => null)

  if (!response.ok) {
    throw mapApiError(response.status, payload)
  }

  // The backend contract defines the response shape. TypeScript cannot validate
  // runtime JSON by itself, so this cast tells the frontend what contract to use.
  return payload as TResponse
}

// Step 1 of the flow: ask FastAPI whether the URL is acceptable.
export const validateRepositoryUrl = (
  repositoryUrl: string,
): Promise<RepositoryValidationResponse> =>
  postJson<RepositoryValidationResponse, RepositoryUrlRequest>(
    '/api/v1/repositories/validate',
    {
      repository_url: repositoryUrl,
    },
  )

// Step 2 of the flow: after validation, fetch the repository metadata.
export const fetchRepositoryMetadata = (
  repositoryUrl: string,
): Promise<RepositoryMetadata> =>
  postJson<RepositoryMetadata, RepositoryUrlRequest>(
    '/api/v1/repositories/metadata',
    {
      repository_url: repositoryUrl,
    },
  )
