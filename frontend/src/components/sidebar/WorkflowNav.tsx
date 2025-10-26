import React, { useMemo } from 'react';
import { NavLink } from 'react-router-dom';
import {
  Upload,
  GitBranch,
  LayoutDashboard,
  FileText,
  Settings,
  LucideIcon
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { ScrollArea } from '@/components/ui/scroll-area';
import { SpacesTree } from '@/components/sidebar/SpacesTree';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';

interface NavItem {
  name: string;
  to: string;
  icon: LucideIcon;
  description: string;
}

const navItems: NavItem[] = [
  {
    name: 'Upload',
    to: '/upload',
    icon: Upload,
    description: 'Bring in source data',
  },
  {
    name: 'Mapping',
    to: '/mapping',
    icon: GitBranch,
    description: 'Align columns to standards',
  },
  {
    name: 'Dashboard',
    to: '/dashboard',
    icon: LayoutDashboard,
    description: 'Review KPIs & narratives',
  },
  {
    name: 'Reports',
    to: '/reports',
    icon: FileText,
    description: 'Generate stakeholder-ready PDFs',
  },
  {
    name: 'Settings',
    to: '/settings',
    icon: Settings,
    description: 'Manage org preferences',
  },
];

interface WorkflowNavProps {
  collapsed: boolean;
  onNavigate?: () => void;
  currentPath?: string;
}

type StepState = 'complete' | 'current' | 'upcoming';

export const WorkflowNav: React.FC<WorkflowNavProps> = ({ collapsed, onNavigate, currentPath }) => {
  const activeIndex = useMemo(() => {
    if (!currentPath) return -1;
    return navItems.findIndex((item) =>
      currentPath === item.to || currentPath.startsWith(`${item.to}/`)
    );
  }, [currentPath]);

  const getStepState = (index: number): StepState => {
    if (activeIndex === -1) {
      return index === 0 ? 'current' : 'upcoming';
    }
    if (index < activeIndex) return 'complete';
    if (index === activeIndex) return 'current';
    return 'upcoming';
  };

  return (
    <nav className="flex h-full flex-col">
      <ScrollArea className="flex-1">
        <div className="space-y-6 px-2 py-4">
          <div className="space-y-2" aria-label="Impact workflow">
            {!collapsed && (
              <div className="px-3 pb-2">
                <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  Impact workflow
                </p>
                <p className="text-xs text-muted-foreground/80">
                  Follow the steps to go from raw data to ready reports.
                </p>
              </div>
            )}
            {navItems.map((item, index) => {
              const state = getStepState(index);
              return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    'group flex items-center gap-3 rounded-2xl px-3 py-3 text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2',
                    state === 'current'
                      ? 'bg-primary/10 text-primary soft-shadow ring-1 ring-primary/30'
                      : 'text-foreground hover:bg-accent/30 hover:text-primary',
                    collapsed && 'justify-center px-2 py-2',
                    isActive && !collapsed ? 'soft-shadow' : ''
                  )
                }
                title={collapsed ? item.name : undefined}
                onClick={onNavigate}
              >
                <span
                  className={cn(
                    'flex h-9 w-9 items-center justify-center rounded-full border text-primary',
                    state === 'complete' && 'border-primary bg-primary text-primary-foreground',
                    state === 'current' && 'border-primary bg-primary/10',
                    state === 'upcoming' && 'border-border/80 bg-background'
                  )}
                >
                  <item.icon className={cn('h-4 w-4', collapsed && 'h-5 w-5')} aria-hidden />
                </span>
                {!collapsed && (
                  <div className="flex-1">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-sm font-semibold text-foreground">{item.name}</span>
                      {state === 'complete' && (
                        <Badge className="bg-primary/15 text-primary" variant="secondary">
                          Done
                        </Badge>
                      )}
                      {state === 'current' && (
                        <Badge className="bg-accent/20 text-foreground" variant="outline">
                          In progress
                        </Badge>
                      )}
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground leading-relaxed">
                      {item.description}
                    </p>
                  </div>
                )}
              </NavLink>
            );
            })}
          </div>

          <Separator className="border-border/60" />

          <SpacesTree collapsed={collapsed} />
        </div>
      </ScrollArea>
    </nav>
  );
};
