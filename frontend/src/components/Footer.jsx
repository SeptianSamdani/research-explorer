import React from 'react';

export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 mt-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-gray-600">
          
          {/* Left side text */}
          <p className="text-center md:text-left">
            © {new Date().getFullYear()} BRIN Research Topic Explorer.
          </p>
          
          {/* Right side links */}
          <div className="flex items-center gap-4">
            <a 
              href="https://www.brin.go.id"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-blue-600 transition-colors"
            >
              Official Website
            </a>

            <span className="h-4 w-px bg-gray-300"></span>

            <a 
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-blue-600 transition-colors"
            >
              GitHub Repo
            </a>
          </div>

        </div>
      </div>
    </footer>
  );
}
