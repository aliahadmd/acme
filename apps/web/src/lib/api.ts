import { client } from '@acme/api-client'
import { env } from './env'

/**
 * Configure the generated API client. Called once per router creation
 * (see src/router.tsx) so both SSR and browser requests hit the right origin.
 */
export function configureClient(baseUrl: string) {
  client.setConfig({ baseUrl })
}
