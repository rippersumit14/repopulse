//Handles frontend configuration
//It decides what backend base URL should be used 


const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim()

// Keeping the API base URL in one file prevents hardcoded backend URLs from
// spreading across components. Empty string means "use the current origin",
// which works with the Vite dev proxy for `/api`.
export const apiConfig = {
  baseUrl: configuredBaseUrl ? configuredBaseUrl.replace(/\/+$/, '') : '',
}

