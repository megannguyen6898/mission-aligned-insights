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
}

export const WorkflowNav: React.FC<WorkflowNavProps> = ({ collapsed }) => {
  return (
    <nav className="flex flex-col h-full py-4">
      <div className="flex-1 space-y-1 px-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-colors',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2',
                isActive
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'text-foreground hover:bg-accent hover:text-accent-foreground',
                collapsed && 'justify-center'
              )
            }
            title={collapsed ? item.name : undefined}
          >
            <item.icon className={cn('h-5 w-5 flex-shrink-0', collapsed && 'h-6 w-6')} />
            {!collapsed && <span>{item.name}</span>}
          </NavLink>
        ))}
      </div>

      {/* Spaces Section Placeholder */}
      {!collapsed && (
        <div className="border-t border-border pt-4 px-4">
          <p className="text-xs font-medium text-muted-foreground mb-2">Spaces</p>
          <div className="text-sm text-muted-foreground">
            No spaces yet
          </div>
        </div>
      )}
    </nav>
  );
};
