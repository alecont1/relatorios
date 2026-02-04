import { NavLink } from 'react-router-dom'
import { Home, ClipboardList, FileText, Settings, User } from 'lucide-react'
import { useAuthStore } from '@/features/auth'

export function MobileNav() {
  const { user } = useAuthStore()
  const canManageTemplates = user?.role === 'admin' || user?.role === 'superadmin'
  const canAccessSettings = user?.role === 'admin' || user?.role === 'superadmin'

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 safe-area-bottom">
      <div className="flex items-center justify-around h-16">
        <NavItem to="/" icon={Home} label="Inicio" />
        <NavItem to="/reports" icon={ClipboardList} label="Relatorios" />
        {canManageTemplates && (
          <NavItem to="/templates" icon={FileText} label="Templates" />
        )}
        {canAccessSettings && (
          <NavItem to="/settings" icon={Settings} label="Empresa" />
        )}
        <NavItem to="/profile" icon={User} label="Perfil" />
      </div>
    </nav>
  )
}

interface NavItemProps {
  to: string
  icon: React.ComponentType<{ className?: string }>
  label: string
}

function NavItem({ to, icon: Icon, label }: NavItemProps) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex flex-col items-center justify-center min-w-[64px] min-h-[48px] px-2 py-1 ${
          isActive
            ? 'text-blue-600'
            : 'text-gray-500 hover:text-gray-900'
        }`
      }
    >
      <Icon className="h-6 w-6" />
      <span className="text-xs mt-0.5">{label}</span>
    </NavLink>
  )
}
