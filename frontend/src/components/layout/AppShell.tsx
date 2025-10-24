import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { WorkflowNav } from '@/components/sidebar/WorkflowNav';
import { cn } from '@/lib/utils';
import { useIsMobile } from '@/hooks/use-mobile';
import { Sheet, SheetContent } from '@/components/ui/sheet';

export const AppShell: React.FC = () => {
  const isMobile = useIsMobile();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

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
    <div className="min-h-screen w-full bg-background">
      <Sheet open={mobileSidebarOpen} onOpenChange={setMobileSidebarOpen}>
        <SheetContent side="left" className="w-full max-w-sm border-r border-border p-0">
          <WorkflowNav collapsed={false} onNavigate={() => setMobileSidebarOpen(false)} />
        </SheetContent>
      </Sheet>

      <header className="fixed left-0 right-0 top-0 z-50 h-16 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex h-full items-center gap-4 px-4">
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
      </header>

      <div className="flex w-full pt-16">
        <aside
          className={cn(
            'hidden lg:fixed lg:left-0 lg:top-16 lg:z-40 lg:h-[calc(100vh-4rem)] lg:border-r lg:border-border lg:bg-background lg:transition-[width] lg:duration-300',
            sidebarCollapsed ? 'lg:w-16' : 'lg:w-72'
          )}
          aria-label="Primary navigation"
        >
          <WorkflowNav collapsed={sidebarCollapsed} />
        </aside>

        <main
          className={cn(
            'flex-1 transition-all duration-300',
            isMobile ? 'ml-0' : sidebarCollapsed ? 'lg:ml-16' : 'lg:ml-72'
          )}
        >
          <div className="mx-auto w-full max-w-[1600px] space-y-6 px-4 py-6 sm:px-6 lg:px-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
