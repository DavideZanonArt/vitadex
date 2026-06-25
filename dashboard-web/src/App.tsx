import { BrowserRouter, Route, Routes } from 'react-router-dom'

import { AppShell } from '@/components/AppShell'
import { useRealtime } from '@/hooks/useRealtime'
import DashboardPage from '@/pages/DashboardPage'
import KnowledgePage from '@/pages/KnowledgePage'
import OperationsPage from '@/pages/OperationsPage'
import { useOpsStore } from '@/store/useOpsStore'

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/knowledge" element={<KnowledgePage />} />
      <Route path="/operations" element={<OperationsPage />} />
    </Routes>
  )
}

export default function App() {
  const connection = useOpsStore((state) => state.connection)
  const generatedAt = useOpsStore((state) => state.snapshot?.generatedAt)
  const hasLocalData = useOpsStore(
    (state) =>
      Boolean(state.snapshot) ||
      Boolean(state.knowledgeSnapshot) ||
      state.operations.length > 0 ||
      Boolean(state.selectedEntity) ||
      Boolean(state.selectedKnowledgeItem),
  )

  useRealtime()

  return (
    <BrowserRouter>
      <AppShell connection={connection} generatedAt={generatedAt} hasLocalData={hasLocalData}>
        <AppRoutes />
      </AppShell>
    </BrowserRouter>
  )
}
