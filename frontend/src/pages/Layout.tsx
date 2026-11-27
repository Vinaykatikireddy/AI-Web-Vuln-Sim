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
    <div className="app-layout">

      {/* Header */}
      <header className="site-header">
        <div className="header-container">
          <div className="header-inner">

            {/* Logo */}
            <div className="header-brand">
              <Link to="/" className="brand-link">
                <img
                  className="brand-logo"
                  src={logoSvg}
                  alt="Attack Simulation Platform"
                />
                <span className="brand-name">
                  AttackSim
                </span>
              </Link>
            </div>

            {/* Desktop Navigation */}
            {user && (
              <nav className="desktop-nav">
                {navigationItems.map((item) => {
                  const isActive = location.pathname === item.path;

                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`nav-link ${isActive ? 'active' : ''}`}
                    >
                      {item.name}
                    </Link>
                  );
                })}
              </nav>
            )}

            {/* Mobile Hamburger */}
            {user && (
              <div className="mobile-nav-toggle-wrap">
                <button
                  type="button"
                  onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                  className="mobile-menu-btn"
                  aria-label="Toggle navigation menu"
                >
                  {mobileMenuOpen ? (
                    // X icon
                    <svg
                      className="icon-menu"
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
                      className="icon-menu"
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
                  <nav className="mobile-menu-dropdown">
                    {navigationItems.map((item) => {
                      const isActive = location.pathname === item.path;

                      return (
                        <Link
                          key={item.path}
                          to={item.path}
                          onClick={() => setMobileMenuOpen(false)}
                          className={`mobile-nav-link ${isActive ? 'active' : ''}`}
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
            <div className="header-auth">
              {loading ? (
                <div className="auth-loading">
                  <span className="auth-loading-text">
                    Loading...
                  </span>
                </div>
              ) : user ? (
                <div className="user-profile-bar">
                  <button
                    onClick={() => logout(navigate)}
                    className="btn btn-sm btn-outline btn-logout"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <div className="auth-links">
                  <Link
                    to="/login"
                    className="btn btn-sm btn-outline"
                  >
                    Login
                  </Link>

                  <Link
                    to="/register"
                    className="btn btn-sm btn-primary"
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
      <main className="main-content">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="site-footer">
        <div className="footer-container">
          <p className="footer-text">
            AI-Powered Web Application Attack Simulation Platform - For Educational Use Only
          </p>
        </div>
      </footer>
    </div>
  )
}

export default Layout
