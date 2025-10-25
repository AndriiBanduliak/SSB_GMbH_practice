import React from 'react';

const Users = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
        <p className="mt-1 text-sm text-gray-600">Manage system users and permissions</p>
      </div>
      
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
        <span className="text-6xl mb-4 block">👥</span>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">User Management</h2>
        <p className="text-gray-600 mb-4">
          This feature allows administrators to manage system users, roles, and permissions.
        </p>
        <p className="text-sm text-gray-500">
          Full implementation available in the backend API at /api/v1/users
        </p>
      </div>
    </div>
  );
};

export default Users;

