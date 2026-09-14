import React from 'react'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import logoSvg from '../logo.svg';
import { useState } from 'react'

const Layout: React.FC = () => {
  const { user, loading, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  const navigationItems = [
    { path: '/', name: 'Home' },
    { path: '/dashboard', name: 'Dashboard' },
    { path: '/labs', name: 'Labs' },
    { path: '/profile', name: 'Profile' },
  ]

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">

      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16 overflow-auto">

            {/* Logo */}
            <div className="flex-shrink-0">
              <Link to="/" className="flex items-center">
                <img
                  className="h-8 w-auto"
                  src={logoSvg}
                  alt="Attack Simulation Platform"
                />
                <span className="ml-2 text-xl font-bold text-gray-900 whitespace-nowrap">
                  AttackSim
                </span>
              </Link>
            </div>

            {/* Desktop Navigation */}
            {user && (
              <nav className="hidden md:flex items-stretch justify-end ml-auto mr-4 lg:mr-6">
                {navigationItems.map((item) => {
                  const isActive = location.pathname === item.path;

                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`
                      inline-flex items-center justify-center
                      px-3 lg:px-4
                      pt-1
                      border-b-2
                      text-sm lg:text-base
                      font-medium
                      whitespace-nowrap
                      transition-colors
                      ${isActive
                          ? "border-blue-500 text-gray-900"
                          : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                        }
                    `}
                    >
                      {item.name}
                    </Link>
                  );
                })}
              </nav>
            )}

            {/* Mobile Hamburger */}
            {user && (
              <div className="md:hidden ml-auto mr-4 relative">
                <button
                  type="button"
                  onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                  className="p-2 rounded-md text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                  aria-label="Toggle navigation menu"
                >
                  {mobileMenuOpen ? (
                    // X icon
                    <svg
                      className="w-6 h-6"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  ) : (
                    // Hamburger icon
                    <svg
                      className="w-6 h-6"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 6h16M4 12h16M4 18h16"
                      />
                    </svg>
                  )}
                </button>

                {/* Mobile Menu */}
                {mobileMenuOpen && (
                  <nav className="absolute right-0 top-full mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg py-2 z-50">
                    {navigationItems.map((item) => {
                      const isActive = location.pathname === item.path;

                      return (
                        <Link
                          key={item.path}
                          to={item.path}
                          onClick={() => setMobileMenuOpen(false)}
                          className={`
                          block px-4 py-3 text-sm font-medium
                          ${isActive
                              ? "bg-blue-50 text-blue-600"
                              : "text-gray-700 hover:bg-gray-50"
                            }
                        `}
                        >
                          {item.name}
                        </Link>
                      );
                    })}
                  </nav>
                )}
              </div>
            )}

            {/* Account / Authentication */}
            <div className="flex-shrink-0">
              {loading ? (
                <div className="flex items-center">
                  <span className="text-sm text-gray-500 whitespace-nowrap">
                    Loading...
                  </span>
                </div>
              ) : user ? (
                <div className="flex items-center gap-2 lg:gap-3">
                  <span className="text-sm lg:text-base text-gray-700 max-w-[120px] truncate">
                    {user?.username}
                  </span>

                  <button
                    onClick={() => logout(navigate)}
                    className="btn btn-secondary text-sm lg:text-base whitespace-nowrap"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-2 lg:gap-4">
                  <Link
                    to="/login"
                    className="btn btn-secondary text-sm lg:text-base whitespace-nowrap"
                  >
                    Login
                  </Link>

                  <Link
                    to="/register"
                    className="btn btn-primary text-sm lg:text-base whitespace-nowrap"
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
      <main className="max-w-7xl w-full mx-auto px-4 md:px-6 lg:px-8 py-8 flex-1">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-500 text-md">
            AI-Powered Web Application Attack Simulation Platform - For Educational Use Only
          </p>
        </div>
      </footer>
    </div>
  )
}

export default Layout