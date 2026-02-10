import { Link, useNavigate } from 'react-router-dom'
import { LogOut, Users, Home, Building2, Settings, FileText, ClipboardList, Download, Award, Shield, CreditCard } from 'lucide-react'
import { useAuthStore, useLogout } from '@/features/auth'
import { MobileNav } from './MobileNav'
import { usePWA } from '@/hooks/usePWA'

interface AppLayoutProps {
  children: React.ReactNode
}

/**
 * Role hierarchy:
 * - superadmin: Global admin (tenant_id = NULL) - Sees all tenants
 * - tenant_admin: Admin of a specific tenant - Manages users, templates, settings for their tenant
 * - project_manager: Manager of specific projects - Manages reports in assigned projects
 * - technician: Field technician - Creates and edits reports
 * - viewer: Read-only access - Can only view reports
 */

export function AppLayout({ children }: AppLayoutProps) {
  const { user } = useAuthStore()
  const logout = useLogout()
  const navigate = useNavigate()
  const { isInstallable, install } = usePWA()

  const handleLogout = async () => {
    await logout.mutateAsync()
    navigate('/login')
  }

  // Permission checks based on new role hierarchy
  const isSuperadmin = user?.role === 'superadmin'
  const isTenantAdmin = user?.role === 'tenant_admin'
  const isProjectManager = user?.role === 'project_manager'

  // Combined checks for common permissions
  const canManageUsers = isSuperadmin || isTenantAdmin
  const canManageTemplates = isSuperadmin || isTenantAdmin
  const canManageProjects = isSuperadmin || isTenantAdmin || isProjectManager
  const canAccessSettings = isSuperadmin || isTenantAdmin
  const canAccessTenants = isSuperadmin // Only superadmin sees tenants menu

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Desktop Navigation */}
      <nav className="hidden md:block bg-white shadow sticky top-0 z-40">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 justify-between">
            <div className="flex items-center gap-8">
              <Link to="/" className="text-xl font-bold text-gray-900">
                SmartHand
              </Link>
              <div className="flex gap-4">
                <Link
                  to="/"
                  className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                >
                  <Home className="h-4 w-4" />
                  Dashboard
                </Link>

                {/* SuperAdmin - Only superadmin */}
                {isSuperadmin && (
                  <Link
                    to="/superadmin/tenants"
                    className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                  >
                    <Shield className="h-4 w-4" />
                    Gestao Tenants
                  </Link>
                )}
                {isSuperadmin && (
                  <Link
                    to="/superadmin/plans"
                    className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                  >
                    <CreditCard className="h-4 w-4" />
                    Planos
                  </Link>
                )}

                {/* Tenants - Only superadmin */}
                {canAccessTenants && (
                  <Link
                    to="/tenants"
                    className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                  >
                    <Building2 className="h-4 w-4" />
                    Empresas
                  </Link>
                )}

                {/* Users - tenant_admin and superadmin */}
                {canManageUsers && (
                  <Link
                    to="/users"
                    className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                  >
                    <Users className="h-4 w-4" />
                    Usuarios
                  </Link>
                )}

                {/* Templates - tenant_admin and superadmin */}
                {canManageTemplates && (
                  <Link
                    to="/templates"
                    className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                  >
                    <FileText className="h-4 w-4" />
                    Templates
                  </Link>
                )}

                {/* Certificados - tenant_admin and superadmin */}
                {canManageTemplates && (
                  <Link
                    to="/certificates"
                    className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                  >
                    <Award className="h-4 w-4" />
                    Certificados
                  </Link>
                )}

                {/* Reports - All authenticated users can see reports */}
                <Link
                  to="/reports"
                  className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                >
                  <ClipboardList className="h-4 w-4" />
                  Relatorios
                </Link>

                {/* Settings - tenant_admin and superadmin */}
                {canAccessSettings && (
                  <Link
                    to="/settings"
                    className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                  >
                    {isSuperadmin ? <Settings className="h-4 w-4" /> : <Building2 className="h-4 w-4" />}
                    {isSuperadmin ? 'Configuracoes' : 'Empresa'}
                  </Link>
                )}
              </div>
            </div>
            <div className="flex items-center gap-4">
              {isInstallable && (
                <button
                  onClick={install}
                  className="flex items-center gap-1 px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg"
                >
                  <Download className="h-4 w-4" />
                  Instalar App
                </button>
              )}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">
                  {user?.full_name}
                </span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
                  {getRoleDisplayName(user?.role)}
                </span>
              </div>
              <button
                onClick={handleLogout}
                disabled={logout.isPending}
                className="flex items-center gap-1 rounded-lg px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              >
                <LogOut className="h-4 w-4" />
                Sair
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile Header */}
      <header className="md:hidden bg-white shadow sticky top-0 z-40">
        <div className="flex items-center justify-between h-14 px-4">
          <Link to="/" className="text-lg font-bold text-gray-900">
            SmartHand
          </Link>
          <div className="flex items-center gap-2">
            {isInstallable && (
              <button
                onClick={install}
                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
              >
                <Download className="h-5 w-5" />
              </button>
            )}
            <button
              onClick={handleLogout}
              disabled={logout.isPending}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Page content */}
      <main className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8 pb-20 md:pb-6">
        {children}
      </main>

      {/* Mobile Navigation */}
      <MobileNav />
    </div>
  )
}

/**
 * Get human-readable display name for role
 */
function getRoleDisplayName(role?: string): string {
  switch (role) {
    case 'superadmin':
      return 'Super Admin'
    case 'tenant_admin':
      return 'Admin'
    case 'project_manager':
      return 'Gerente'
    case 'technician':
      return 'Tecnico'
    case 'viewer':
      return 'Visualizador'
    default:
      return role || 'Usuario'
  }
}
