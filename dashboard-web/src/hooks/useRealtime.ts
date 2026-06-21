import { useEffect } from 'react'

import { useOpsStore } from '@/store/useOpsStore'
import { apiUrl } from '@/utils/api'

export function useRealtime() {
  const refreshAll = useOpsStore((state) => state.refreshAll)
  const setConnection = useOpsStore((state) => state.setConnection)

  useEffect(() => {
    setConnection('connecting')
    const source = new EventSource(apiUrl('/api/stream'))

    source.addEventListener('open', () => {
      setConnection('connected')
    })

    source.addEventListener('snapshot:update', () => {
      void refreshAll()
    })

    source.addEventListener('error', () => {
      setConnection('degraded')
    })

    return () => {
      source.close()
    }
  }, [refreshAll, setConnection])
}
