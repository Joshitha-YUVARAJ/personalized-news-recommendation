import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "../lib/api";
import type { RecItem } from "../types";
import ArticleCard from '../components/ArticleCard';
import { useState } from 'react';
import { motion } from 'framer-motion';
import { FiSearch, FiTrendingUp, FiArrowLeft, FiDownload } from 'react-icons/fi';
import {
  GlassCard,
  FormContainer,
  SearchContainer,
  SearchInput,
  SearchButton,
  LoadingCard,
  LoadingTextPlaceholder,
  PDFExportButton,
  EmptyStateContainer,
  EmptyStateIcon,
  EmptyStateTitle,
  EmptyStateMessage,
  SectionHeader,
  SectionTitle,
  SectionSubtitle,
  SecondaryButton,
} from '../components/ui/StyledComponents';

export default function Home() {
  const { data: trending, isLoading: trendingLoading } = useQuery({
    queryKey: ['trending'],
    queryFn: async () => {
      console.log('🔄 Fetching trending articles...');
      const result = await api.trending(20);
      console.log('✅ Trending articles received:', result?.length || 0, 'articles');
      console.log('📰 First article:', result?.[0]?.title);
      return result;
    },
  });

  const [q, setQ] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [results, setResults] = useState<RecItem[]>([]);
  const [categories, setCategories] = useState<Record<string, number>>({});

  const search = useMutation({
    mutationFn: async () => {
      const items = await api.search(q, 20, selectedCategory || undefined);
      setResults(items);
      const counts = items.reduce((acc, r) => {
        const c = (r.category || "Unknown").trim();
        acc[c] = (acc[c] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);
      setCategories(counts);
      return items;
    },
    onSuccess: () => setQ(''),
  });

  const exportMutation = useMutation({
    mutationFn: async (items: RecItem[]) => {
      console.log('Exporting', items.length, 'articles to PDF...');
      
      // Dynamic import to avoid bundle size issues
      const jsPDF = (await import('jspdf')).default;
      const doc = new jsPDF();
      
      // PDF title
      doc.setFontSize(20);
      doc.text('Smart News Recommendations', 20, 30);
      
      // Add metadata
      doc.setFontSize(12);
      doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 20, 45);
      doc.text(`Total Articles: ${items.length}`, 20, 55);
      
      let yPosition = 70;
      const pageHeight = doc.internal.pageSize.height;
      const margin = 20;
      const lineHeight = 7;
      
      items.forEach((item, index) => {
        // Check if we need a new page
        if (yPosition > pageHeight - 50) {
          doc.addPage();
          yPosition = 30;
        }
        
        // Article number and title
        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        const title = `${index + 1}. ${item.title}`;
        const titleLines = doc.splitTextToSize(title, 170);
        doc.text(titleLines, margin, yPosition);
        yPosition += titleLines.length * lineHeight + 3;
        
        // Category
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(100);
        doc.text(`Category: ${item.category || 'Unknown'}`, margin, yPosition);
        yPosition += lineHeight;
        
        // Abstract/Summary
        if (item.abstract) {
          doc.setTextColor(0);
          const abstractLines = doc.splitTextToSize(item.abstract, 170);
          doc.text(abstractLines, margin, yPosition);
          yPosition += abstractLines.length * lineHeight + 10;
        } else {
          yPosition += 10;
        }
      });
      
      // Save the PDF
      const filename = `news-recommendations-${new Date().toISOString().split('T')[0]}.pdf`;
      doc.save(filename);
      
      console.log('PDF exported successfully:', filename);
    },
    onError: (error) => {
      console.error('PDF export failed:', error);
      alert('Failed to export PDF. Please try again.');
    },
  });

  const items: RecItem[] = search.data ?? (results.length > 0 ? results : trending) ?? [];
  
  // Debug logging (can be removed in production)
  // console.log('🐛 Debug - trending data:', trending?.length || 0, 'articles');
  const isSearchActive = search.data !== undefined;

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  };

  const LoadingSkeleton = () => (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
        gap: '2rem',
        padding: '2rem',
      }}
    >
      {[...Array(6)].map((_, index) => (
        <LoadingCard key={index}>
          <div style={{ padding: '1.5rem' }}>
            <LoadingTextPlaceholder
              style={{ height: '1rem', width: '25%', marginBottom: '1rem' }}
            />
            <LoadingTextPlaceholder
              style={{ height: '1.5rem', marginBottom: '1rem' }}
            />
            <LoadingTextPlaceholder
              style={{ height: '1rem', marginBottom: '0.5rem' }}
            />
            <LoadingTextPlaceholder style={{ height: '1rem', width: '60%' }} />
          </div>
        </LoadingCard>
      ))}
    </div>
  );

  return (
    <motion.div variants={containerVariants} initial="hidden" animate="visible">
      {/* Hero Section */}
      <GlassCard
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      >
        <FormContainer style={{ textAlign: 'center', padding: '3rem 2rem' }}>
          <SectionHeader>
            <SectionTitle style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
              Discover News That Matters
            </SectionTitle>
            <SectionSubtitle
              style={{ fontSize: '1.25rem', marginBottom: '2rem' }}
            >
              AI-powered recommendations from thousands of sources
            </SectionSubtitle>
          </SectionHeader>

          {/* Search Bar */}
          <SearchContainer style={{ maxWidth: '600px', margin: '0 auto' }}>
            <div style={{ position: 'relative' }}>
              <SearchInput
                placeholder="Search for news topics, keywords, or categories (try: sports, health, finance)..."
                value={q}
                onChange={e => setQ(e.target.value)}
                onKeyPress={e =>
                  e.key === 'Enter' && q.trim() && search.mutate()
                }
                whileFocus={{ scale: 1.02 }}
                transition={{ duration: 0.2 }}
              />
              <FiSearch
                style={{
                  position: 'absolute',
                  right: '1rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'rgba(255, 255, 255, 0.6)',
                  fontSize: '1.2rem',
                }}
              />
            </div>

            {/* Category Selector */}
            {Object.keys(categories).length > 0 && (
              <select
                value={selectedCategory}
                onChange={e => setSelectedCategory(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem',
                  marginTop: '1rem',
                  background: 'rgba(255, 255, 255, 0.1)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '12px',
                  color: 'white',
                  fontSize: '1rem',
                  outline: 'none',
                  cursor: 'pointer',
                }}
              >
                <option
                  value=""
                  style={{ background: '#1a1a1a', color: 'white' }}
                >
                  All Categories
                </option>
                {Object.keys(categories).map(category => (
                  <option
                    key={category}
                    value={category}
                    style={{ background: '#1a1a1a', color: 'white' }}
                  >
                    {category.charAt(0).toUpperCase() + category.slice(1)} ({categories[category]})
                  </option>
                ))}
              </select>
            )}

            {/* Quick Category Tags */}
            <div
              style={{
                display: 'flex',
                gap: '0.5rem',
                marginTop: '1rem',
                flexWrap: 'wrap',
                justifyContent: 'center',
              }}
            >
              {['sports', 'health', 'finance', 'news', 'entertainment'].map(
                tag => (
                  <button
                    key={tag}
                    onClick={() => {
                      setQ(tag);
                      setSelectedCategory(tag);
                      setTimeout(() => search.mutate(), 100);
                    }}
                    style={{
                      padding: '0.5rem 1rem',
                      background:
                        selectedCategory === tag
                          ? 'rgba(255, 255, 255, 0.2)'
                          : 'rgba(255, 255, 255, 0.1)',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      borderRadius: '20px',
                      color: 'white',
                      fontSize: '0.875rem',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                    }}
                    onMouseEnter={e => {
                      e.currentTarget.style.background =
                        'rgba(255, 255, 255, 0.2)';
                      e.currentTarget.style.transform = 'scale(1.05)';
                    }}
                    onMouseLeave={e => {
                      e.currentTarget.style.background =
                        selectedCategory === tag
                          ? 'rgba(255, 255, 255, 0.2)'
                          : 'rgba(255, 255, 255, 0.1)';
                      e.currentTarget.style.transform = 'scale(1)';
                    }}
                  >
                    #{tag}
                  </button>
                )
              )}
            </div>

            <SearchButton
              onClick={() => q.trim() && search.mutate()}
              disabled={!q.trim() || search.isPending}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.98 }}
            >
              {search.isPending ? (
                <>
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{
                      duration: 1,
                      repeat: Infinity,
                      ease: 'linear',
                    }}
                    style={{ display: 'inline-block', marginRight: '0.5rem' }}
                  >
                    ⟳
                  </motion.div>
                  Searching...
                </>
              ) : (
                <>
                  <FiSearch style={{ marginRight: '0.5rem' }} />
                  Search
                </>
              )}
            </SearchButton>
          </SearchContainer>

          <div style={{ display: 'flex', justifyContent: 'center', marginTop: '1rem' }}>
            <PDFExportButton
              onClick={() => exportMutation.mutate(items ?? [])}
              disabled={!items || items.length === 0 || exportMutation.isPending}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <FiDownload />
              {exportMutation.isPending ? 'Exporting...' : 'Export PDF'}
            </PDFExportButton>
          </div>
        </FormContainer>
      </GlassCard>

      {/* Results Section */}
      <GlassCard
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut', delay: 0.2 }}
        style={{ marginTop: '2rem' }}
      >
        <FormContainer>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '2rem',
            }}
          >
            <SectionHeader style={{ textAlign: 'left', margin: 0 }}>
              <SectionTitle
                style={{
                  fontSize: '2rem',
                  marginBottom: '0.5rem',
                  display: 'flex',
                  alignItems: 'center',
                }}
              >
                <FiTrendingUp style={{ marginRight: '0.5rem' }} />
                {isSearchActive ? 'Search Results' : 'Trending Stories'}
              </SectionTitle>
            </SectionHeader>

            {isSearchActive && (
              <SecondaryButton
                onClick={() => search.reset()}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
              >
                <FiArrowLeft style={{ marginRight: '0.5rem' }} />
                Back to Trending
              </SecondaryButton>
            )}
          </div>

          {/* Loading State */}
          {(trendingLoading || search.isPending) && <LoadingSkeleton />}

          {/* Articles Grid */}
          {!trendingLoading && !search.isPending && (
            <>
              {items.length > 0 ? (
                <motion.div
                  style={{
                    display: 'grid',
                    gridTemplateColumns:
                      'repeat(auto-fill, minmax(350px, 1fr))',
                    gap: '2rem',
                    padding: '1rem',
                  }}
                  variants={containerVariants}
                  initial="hidden"
                  animate="visible"
                >
                  {items.map((item, idx) => (
                    <motion.div
                      key={`${item.item_id}-${idx}`}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5, delay: idx * 0.1 }}
                    >
                      <ArticleCard item={item} />
                    </motion.div>
                  ))}
                </motion.div>
              ) : (
                <EmptyStateContainer>
                  <EmptyStateIcon
                    animate={{
                      scale: [1, 1.1, 1],
                      rotate: [0, 5, -5, 0],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: 'easeInOut',
                    }}
                  >
                    📰
                  </EmptyStateIcon>
                  <EmptyStateTitle>
                    {isSearchActive
                      ? 'No articles found'
                      : 'No trending articles'}
                  </EmptyStateTitle>
                  <EmptyStateMessage>
                    {isSearchActive
                      ? 'Try different keywords or browse trending stories.'
                      : 'Check back later for the latest trends.'}
                  </EmptyStateMessage>
                </EmptyStateContainer>
              )}
            </>
          )}
        </FormContainer>
      </GlassCard>
    </motion.div>
  );
}
