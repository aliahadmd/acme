import { z } from 'zod'

const envSchema = z.object({
  apiBaseUrl: z.url(),
})

function resolveApiBaseUrl(): string {
  const fallback = 'http://localhost:8000'
  // SSR/server runtime: API_BASE_URL points at the API from the Node process.
  // In prod this may be an internal docker-network URL — never ship it to the browser.
  if (import.meta.env.SSR) {
    return process.env.API_BASE_URL ?? import.meta.env.VITE_API_BASE_URL ?? fallback
  }
  // Browser bundle: only VITE_-prefixed vars are inlined at build time.
  return import.meta.env.VITE_API_BASE_URL ?? fallback
}

export const env = envSchema.parse({ apiBaseUrl: resolveApiBaseUrl() })
