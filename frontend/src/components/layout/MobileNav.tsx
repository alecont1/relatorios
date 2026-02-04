import { NavLink } from 'react-router-dom'
import { Home, ClipboardList, FileText, Settings, User, FolderKanban, Building2 } from 'lucide-react'
import { useAuthStore } from '@/features/auth'

/**
 * Mobile navigation with role-based menu items.
 *
 * Role hierarchy:
 * - superadmin: Sees Empresas, Templates, Empresa settings
 * - tenant_admin: Sees Templates, Empresa settings
 * - project_manager: Sees Projetos
 * - technician: Basic access
 * - viewer: Read-only access
 */
export function MobileNav() {
  const { user } = useAuthStore()

  // Permission checks based on new role hierarchy
  const isSuperadmin = user?.role === 'superadmin'
  const isTenantAdmin = user?.role === 'tenant_admin'
  const isProjectManager = user?.role === 'project_manager'

  const canManageTemplates = isSuperadmin || isTenantAdmin
  const canAccessSettings = isSuperadmin || isTenantAdmin
  const canManageProjects = isSuperadmin || isTenantAdmin || isProjectManager
  const canAccessTenants = isSuperadmin

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 safe-area-bottom">
      <div className="flex items-center justify-around h-16">
        <NavItem to="/" icon={Home} label="Inicio" />
        <NavItem to="/reports" icon={ClipboardList} label="Relatorios" />

        {/* Show projects for project managers and above */}
        {canManageProjects && (
          <NavItem to="/projects" icon={FolderKanban} label="Projetos" />
        )}

        {/* Show templates for tenant admins and superadmins */}
        {canManageTemplates && (
          <NavItem to="/templates" icon={FileText} label="Templates" />
        )}

        {/* Show tenants only for superadmin */}
        {canAccessTenants && (
          <NavItem to="/tenants" icon={Building2} label="Empresas" />
        )}

        {/* Show settings for tenant admins and superadmins */}
        {canAccessSettings && (
          <NavItem to="/settings" icon={Settings} label="Empresa" />
        )}

        {/* Profile is always visible */}
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
