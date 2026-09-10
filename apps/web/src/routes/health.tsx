import { getHealthOptions } from '@acme/api-client'
import { useQuery } from '@tanstack/react-query'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/health')({
  component: Health,
})

function Health() {
  const { data, isPending, error } = useQuery(getHealthOptions())

  return (
    <main
      style={{
        fontFamily: 'system-ui, sans-serif',
        maxWidth: 640,
        margin: '4rem auto',
        padding: '0 1rem',
      }}
    >
      <h1>API health</h1>
      {isPending && <p>Checking…</p>}
      {error && <p style={{ color: 'crimson' }}>{error.message}</p>}
      {data && (
        <p>
          status: <strong>{data.status}</strong> · environment: {data.environment}
        </p>
      )}
    </main>
  )
}
