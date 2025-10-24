import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { WorkflowNav } from '@/components/sidebar/WorkflowNav';
import { cn } from '@/lib/utils';

export const AppShell: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="min-h-screen bg-background w-full">
      {/* Top Bar */}
      <header className="fixed top-0 left-0 right-0 z-50 h-16 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex h-full items-center px-4 gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="h-9 w-9"
            aria-label="Toggle sidebar"
          >
            <Menu className="h-5 w-5" />
          </Button>
          <div className="flex items-center gap-2">
            <div className="text-2xl font-bold text-foreground">
              Impact<span className="text-primary">View</span>
            </div>
          </div>
        </div>
      </header>

      {/* Layout Container */}
      <div className="flex pt-16 w-full">
        {/* Sidebar */}
        <aside
          className={cn(
            'fixed left-0 top-16 h-[calc(100vh-4rem)] border-r border-border bg-background transition-all duration-300 z-40',
            sidebarCollapsed ? 'w-16' : 'w-64'
          )}
        >
          <WorkflowNav collapsed={sidebarCollapsed} />
        </aside>

        {/* Main Content */}
        <main
          className={cn(
            'flex-1 transition-all duration-300',
            sidebarCollapsed ? 'ml-16' : 'ml-64'
          )}
        >
          <div className="p-8 space-y-6 max-w-[1600px]">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
