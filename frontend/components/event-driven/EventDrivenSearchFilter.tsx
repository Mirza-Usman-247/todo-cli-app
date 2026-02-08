/**
 * Event-Driven Search Filter Component
 * Implements T067 from tasks.md
 *
 * Search and filter interface for tasks
 */
'use client';

import { useState } from 'react';
import { SearchQuery } from '@/services/event-driven-task.service';

interface EventDrivenSearchFilterProps {
  onSearch: (query: SearchQuery) => void;
  loading?: boolean;
}

const priorityOptions = [
  { value: '', label: 'All Priorities' },
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'urgent', label: 'Urgent' }
];

const sortOptions = [
  { value: 'createdAt', label: 'Created Date' },
  { value: 'updatedAt', label: 'Updated Date' },
  { value: 'dueDate', label: 'Due Date' },
  { value: 'priority', label: 'Priority' }
];

export function EventDrivenSearchFilter({
  onSearch,
  loading = false
}: EventDrivenSearchFilterProps) {
  const [keyword, setKeyword] = useState('');
  const [priority, setPriority] = useState('');
  const [tagInput, setTagInput] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<SearchQuery['sortBy']>('createdAt');
  const [ascending, setAscending] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleSearch = () => {
    const query: SearchQuery = {
      keyword: keyword.trim() || undefined,
      priority: priority || undefined,
      tags: selectedTags.length > 0 ? selectedTags : undefined,
      sortBy,
      ascending
    };

    onSearch(query);
  };

  const handleClear = () => {
    setKeyword('');
    setPriority('');
    setSelectedTags([]);
    setSortBy('createdAt');
    setAscending(false);

    // Trigger search with empty filters
    onSearch({
      sortBy: 'createdAt',
      ascending: false
    });
  };

  const handleAddTag = () => {
    const trimmedTag = tagInput.trim();
    if (trimmedTag && !selectedTags.includes(trimmedTag)) {
      setSelectedTags(prev => [...prev, trimmedTag]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setSelectedTags(prev => prev.filter(tag => tag !== tagToRemove));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (tagInput.trim()) {
        handleAddTag();
      } else {
        handleSearch();
      }
    }
  };

  const hasActiveFilters = keyword || priority || selectedTags.length > 0;

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
      {/* Search Bar */}
      <div className="p-4">
        <div className="flex gap-2">
          <div className="flex-grow relative">
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Search tasks by title or description..."
              disabled={loading}
            />
            <svg
              className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>

          <button
            onClick={handleSearch}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Searching...
              </>
            ) : (
              'Search'
            )}
          </button>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            aria-label="Toggle advanced filters"
          >
            <svg
              className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>

        {/* Active Filters Indicator */}
        {hasActiveFilters && !isExpanded && (
          <div className="mt-2 flex items-center gap-2 text-sm text-gray-600">
            <span className="font-medium">Active filters:</span>
            {keyword && <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded">Keyword</span>}
            {priority && <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded">Priority</span>}
            {selectedTags.length > 0 && (
              <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded">
                {selectedTags.length} tag{selectedTags.length > 1 ? 's' : ''}
              </span>
            )}
            <button
              onClick={handleClear}
              className="ml-auto text-red-600 hover:text-red-800 text-sm font-medium"
            >
              Clear all
            </button>
          </div>
        )}
      </div>

      {/* Advanced Filters */}
      {isExpanded && (
        <div className="px-4 pb-4 border-t border-gray-200 pt-4 space-y-4">
          {/* Priority Filter */}
          <div>
            <label htmlFor="priority-filter" className="block text-sm font-medium text-gray-700 mb-1">
              Priority
            </label>
            <select
              id="priority-filter"
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            >
              {priorityOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Tags Filter */}
          <div>
            <label htmlFor="tags-filter" className="block text-sm font-medium text-gray-700 mb-1">
              Filter by Tags
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                id="tags-filter"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={handleKeyDown}
                className="flex-grow px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Type tag and press Enter"
                disabled={loading}
              />
              <button
                type="button"
                onClick={handleAddTag}
                disabled={loading || !tagInput.trim()}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Add
              </button>
            </div>

            {/* Selected Tags */}
            {selectedTags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {selectedTags.map((tag, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-1 px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm"
                  >
                    #{tag}
                    <button
                      type="button"
                      onClick={() => handleRemoveTag(tag)}
                      disabled={loading}
                      className="text-purple-600 hover:text-purple-800"
                      aria-label={`Remove tag ${tag}`}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Sort Options */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="sort-by" className="block text-sm font-medium text-gray-700 mb-1">
                Sort By
              </label>
              <select
                id="sort-by"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SearchQuery['sortBy'])}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={loading}
              >
                {sortOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="sort-order" className="block text-sm font-medium text-gray-700 mb-1">
                Order
              </label>
              <select
                id="sort-order"
                value={ascending ? 'asc' : 'desc'}
                onChange={(e) => setAscending(e.target.value === 'asc')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={loading}
              >
                <option value="desc">Descending</option>
                <option value="asc">Ascending</option>
              </select>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 justify-end pt-2">
            <button
              onClick={handleClear}
              disabled={loading || !hasActiveFilters}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Clear Filters
            </button>
            <button
              onClick={handleSearch}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              Apply Filters
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
