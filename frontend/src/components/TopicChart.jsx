import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function TopicChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-80 text-gray-500">
        Tidak ada data topik
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={350}>
      <BarChart data={data} margin={{ top: 20, right: 20, left: 0, bottom: 80 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis 
          dataKey="name" 
          angle={-45}
          textAnchor="end"
          height={100}
          interval={0}
          tick={{ fill: '#4B5563', fontSize: 12 }}
        />
        <YAxis tick={{ fill: '#4B5563', fontSize: 12 }} />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: 'white', 
            border: '1px solid #E5E7EB',
            borderRadius: '8px',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
          }}
        />
        <Bar dataKey="publication_count" fill="#D22630" name="Jumlah Publikasi" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}