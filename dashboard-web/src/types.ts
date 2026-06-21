export type EntityKind = 'task' | 'approval' | 'followup' | 'panel' | 'log'

export type UnifiedItem = {
  id: string
  kind: EntityKind
  title: string
  status: string
  updatedAt: string
  relatedTaskId?: string
  tags: string[]
  preview: string
}

export type TimelineEvent = {
  id: string
  at: string
  kind: EntityKind | 'system'
  label: string
  severity: 'info' | 'warning' | 'critical'
  entityId?: string
  entityKind?: EntityKind | 'log'
}

export type DashboardSnapshot = {
  generatedAt: string
  summary: {
    activeTasks: number
    pendingApprovals: number
    dueFollowups: number
    decisionRequests: number
    recentEvents: number
    panels: number
    logs: number
  }
  priorities: UnifiedItem[]
  timeline: TimelineEvent[]
  health: {
    mode: 'read_only'
    realtime: 'connected' | 'degraded' | 'polling'
    source: 'local_sqlite'
    workspaceRoot: string
  }
}

export type EntityDetail = {
  id: string
  kind: EntityKind
  title: string
  status: string
  relatedTaskId?: string
  data: Record<string, unknown>
  rendered?: string
}

export type PaginatedItems = {
  items: UnifiedItem[]
  count: number
}
