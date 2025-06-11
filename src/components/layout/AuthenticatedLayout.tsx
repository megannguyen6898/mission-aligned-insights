
import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import TopNavbar from './TopNavbar';

const AuthenticatedLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <TopNavbar />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 ml-64 p-8 pt-16">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AuthenticatedLayout;
