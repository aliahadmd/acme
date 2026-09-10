import { describe, expect, it } from 'vitest'
import { env } from '../src/lib/env'

describe('env', () => {
  it('falls back to the local API URL when no env vars are set', () => {
    expect(env.apiBaseUrl).toBe('http://localhost:8000')
  })
})
