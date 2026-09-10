import { createRouter } from '@tanstack/react-router'
import { setupRouterSsrQueryIntegration } from '@tanstack/react-router-ssr-query'
import { configureClient } from './lib/api'
import { env } from './lib/env'
import { createQueryClient } from './lib/queryClient'
import { routeTree } from './routeTree.gen'

export function getRouter() {
  const queryClient = createQueryClient()

  // Point the generated API client at the right origin for this runtime
  // (server gets API_BASE_URL, browser gets VITE_API_BASE_URL).
  configureClient(env.apiBaseUrl)

  const router = createRouter({
    routeTree,
    context: { queryClient },
    scrollRestoration: true,
    defaultPreload: 'intent',
  })

  // Dehydrates the query cache on SSR, rehydrates it in the browser.
  setupRouterSsrQueryIntegration({ router, queryClient })

  return router
}

declare module '@tanstack/react-router' {
  interface Register {
    router: ReturnType<typeof getRouter>
  }
}
