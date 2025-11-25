import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function TrendChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-80 text-gray-500">
        Tidak ada data tren
      </div>
    );
  }

  const yearlyData = {};
  data.forEach(item => {
    if (!yearlyData[item.year]) {
      yearlyData[item.year] = { year: item.year };
    }
    yearlyData[item.year][item.topic] = item.count;
  });

  const chartData = Object.values(yearlyData).sort((a, b) => a.year - b.year);
  const topics = [...new Set(data.map(item => item.topic))];
  const colors = ['#D22630', '#002B5C', '#059669', '#F59E0B', '#8B5CF6'];

  return (
    <ResponsiveContainer width="100%" height={350}>
      <LineChart data={chartData} margin={{ top: 20, right: 20, left: 0, bottom: 20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis dataKey="year" tick={{ fill: '#4B5563', fontSize: 12 }} />
        <YAxis tick={{ fill: '#4B5563', fontSize: 12 }} />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: 'white', 
            border: '1px solid #E5E7EB',
            borderRadius: '8px',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
          }}
        />
        <Legend wrapperStyle={{ paddingTop: '20px' }} />
        {topics.slice(0, 5).map((topic, idx) => (
          <Line
            key={topic}
            type="monotone"
            dataKey={topic}
            stroke={colors[idx % colors.length]}
            strokeWidth={2.5}
            dot={{ r: 5, strokeWidth: 2 }}
            activeDot={{ r: 7 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}