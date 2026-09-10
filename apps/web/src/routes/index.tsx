import { listUsersOptions } from '@acme/api-client'
import { useQuery } from '@tanstack/react-query'
import { createFileRoute, Link } from '@tanstack/react-router'

export const Route = createFileRoute('/')({
  // Prefetch on the server during SSR; the browser hydrates with the data.
  loader: ({ context }) => context.queryClient.ensureQueryData(listUsersOptions()),
  component: Home,
})

function Home() {
  const { data, isPending, error } = useQuery(listUsersOptions())

  return (
    <main
      style={{
        fontFamily: 'system-ui, sans-serif',
        maxWidth: 640,
        margin: '4rem auto',
        padding: '0 1rem',
      }}
    >
      <h1>acme</h1>
      <p>
        Full-stack scaffold: TanStack Start (SSR) + FastAPI, connected by a generated typed client.
        This list is server-prefetched, then hydrated.
      </p>
      <h2>Users</h2>
      {isPending && <p>Loading…</p>}
      {error && <p style={{ color: 'crimson' }}>Failed to load users</p>}
      {data && (
        <ul>
          {data.data.map((user) => (
            <li key={user.id}>
              {user.name} — {user.email}
            </li>
          ))}
          {data.data.length === 0 && <li>No users yet — POST to /api/users to add some.</li>}
        </ul>
      )}
      <p>
        <Link to="/health">API health →</Link>
      </p>
    </main>
  )
}
