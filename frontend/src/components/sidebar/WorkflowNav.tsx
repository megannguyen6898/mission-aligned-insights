import React from 'react';
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

interface NavItem {
  name: string;
  to: string;
  icon: LucideIcon;
}

const navItems: NavItem[] = [
  { name: 'Upload', to: '/upload', icon: Upload },
  { name: 'Mapping', to: '/mapping', icon: GitBranch },
  { name: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
  { name: 'Reports', to: '/reports', icon: FileText },
  { name: 'Settings', to: '/settings', icon: Settings },
];

interface WorkflowNavProps {
  collapsed: boolean;
  onNavigate?: () => void;
}

export const WorkflowNav: React.FC<WorkflowNavProps> = ({ collapsed, onNavigate }) => {
  return (
    <nav className="flex h-full flex-col">
      <ScrollArea className="flex-1">
        <div className="space-y-6 px-2 py-4">
          <div className="space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2',
                    isActive
                      ? 'bg-primary text-primary-foreground shadow-sm'
                      : 'text-foreground hover:bg-accent hover:text-accent-foreground',
                    collapsed && 'justify-center'
                  )
                }
                title={collapsed ? item.name : undefined}
                onClick={onNavigate}
              >
                <item.icon className={cn('h-5 w-5 flex-shrink-0', collapsed && 'h-6 w-6')} />
                {!collapsed && <span>{item.name}</span>}
              </NavLink>
            ))}
          </div>

          <Separator className="border-border/60" />

          <SpacesTree collapsed={collapsed} />
        </div>
      </ScrollArea>
    </nav>
  );
};
