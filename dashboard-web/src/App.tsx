import { BrowserRouter, Route, Routes } from 'react-router-dom'

import { AppShell } from '@/components/AppShell'
import DashboardPage from '@/pages/DashboardPage'
import ArchivePage from '@/pages/ArchivePage'
import OperationsPage from '@/pages/OperationsPage'
import { useOpsStore } from '@/store/useOpsStore'

export default function App() {
  const connection = useOpsStore((state) => state.connection)
  const generatedAt = useOpsStore((state) => state.snapshot?.generatedAt)

  return (
    <BrowserRouter>
      <AppShell connection={connection} generatedAt={generatedAt}>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/operations" element={<OperationsPage />} />
          <Route path="/archive" element={<ArchivePage />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  )
}
