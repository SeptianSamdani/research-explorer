import React, { useState, useEffect } from 'react';
import { getPublications } from '../services/api';
import Pagination from './Pagination';
import TableSkeleton from './TableSkeleton';
import PublicationDetailModal from './PublicationDetailModal';

export default function PublicationTable({ filters = {}, searchQuery = '' }) {
  const [publications, setPublications] = useState([]);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    total_pages: 0,
    has_next: false,
    has_prev: false
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPublicationId, setSelectedPublicationId] = useState(null);

  useEffect(() => {
    fetchPublications(1); // Reset to page 1 when filters change
  }, [filters, searchQuery]);

  const fetchPublications = async (page) => {
    setLoading(true);
    setError(null);
    
    try {
      const params = {
        page,
        per_page: 20,
        ...filters,
        ...(searchQuery && { search: searchQuery })
      };
      
      const data = await getPublications(params);
      
      setPublications(data.items || []);
      setPagination({
        page: data.page,
        per_page: data.per_page,
        total: data.total,
        total_pages: data.total_pages,
        has_next: data.has_next,
        has_prev: data.has_prev
      });
    } catch (err) {
      setError('Failed to fetch publications');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage) => {
    fetchPublications(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleRowClick = (publicationId) => {
    setSelectedPublicationId(publicationId);
  };

  if (loading) {
    return <TableSkeleton rows={10} />;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        {error}
      </div>
    );
  }

  return (
    <>
      <div className="overflow-x-auto bg-white rounded-lg shadow">
        {/* Results Info */}
        <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
          <p className="text-sm text-gray-600">
            Showing {publications.length > 0 ? ((pagination.page - 1) * pagination.per_page) + 1 : 0} to{' '}
            {Math.min(pagination.page * pagination.per_page, pagination.total)} of{' '}
            {pagination.total} results
            {searchQuery && (
              <span className="ml-2 font-medium">
                for "{searchQuery}"
              </span>
            )}
          </p>
        </div>

        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Title
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Year
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Authors
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Source
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Action
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {publications.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-12 text-center">
                  <div className="text-gray-500">
                    <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p className="mt-2 text-lg font-medium">No publications found</p>
                    {searchQuery && (
                      <p className="mt-1 text-sm">Try adjusting your search or filters</p>
                    )}
                  </div>
                </td>
              </tr>
            ) : (
              publications.map((pub) => (
                <tr 
                  key={pub.id} 
                  className="hover:bg-gray-50 transition-colors cursor-pointer"
                  onClick={() => handleRowClick(pub.id)}
                >
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900 hover:text-blue-600">
                      {pub.title}
                    </div>
                    {pub.abstract && (
                      <div className="text-sm text-gray-500 mt-1 line-clamp-2">
                        {pub.abstract.substring(0, 150)}...
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {pub.year || 'N/A'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {pub.authors && pub.authors.length > 0 ? (
                      <div className="space-y-1">
                        {pub.authors.slice(0, 2).map((author, idx) => (
                          <div key={idx} className="truncate max-w-xs">
                            {author.name}
                          </div>
                        ))}
                        {pub.authors.length > 2 && (
                          <div className="text-xs text-gray-400">
                            +{pub.authors.length - 2} more
                          </div>
                        )}
                      </div>
                    ) : (
                      'No authors'
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    <div className="truncate max-w-xs">
                      {pub.source || 'Unknown'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRowClick(pub.id);
                      }}
                      className="text-blue-600 hover:text-blue-800 font-medium"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {/* Pagination */}
        {publications.length > 0 && (
          <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
            <Pagination
              currentPage={pagination.page}
              totalPages={pagination.total_pages}
              onPageChange={handlePageChange}
              hasNext={pagination.has_next}
              hasPrev={pagination.has_prev}
            />
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selectedPublicationId && (
        <PublicationDetailModal
          publicationId={selectedPublicationId}
          onClose={() => setSelectedPublicationId(null)}
        />
      )}
    </>
  );
}