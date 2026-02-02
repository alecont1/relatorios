import { Link, useNavigate } from 'react-router-dom'
import { LogOut, Users, Home, Building2, Settings, FileText, ClipboardList, Download } from 'lucide-react'
import { useAuthStore, useLogout } from '@/features/auth'
import { MobileNav } from './MobileNav'
import { usePWA } from '@/hooks/usePWA'

interface AppLayoutProps {
  children: React.ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  const { user } = useAuthStore()
  const logout = useLogout()
  const navigate = useNavigate()
  const { isInstallable, install } = usePWA()

  const handleLogout = async () => {
    await logout.mutateAsync()
    navigate('/login')
  }

  const canManageUsers = user?.role === 'admin' || user?.role === 'superadmin'

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
                {canManageUsers && (
                  <Link
                    to="/users"
                    className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                  >
                    <Users className="h-4 w-4" />
                    Usuarios
                  </Link>
                )}
                {canManageUsers && (
                  <Link
                    to="/templates"
                    className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                  >
                    <FileText className="h-4 w-4" />
                    Templates
                  </Link>
                )}
                <Link
                  to="/reports"
                  className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                >
                  <ClipboardList className="h-4 w-4" />
                  Relatorios
                </Link>
                {user?.role === 'superadmin' && (
                  <Link
                    to="/tenants"
                    className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                  >
                    <Building2 className="h-4 w-4" />
                    Tenants
                  </Link>
                )}
                {(user?.role === 'admin' || user?.role === 'superadmin') && (
                  <Link
                    to="/settings"
                    className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                  >
                    <Settings className="h-4 w-4" />
                    Configuracoes
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
              <span className="text-sm text-gray-600">
                {user?.full_name}
              </span>
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
