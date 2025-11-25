import React from 'react';

export default function StatCard({ title, value, icon, color = 'blue' }) {
  const colorClasses = {
    red: 'bg-red-50 text-[#D22630]',
    blue: 'bg-blue-50 text-[#002B5C]',
    gray: 'bg-gray-100 text-gray-700'
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-4xl font-bold text-[#1F1F1F]">{value.toLocaleString()}</p>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          {icon ? React.createElement(icon, { className: 'w-7 h-7' }) : null}
        </div>
      </div>
    </div>
  );
}