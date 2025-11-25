import React, { useState, useEffect } from 'react';
import { getPublicationStats, getTopics, getTopicTrends, getPublications } from '../services/api';
import PublicationTable from '../components/PublicationTable';
import TopicChart from '../components/TopicChart';
import TrendChart from '../components/TrendChart';
import StatCard from '../components/StatCard';
import SearchBar from '../components/SearchBar';
import Footer from '../components/Footer';
import { ChevronLeft, X, ChevronRight } from 'lucide-react'; 

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalPublications: 0,
    totalAuthors: 0,
    totalTopics: 0,
  });
  const [topics, setTopics] = useState([]);
  const [trends, setTrends] = useState([]);
  const [publications, setPublications] = useState([]);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    total_pages: 0,
    has_next: false,
    has_prev: false
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedYear, setSelectedYear] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    fetchPublications(1);
  }, [searchQuery, selectedYear, selectedTopic]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, topicsData, trendsData] = await Promise.all([
       getPublicationStats(),
       getTopics(),
       getTopicTrends()
      ]);

      setStats({
        totalPublications: statsData.total_publications || 0,
        totalAuthors: statsData.total_authors || 0,
        totalTopics: statsData.total_topics || 0,
      });

      setTopics(topicsData || []);
      setTrends(trendsData || []);
      
      await fetchPublications(1);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Gagal memuat data. Pastikan backend sudah berjalan.');
    } finally {
      setLoading(false);
    }
  };

  const fetchPublications = async (page) => {
    try {
      const params = {
        page,
        per_page: 20,
        ...(selectedYear && { year: selectedYear }),
        ...(selectedTopic && { topic_id: selectedTopic }),
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
    } catch (error) {
      console.error('Error fetching publications:', error);
    }
  };

  const handlePageChange = (newPage) => {
    fetchPublications(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const clearAllFilters = () => {
    setSelectedYear('');
    setSelectedTopic('');
    setSearchQuery('');
  };

  const hasActiveFilters = selectedYear || selectedTopic || searchQuery;
  const years = Array.from({ length: 5 }, (_, i) => 2024 - i);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F4F4F4] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-[#D22630] mx-auto mb-4"></div>
          <div className="text-xl font-medium text-[#002B5C]">Memuat Dashboard...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#F4F4F4] flex items-center justify-center">
        <div className="bg-white border-2 border-red-300 rounded-lg p-8 max-w-md shadow-lg">
          <h2 className="text-xl font-bold text-[#D22630] mb-3">Error Memuat Dashboard</h2>
          <p className="text-gray-700 mb-4">{error}</p>
          <button
            onClick={fetchData}
            className="px-5 py-2.5 bg-[#D22630] text-white rounded-lg hover:bg-[#B01F28] transition-colors font-medium"
          >
            Coba Lagi
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F4F4F4]">
      {/* Header */}
      <header className="bg-white shadow-sm border-b-2 border-[#D22630]">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-[#002B5C] mb-1">
                Research Intelligence Dashboard
              </h1>
              <p className="text-gray-600">
                Badan Riset dan Inovasi Nasional
              </p>
            </div>
            <button
              onClick={fetchData}
              className="flex items-center gap-2 px-5 py-2.5 bg-[#D22630] text-white rounded-lg hover:bg-[#B01F28] transition-colors font-medium shadow-sm"
            >
              Perbarui Data
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <StatCard
            title="Total Publikasi"
            value={stats.totalPublications}
            color="red"
          />
          <StatCard
            title="Topik Riset"
            value={stats.totalTopics}
            color="blue"
          />
          <StatCard
            title="Peneliti Terdaftar"
            value={stats.totalAuthors}
            color="gray"
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-[#002B5C] mb-6 border-b-2 border-[#D22630] pb-3">
              Distribusi Topik Penelitian
            </h2>
            <TopicChart data={topics} />
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-[#002B5C] mb-6 border-b-2 border-[#D22630] pb-3">
              Tren Publikasi per Topik
            </h2>
            <TrendChart data={trends} />
          </div>
        </div>

        {/* Search & Filter Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-bold text-[#002B5C] mb-4 flex items-center gap-2">
            Pencarian & Filter
          </h2>
          
          {/* Search Bar */}
          <div className="relative mb-6">
            {/* <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" /> */}
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Cari publikasi berdasarkan judul atau abstrak..."
              className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#D22630] focus:border-transparent"
            />
          </div>

          {/* Filters */}
          <div className="flex items-start justify-between gap-4 mb-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1">
              <div>
                <label className="block text-sm font-semibold text-[#002B5C] mb-2">
                  Tahun Publikasi
                </label>
                <select
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#D22630] focus:border-transparent"
                  value={selectedYear}
                  onChange={(e) => setSelectedYear(e.target.value)}
                >
                  <option value="">Semua Tahun</option>
                  {years.map(year => (
                    <option key={year} value={year}>{year}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-[#002B5C] mb-2">
                  Topik Penelitian
                </label>
                <select
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#D22630] focus:border-transparent"
                  value={selectedTopic}
                  onChange={(e) => setSelectedTopic(e.target.value)}
                >
                  <option value="">Semua Topik</option>
                  {topics.map(topic => (
                    <option key={topic.id} value={topic.id}>
                      {topic.name} ({topic.publication_count})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {hasActiveFilters && (
              <button
                onClick={clearAllFilters}
                className="mt-7 px-4 py-2.5 text-[#D22630] border border-[#D22630] rounded-lg hover:bg-red-50 transition-colors font-medium"
              >
                Hapus Filter
              </button>
            )}
          </div>

          {/* Active Filters Display */}
          {hasActiveFilters && (
            <div className="flex flex-wrap gap-2 pt-4 border-t border-gray-200">
              {searchQuery && (
                <span className="inline-flex items-center gap-2 px-3 py-1.5 bg-[#D22630] text-white rounded-full text-sm font-medium">
                  Pencarian: "{searchQuery}"
                  <button onClick={() => setSearchQuery('')} className="hover:text-gray-200">
                    <X className="w-4 h-4" />
                  </button>
                </span>
              )}
              {selectedYear && (
                <span className="inline-flex items-center gap-2 px-3 py-1.5 bg-[#002B5C] text-white rounded-full text-sm font-medium">
                  Tahun: {selectedYear}
                  <button onClick={() => setSelectedYear('')} className="hover:text-gray-200">
                    <X className="w-4 h-4" />
                  </button>
                </span>
              )}
              {selectedTopic && (
                <span className="inline-flex items-center gap-2 px-3 py-1.5 bg-gray-600 text-white rounded-full text-sm font-medium">
                  Topik: {topics.find(t => t.id === parseInt(selectedTopic))?.name}
                  <button onClick={() => setSelectedTopic('')} className="hover:text-gray-200">
                    <X className="w-4 h-4" />
                  </button>
                </span>
              )}
            </div>
          )}
        </div>

        {/* Publications Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
            <h2 className="text-xl font-bold text-[#002B5C]">
              Daftar Publikasi
              {hasActiveFilters && (
                <span className="text-sm font-normal text-gray-600 ml-2">
                  (Hasil terfilter)
                </span>
              )}
            </h2>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-[#002B5C]">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-bold text-white uppercase tracking-wider">
                    Judul Publikasi
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-white uppercase tracking-wider">
                    Tahun
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-white uppercase tracking-wider">
                    Penulis
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-white uppercase tracking-wider">
                    Sumber
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {publications.length === 0 ? (
                  <tr>
                    <td colSpan="4" className="px-6 py-12 text-center">
                      <div className="text-gray-500">
                        <Search className="mx-auto h-12 w-12 text-gray-400 mb-3" />
                        <p className="text-lg font-medium text-[#002B5C]">Tidak ada publikasi ditemukan</p>
                        {searchQuery && (
                          <p className="mt-1 text-sm">Coba sesuaikan pencarian atau filter Anda</p>
                        )}
                      </div>
                    </td>
                  </tr>
                ) : (
                  publications.map((pub) => (
                    <tr key={pub.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="text-sm font-semibold text-[#1F1F1F]">{pub.title}</div>
                        {pub.abstract && (
                          <div className="text-sm text-gray-500 mt-1 line-clamp-2">
                            {pub.abstract.substring(0, 150)}...
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 font-medium">
                        {pub.year || 'N/A'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-700">
                        {pub.authors && pub.authors.length > 0 ? (
                          <div className="space-y-1">
                            {pub.authors.slice(0, 2).map((author, idx) => (
                              <div key={idx} className="truncate max-w-xs">
                                {author.name}
                              </div>
                            ))}
                            {pub.authors.length > 2 && (
                              <div className="text-xs text-gray-400">
                                +{pub.authors.length - 2} lainnya
                              </div>
                            )}
                          </div>
                        ) : (
                          'Tidak ada penulis'
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-700">
                        <div className="truncate max-w-xs">
                          {pub.source || 'Unknown'}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Menampilkan <span className="font-semibold">{publications.length > 0 ? ((pagination.page - 1) * pagination.per_page) + 1 : 0}</span> - <span className="font-semibold">{Math.min(pagination.page * pagination.per_page, pagination.total)}</span> dari <span className="font-semibold">{pagination.total.toLocaleString()}</span> publikasi
            </div>
            <div className="flex gap-2">
              <button 
                onClick={() => handlePageChange(pagination.page - 1)}
                disabled={!pagination.has_prev}
                className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                  pagination.has_prev 
                    ? 'bg-[#D22630] text-white hover:bg-[#B01F28]' 
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                }`}
              >
                <ChevronLeft className="w-5 h-5" />
                Sebelumnya
              </button>
              <div className="flex items-center gap-2">
                <span className="px-4 py-2 bg-[#002B5C] text-white rounded-lg font-semibold">
                  {pagination.page}
                </span>
                <span className="text-gray-600">dari</span>
                <span className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-semibold">
                  {pagination.total_pages}
                </span>
              </div>
              <button 
                onClick={() => handlePageChange(pagination.page + 1)}
                disabled={!pagination.has_next}
                className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                  pagination.has_next 
                    ? 'bg-[#D22630] text-white hover:bg-[#B01F28]' 
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                }`}
              >
                Selanjutnya
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <p>© 2024 Badan Riset dan Inovasi Nasional</p>
            <div className="flex items-center gap-4">
              <a href="https://www.brin.go.id" target="_blank" rel="noopener noreferrer" className="hover:text-[#D22630] transition-colors font-medium">
                Website Resmi
              </a>
              <span className="h-4 w-px bg-gray-300"></span>
              <a href="#" className="hover:text-[#D22630] transition-colors font-medium">
                Dokumentasi
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}