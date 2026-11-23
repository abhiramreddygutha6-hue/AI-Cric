import { useEffect, useState } from 'react'
import { api } from './api.js'

// Fetch a path whenever it changes. Pass null to skip the request.
export function useApi(path) {
  const [state, setState] = useState({ data: null, error: null, loading: path != null })

  useEffect(() => {
    if (path == null) {
      setState({ data: null, error: null, loading: false })
      return undefined
    }
    let cancelled = false
    setState((s) => ({ ...s, loading: true, error: null }))
    api
      .get(path)
      .then((data) => !cancelled && setState({ data, error: null, loading: false }))
      .catch((e) => !cancelled && setState({ data: null, error: e.message, loading: false }))
    return () => {
      cancelled = true
    }
  }, [path])

  return state
}
