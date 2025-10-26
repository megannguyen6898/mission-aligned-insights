import React, { useEffect, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Menu, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { WorkflowNav } from '@/components/sidebar/WorkflowNav';
import { cn } from '@/lib/utils';
import { useIsMobile } from '@/hooks/use-mobile';
import { Sheet, SheetContent } from '@/components/ui/sheet';
import { AskAIDrawer } from '@/components/ai/AskAIDrawer';

export const AppShell: React.FC = () => {
  const isMobile = useIsMobile();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [aiDrawerOpen, setAIDrawerOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    if (isMobile) {
      setSidebarCollapsed(false);
    } else {
      setMobileSidebarOpen(false);
    }
  }, [isMobile]);

  const handleSidebarToggle = () => {
    if (isMobile) {
      setMobileSidebarOpen(true);
    } else {
      setSidebarCollapsed((prev) => !prev);
    }
  };

  return (
    <div className="app-surface w-full">
      <AskAIDrawer open={aiDrawerOpen} onOpenChange={setAIDrawerOpen} />
      <Sheet open={mobileSidebarOpen} onOpenChange={setMobileSidebarOpen}>
        <SheetContent side="left" className="w-full max-w-sm border-r border-border p-0">
          <WorkflowNav
            collapsed={false}
            currentPath={location.pathname}
            onNavigate={() => setMobileSidebarOpen(false)}
          />
        </SheetContent>
      </Sheet>

      <header className="fixed left-0 right-0 top-0 z-50 h-16 border-b border-border/60 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex h-full items-center justify-between gap-4 px-4">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleSidebarToggle}
              className="h-9 w-9"
              aria-label="Toggle navigation"
            >
              <Menu className="h-5 w-5" />
            </Button>
            <div className="flex items-center gap-2">
              <div className="text-2xl font-bold text-foreground">
                Impact<span className="text-primary">View</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              className="hidden sm:inline-flex rounded-full border-primary/40 bg-primary/10 px-4 text-sm font-medium text-primary hover:bg-primary hover:text-primary-foreground"
              onClick={() => setAIDrawerOpen(true)}
            >
              <Sparkles className="mr-2 h-4 w-4" />
              Ask AI
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="sm:hidden"
              onClick={() => setAIDrawerOpen(true)}
              aria-label="Open Ask AI"
            >
              <Sparkles className="h-5 w-5 text-primary" />
            </Button>
          </div>
        </div>
      </header>

      <div className="flex w-full pt-16">
        <aside
          className={cn(
            'hidden lg:fixed lg:left-0 lg:top-16 lg:z-40 lg:h-[calc(100vh-4rem)] lg:border-r lg:border-border/60 lg:bg-sidebar lg:transition-[width] lg:duration-300',
            sidebarCollapsed ? 'lg:w-20' : 'lg:w-80'
          )}
          aria-label="Primary navigation"
        >
          <WorkflowNav
            collapsed={sidebarCollapsed}
            currentPath={location.pathname}
            onNavigate={() => undefined}
          />
        </aside>

        <main
          className={cn(
            'flex-1 transition-all duration-300',
            isMobile ? 'ml-0' : sidebarCollapsed ? 'lg:ml-24' : 'lg:ml-80'
          )}
        >
          <div className="mx-auto w-full max-w-[1600px] space-y-8 bg-transparent px-4 py-8 sm:px-6 lg:px-12">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
