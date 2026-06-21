import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import { Activity, Archive, PanelLeftOpen, Radio } from 'lucide-react'

import { cn } from '@/lib/utils'

type AppShellProps = {
  children: ReactNode
  connection: 'connecting' | 'connected' | 'degraded'
  generatedAt?: string
}

const links = [
  { to: '/', label: 'Dashboard', icon: Activity, end: true },
  { to: '/operazioni', label: 'Operazioni', icon: PanelLeftOpen },
  { to: '/archivio', label: 'Archivio', icon: Archive },
]

export function AppShell({ children, connection, generatedAt }: AppShellProps) {
  return (
    <div className="min-h-screen bg-[var(--paper)] text-[var(--ink)]">
      <div className="mx-auto grid min-h-screen max-w-[1600px] grid-cols-1 gap-8 px-5 py-6 lg:grid-cols-[248px_minmax(0,1fr)] lg:px-8">
        <aside className="rounded-[32px] border border-black/8 bg-white/78 p-6 shadow-[0_30px_70px_rgba(19,19,18,0.05)] backdrop-blur">
          <div className="border-b border-black/6 pb-6">
            <p className="text-[11px] uppercase tracking-[0.26em] text-black/35">Davide Private Ops</p>
            <h1 className="mt-3 font-serif text-[2rem] leading-none text-black/85">Osservatorio locale</h1>
            <p className="mt-3 text-sm leading-6 text-black/45">
              Vista editoriale, sola lettura, agganciata ai segnali reali del tuo Private OS.
            </p>
          </div>

          <nav className="mt-6 space-y-2">
            {links.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                end={end}
                to={to}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 rounded-2xl px-4 py-3 text-sm transition',
                    isActive ? 'bg-black text-white shadow-lg shadow-black/10' : 'text-black/58 hover:bg-black/[0.04]',
                  )
                }
              >
                <Icon className="h-4 w-4" />
                <span>{label}</span>
              </NavLink>
            ))}
          </nav>

          <div className="mt-8 rounded-[24px] border border-black/8 bg-[var(--paper-strong)] p-4">
            <div className="flex items-center gap-3">
              <Radio className={cn('h-4 w-4', connection === 'connected' ? 'text-emerald-700' : 'text-amber-700')} />
              <div>
                <p className="text-[11px] uppercase tracking-[0.24em] text-black/35">Realtime</p>
                <p className="text-sm text-black/70">
                  {connection === 'connected' ? 'Connesso allo stream locale' : connection === 'degraded' ? 'Riconnessione in corso' : 'Connessione iniziale'}
                </p>
              </div>
            </div>
            <p className="mt-4 text-xs leading-5 text-black/45">
              {generatedAt ? `Ultimo snapshot ${new Date(generatedAt).toLocaleString('it-IT')}` : 'In attesa del primo snapshot'}
            </p>
          </div>
        </aside>

        <main className="pb-12">{children}</main>
      </div>
    </div>
  )
}
