
import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, Upload, Reports, Users, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Dashboard', to: '/dashboard', icon: Home },
  { name: 'Upload Data', to: '/upload', icon: Upload },
  { name: 'Reports', to: '/reports', icon: Reports },
  { name: 'Investors', to: '/investors', icon: Users },
  { name: 'Settings', to: '/settings', icon: Settings },
];

const Sidebar: React.FC = () => {
  return (
    <div className="fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-gray-200 pt-16">
      <div className="flex flex-col h-full">
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  'flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                  isActive
                    ? 'bg-mega-primary text-white'
                    : 'text-gray-700 hover:text-mega-primary hover:bg-gray-50'
                )
              }
            >
              <item.icon className="mr-3 h-5 w-5" />
              {item.name}
            </NavLink>
          ))}
        </nav>
      </div>
    </div>
  );
};

export default Sidebar;
