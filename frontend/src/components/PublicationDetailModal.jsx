import React, { useState, useEffect } from 'react';
import { getPublicationById } from '../services/api';

export default function PublicationDetailModal({ publicationId, onClose }) {
  const [publication, setPublication] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPublication = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getPublicationById(publicationId);
        setPublication(data);
      } catch (err) {
        setError('Failed to load publication details');
        console.error('Error:', err);
      } finally {
        setLoading(false);
      }
    };

    if (publicationId) {
      fetchPublication();
    }
  }, [publicationId]);

  if (!publicationId) return null;

  return (
    <div
      className="fixed inset-0 backdrop-blur-sm bg-black/10 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Publication Details</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <div className="text-gray-600">Loading...</div>
              </div>
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
              {error}
            </div>
          ) : publication ? (
            <div className="space-y-6">
              {/* Title */}
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  {publication.title}
                </h3>
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span className="flex items-center gap-1">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                    </svg>
                    {publication.year || 'N/A'}
                  </span>
                  <span className="flex items-center gap-1">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
                    </svg>
                    {publication.source || 'Unknown'}
                  </span>
                </div>
              </div>

              {/* Abstract */}
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">Abstract</h4>
                <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                  {publication.abstract || 'No abstract available'}
                </p>
              </div>

              {/* Authors */}
              {publication.authors && publication.authors.length > 0 && (
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-3">Authors</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {publication.authors.map((author, idx) => (
                      <div key={idx} className="bg-gray-50 rounded-lg p-3">
                        <div className="font-medium text-gray-900">{author.name}</div>
                        {author.affiliation && (
                          <div className="text-sm text-gray-600 mt-1">
                            {author.affiliation}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Topics */}
              {publication.topics && publication.topics.length > 0 && (
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-3">Topics</h4>
                  <div className="flex flex-wrap gap-2">
                    {publication.topics.map((topic, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                      >
                        {topic.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* URL/DOI */}
              {publication.url && (
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">Link</h4>
                    <a
                        href={publication.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 underline break-all"
                    >
                        {publication.url}
                    </a>
                </div>
              )}
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4">
          <button
            onClick={onClose}
            className="w-full md:w-auto px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}