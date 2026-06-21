import { useEffect } from 'react'

import { EntityDetail } from '@/components/EntityDetail'
import { SectionFrame } from '@/components/SectionFrame'
import { UnifiedList } from '@/components/UnifiedList'
import { useOpsStore } from '@/store/useOpsStore'

export default function ArchivePage() {
  const logs = useOpsStore((state) => state.logs)
  const panels = useOpsStore((state) => state.panels)
  const selectedEntity = useOpsStore((state) => state.selectedEntity)
  const refreshLogs = useOpsStore((state) => state.refreshLogs)
  const refreshPanels = useOpsStore((state) => state.refreshPanels)
  const selectEntity = useOpsStore((state) => state.selectEntity)

  useEffect(() => {
    void Promise.all([refreshLogs(), refreshPanels()])
  }, [refreshLogs, refreshPanels])

  return (
    <div className="space-y-6">
      <div className="grid gap-6 xl:grid-cols-2">
        <SectionFrame
          eyebrow="Archive"
          title="Audit log"
          subtitle="The chronological system trail, useful for understanding what happened and when."
        >
          <UnifiedList
            items={logs}
            selectedId={selectedEntity?.id}
            emptyLabel="No logs available."
            onSelect={(item) => void selectEntity(item.kind, item.id)}
          />
        </SectionFrame>

        <SectionFrame
          eyebrow="Workspace"
          title="Generated panels"
          subtitle="Structured material exported from Private OS and rendered in a readable way."
        >
          <UnifiedList
            items={panels}
            selectedId={selectedEntity?.id}
            emptyLabel="No panels available."
            onSelect={(item) => void selectEntity(item.kind, item.id)}
          />
        </SectionFrame>
      </div>

      <EntityDetail entity={selectedEntity} />
    </div>
  )
}
