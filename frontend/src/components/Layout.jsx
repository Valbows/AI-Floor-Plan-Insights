import React, { useState, createContext, useContext } from 'react'
import Sidebar from './Sidebar'

// Create context for sidebar state
export const SidebarContext = createContext()

const Layout = ({ children }) => {
  const [isCollapsed, setIsCollapsed] = useState(false)

  return (
    <SidebarContext.Provider value={{ isCollapsed, setIsCollapsed }}>
      <div className="flex min-h-screen" style={{ background: '#F6F1EB' }}>
        <Sidebar isCollapsed={isCollapsed} setIsCollapsed={setIsCollapsed} />
        <main 
          className="flex-1 transition-all duration-300" 
          style={{ marginLeft: isCollapsed ? '80px' : '256px' }}
        >
          {children}
        </main>
      </div>
    </SidebarContext.Provider>
  )
}

export default Layout

