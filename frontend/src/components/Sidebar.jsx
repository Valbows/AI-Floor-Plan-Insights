import React, { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Home, BarChart3, Plus, LogOut, User, ChevronLeft, ChevronRight, Wrench } from 'lucide-react'

const Sidebar = ({ isCollapsed, setIsCollapsed }) => {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const navItems = [
    { path: '/dashboard', icon: Home, label: 'Properties' },
    { path: '/analytics', icon: BarChart3, label: 'Analytics' },
    { path: '/properties/new', icon: Plus, label: 'Add Property' },
    { path: '/agent-tools', icon: Wrench, label: 'Agent Tools', special: true },
  ]

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div 
      className="fixed left-0 top-0 h-screen bg-black flex flex-col transition-all duration-300 z-50" 
      style={{ 
        width: isCollapsed ? '80px' : '256px',
        borderRight: '4px solid #FF5959' 
      }}
    >
      {/* Logo & Toggle */}
      <div className="p-6 border-b" style={{ borderBottomColor: '#333333' }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Home className="w-6 h-6" style={{ color: '#FF5959' }} />
            {!isCollapsed && <span className="text-xl font-black uppercase tracking-tight text-white">FP AI</span>}
          </div>
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1 rounded transition-all"
            style={{ color: '#CCCCCC' }}
            onMouseEnter={(e) => e.currentTarget.style.color = '#FF5959'}
            onMouseLeave={(e) => e.currentTarget.style.color = '#CCCCCC'}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>
        {!isCollapsed && <p className="text-xs text-gray-400 mt-1">Floor Plan Insights</p>}
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path || (item.path === '/agent-tools' && location.pathname.includes('/agent-tools'))
          const Icon = item.icon
          
          return (
            <div key={item.path}>
              {/* Add divider before Agent Tools */}
              {item.special && (
                <div className="my-3 border-t" style={{borderColor: '#333333'}} />
              )}
              
              <Link
                to={item.path}
                className="flex items-center rounded-lg transition-all group"
                style={{
                  background: isActive ? '#FF5959' : (item.special ? '#1A1A1A' : 'transparent'),
                  color: isActive ? '#FFFFFF' : '#CCCCCC',
                  padding: isCollapsed ? '12px' : '12px 16px',
                  justifyContent: isCollapsed ? 'center' : 'flex-start',
                  gap: isCollapsed ? '0' : '12px',
                  border: item.special && !isActive ? '2px solid #333333' : 'none'
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.background = item.special ? '#2A2A2A' : '#1A1A1A'
                    e.currentTarget.style.color = '#FFFFFF'
                    if (item.special) {
                      e.currentTarget.style.borderColor = '#FF5959'
                    }
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.background = item.special ? '#1A1A1A' : 'transparent'
                    e.currentTarget.style.color = '#CCCCCC'
                    if (item.special) {
                      e.currentTarget.style.borderColor = '#333333'
                    }
                  }
                }}
                title={isCollapsed ? item.label : ''}
              >
                <Icon className="w-5 h-5" />
                {!isCollapsed && <span className="font-bold text-sm uppercase tracking-wide">{item.label}</span>}
              </Link>
            </div>
          )
        })}
      </nav>

      {/* User Info & Logout */}
      <div className="p-4 border-t" style={{ borderTopColor: '#333333' }}>
        {!isCollapsed ? (
          <>
            <div className="flex items-center space-x-3 px-4 py-3 rounded-lg mb-2" style={{ background: '#1A1A1A' }}>
              <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ background: '#FF5959' }}>
                <User className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs text-gray-400">Logged in as</p>
                <p className="text-sm text-white font-medium truncate">{user?.email}</p>
              </div>
            </div>
            
            <button
              onClick={handleLogout}
              className="w-full flex items-center justify-center space-x-2 px-4 py-3 rounded-lg transition-all"
              style={{ background: 'transparent', color: '#FF5959', border: '2px solid #FF5959' }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#FF5959'
                e.currentTarget.style.color = '#FFFFFF'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent'
                e.currentTarget.style.color = '#FF5959'
              }}
            >
              <LogOut className="w-4 h-4" />
              <span className="font-bold text-sm uppercase">Logout</span>
            </button>
          </>
        ) : (
          <>
            <div className="flex justify-center mb-2">
              <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ background: '#FF5959' }}>
                <User className="w-5 h-5 text-white" />
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="w-full flex items-center justify-center p-3 rounded-lg transition-all"
              style={{ background: 'transparent', color: '#FF5959', border: '2px solid #FF5959' }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#FF5959'
                e.currentTarget.style.color = '#FFFFFF'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent'
                e.currentTarget.style.color = '#FF5959'
              }}
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </>
        )}
      </div>
    </div>
  )
}

export default Sidebar

