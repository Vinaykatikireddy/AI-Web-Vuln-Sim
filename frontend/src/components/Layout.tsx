import React from 'react'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import logoSvg from '../logo.svg';

const Layout: React.FC = () => {
  const { user, loading, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  const navigationItems = [
    { path: '/', name: 'Home' },
    { path: '/dashboard', name: 'Dashboard', auth: true },
    { path: '/labs', name: 'Labs', auth: true },
    { path: '/profile', name: 'Profile', auth: true },
    { path: '/settings', name: 'Settings', auth: true },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <img className="h-8 w-auto" src={logoSvg} alt="Attack Simulation Platform" />
                <span className="ml-2 text-xl font-bold text-gray-900">AttackSim</span>
              </div>
              <nav className="hidden sm:ml-6 sm:flex sm:space-x-8">
 {navigationItems.map((item) => (
                    item.auth ? (
                      user ? (
                        <Link
                          key={item.path}
                          to={item.path}
                          className={location.pathname === item.path
                            ? 'border-blue-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium'
                          }
                        >
                          {item.name}
                        </Link>
                      ) : null
                    ) : (
                      <Link
                        key={item.path}
                        to={item.path}
                        className={location.pathname === item.path
                          ? 'border-blue-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium'
                        }
                      >
                        {item.name}
                      </Link>
                    )
                  ))}
              </nav>
            </div>
            <div className="flex items-center">
              {loading ? (
                <div className="flex items-center">
                  <span className="text-sm text-gray-500">Loading...</span>
                </div>
              ) : user ? (
                <div className="ml-3 relative">
                  <div className="flex items-center">
                    <span className="text-sm text-gray-700 mr-2">{user?.username}</span>
                    <button
                      onClick={() => logout(navigate)}
                      className="btn btn-secondary text-sm"
                    >
                      Logout
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex items-center space-x-4">
                  <Link
                    to="/login"
                    className="btn btn-secondary text-sm"
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="btn btn-primary text-sm"
                  >
                    Register
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white shadow mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-500 text-sm">
            AI-Powered Web Application Attack Simulation Platform - For Educational Use Only
          </p>
        </div>
      </footer>
    </div>
  )
}

export default Layout