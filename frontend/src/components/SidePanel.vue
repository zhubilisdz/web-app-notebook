<template>
  <div class="side-panel">
    <div class="panel-header">
      <h3>搜索与筛选</h3>
      <button 
        class="panel-toggle"
        @click="togglePanel"
        :class="{ collapsed: isCollapsed }"
      >
        {{ isCollapsed ? '展开' : '收起' }}
      </button>
    </div>
    
    <div class="panel-content" :class="{ collapsed: isCollapsed }">
      <!-- 搜索框 -->
      <div class="search-section">
        <div class="search-input-wrapper">
          <input 
            v-model="searchQuery"
            class="search-input"
            placeholder="搜索笔记内容..."
            @input="onSearchInput"
          />
          <button 
            v-if="searchQuery"
            class="clear-search"
            @click="clearSearch"
          >
            ×
          </button>
        </div>
        
        <!-- 导入导出功能 -->
        <div class="import-export-section">
          <h4>📁 导入导出</h4>
          
          <div class="export-controls">
            <h5>导出笔记</h5>
            <div class="export-format-selector">
              <label class="format-option">
                <input type="radio" v-model="exportFormat" value="json" />
                <span>JSON</span>
              </label>
              <label class="format-option">
                <input type="radio" v-model="exportFormat" value="markdown" />
                <span>Markdown</span>
              </label>
              <label class="format-option">
                <input type="radio" v-model="exportFormat" value="txt" />
                <span>文本</span>
              </label>
            </div>
            <button 
              class="btn-export" 
              @click="exportNotes"
              :disabled="isExporting"
            >
              <span v-if="isExporting" class="loading-spinner"></span>
              {{ isExporting ? '导出中...' : '📤 导出笔记' }}
            </button>
          </div>
          
          <div class="import-controls">
            <h5>导入笔记</h5>
            <div class="import-options">
              <div class="merge-mode-selector">
                <label class="merge-option">
                  <input type="radio" v-model="importMergeMode" value="add" />
                  <span>添加新笔记</span>
                </label>
                <label class="merge-option">
                  <input type="radio" v-model="importMergeMode" value="replace" />
                  <span>替换重复</span>
                </label>
                <label class="merge-option">
                  <input type="radio" v-model="importMergeMode" value="skip" />
                  <span>跳过重复</span>
                </label>
              </div>
              
              <div class="file-upload-area">
                <input 
                  ref="fileInput"
                  type="file" 
                  accept=".json,.md,.txt"
                  @change="handleFileSelect"
                  style="display: none;"
                />
                <button 
                  class="btn-select-file"
                  @click="$refs.fileInput.click()"
                >
                  📁 选择文件
                </button>
                
                <div v-if="selectedFile" class="selected-file-info">
                  <span class="file-name">{{ selectedFile.name }}</span>
                  <span class="file-size">({{ formatFileSize(selectedFile.size) }})</span>
                  <button class="btn-clear-file" @click="clearSelectedFile">×</button>
                </div>
              </div>
              
              <button 
                class="btn-import"
                @click="importNotes"
                :disabled="!selectedFile || isImporting"
              >
                <span v-if="isImporting" class="loading-spinner"></span>
                {{ isImporting ? '导入中...' : '📥 导入笔记' }}
              </button>
            </div>
          </div>
          
          <!-- 导入导出状态提示 -->
          <div v-if="importExportStatus" class="import-export-status" :class="importExportStatus.type">
            <span class="status-icon">{{ importExportStatus.icon }}</span>
            <span class="status-message">{{ importExportStatus.message }}</span>
          </div>
        </div>

        <!-- 分类管理功能 -->
        <div class="category-management-section">
          <h4>📁 分类管理</h4>
          
          <div class="category-controls">
            <button 
              class="btn-category-manager"
              @click="showCategoryManager = !showCategoryManager"
            >
              <span class="btn-icon">🗂️</span>
              {{ showCategoryManager ? '隐藏分类管理' : '管理分类' }}
            </button>
            
            <div v-if="categories.length > 0" class="category-filter">
              <h5>按分类筛选</h5>
              <div class="category-filter-list">
                <button 
                  class="category-filter-item"
                  :class="{ active: selectedCategoryId === null }"
                  @click="filterByCategory(null)"
                >
                  <span class="category-icon">📋</span>
                  <span class="category-name">全部笔记</span>
                  <span class="note-count">({{ totalNotes }})</span>
                </button>
                
                <button 
                  v-for="category in categories"
                  :key="category.id"
                  class="category-filter-item"
                  :class="{ active: selectedCategoryId === category.id }"
                  @click="filterByCategory(category.id)"
                >
                  <span class="category-icon">{{ category.icon }}</span>
                  <span class="category-name">{{ category.name }}</span>
                  <span class="note-count">({{ category.note_count || 0 }})</span>
                </button>
              </div>
            </div>
            
            <div v-else class="no-categories-hint">
              <p>还没有分类，创建分类来更好地组织笔记</p>
            </div>
          </div>
        </div>

        <div class="semantic-search">
          <div class="search-input-group">
            <input 
              v-model="semanticQuery" 
              @keyup.enter="performSemanticSearch"
              @input="onSemanticInput"
              type="text" 
              placeholder="智能搜索（支持自然语言描述）..."
              class="search-input semantic-input"
            />
            <div class="search-suggestions" v-if="searchSuggestions.length > 0">
              <div 
                v-for="suggestion in searchSuggestions" 
                :key="suggestion"
                @click="selectSuggestion(suggestion)"
                class="suggestion-item"
              >
                {{ suggestion }}
              </div>
            </div>
          </div>
          <button 
            @click="performSemanticSearch" 
            :disabled="!semanticQuery.trim() || isSearching"
            class="btn btn-search"
          >
            <span v-if="isSearching" class="loading-spinner">⟳</span>
            {{ isSearching ? '搜索中...' : '🔍 智能搜索' }}
          </button>
        </div>
        
        <!-- 搜索历史 -->
        <div v-if="searchHistory.length > 0" class="search-history">
          <h5>搜索历史</h5>
          <div class="history-items">
            <span 
              v-for="(item, index) in searchHistory.slice(0, 5)" 
              :key="index"
              @click="selectHistoryItem(item)"
              class="history-item"
            >
              {{ item }}
            </span>
          </div>
          <button @click="clearSearchHistory" class="btn-clear-history">清除历史</button>
        </div>
        
        <!-- 语义搜索结果 -->
        <div v-if="semanticResults.length > 0" class="semantic-results">
          <div class="results-header">
            <h4>🎯 搜索结果</h4>
            <div class="results-info">
              <span class="results-count">{{ semanticResults.length }} 条结果</span>
              <span class="search-time" v-if="searchTime">{{ searchTime }}ms</span>
            </div>
          </div>
          
          <div class="results-container">
            <div 
              v-for="result in semanticResults" 
              :key="result.id"
              @click="$emit('select-note', result)"
              class="search-result-item"
              :class="{ 'high-relevance': result.relevance_score >= 15 }"
            >
              <div class="result-header">
                <div class="result-title">{{ result.title }}</div>
                <div class="result-score-badge" :class="getScoreClass(result.relevance_score)">
                  {{ getScoreText(result.relevance_score) }}
                </div>
              </div>
              
              <div class="result-snippet" v-html="highlightText(result.snippet, semanticQuery)"></div>
              
              <div class="result-meta">
                <span class="result-date">{{ formatDate(result.updated_at) }}</span>
                <div class="result-tags" v-if="result.tags.length > 0">
                  <span 
                    v-for="tag in result.tags.slice(0, 3)" 
                    :key="tag"
                    class="tag-chip"
                  >
                    {{ tag }}
                  </span>
                  <span v-if="result.tags.length > 3" class="more-tags">
                    +{{ result.tags.length - 3 }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="results-actions">
            <button @click="clearSemanticResults" class="btn btn-clear">清除结果</button>
            <button @click="exportResults" class="btn btn-export">导出结果</button>
          </div>
        </div>
        
        <!-- 搜索状态提示 -->
        <div v-if="searchStatus" class="search-status" :class="searchStatus.type">
          <span class="status-icon">{{ searchStatus.icon }}</span>
          <span class="status-text">{{ searchStatus.message }}</span>
        </div>
        
        <div class="search-options">
          <label class="checkbox-label">
            <input 
              v-model="searchOptions.includeTitle"
              type="checkbox"
              @change="onSearchOptionsChange"
            />
            搜索标题
          </label>
          
          <label class="checkbox-label">
            <input 
              v-model="searchOptions.includeContent"
              type="checkbox"
              @change="onSearchOptionsChange"
            />
            搜索内容
          </label>
          
          <label class="checkbox-label">
            <input 
              v-model="searchOptions.includeTags"
              type="checkbox"
              @change="onSearchOptionsChange"
            />
            搜索标签
          </label>
        </div>
      </div>
      
      <!-- 标签筛选 -->
      <div class="filter-section">
        <h4>按标签筛选</h4>
        
        <div class="tags-filter">
          <button 
            class="tag-filter"
            :class="{ active: selectedTags.length === 0 }"
            @click="clearTagFilter"
          >
            全部
          </button>
          
          <button 
            v-for="tag in availableTags"
            :key="tag.name"
            class="tag-filter"
            :class="{ active: selectedTags.includes(tag.name) }"
            @click="toggleTag(tag.name)"
          >
            {{ tag.name }}
            <span class="tag-count">({{ tag.count }})</span>
          </button>
        </div>
      </div>
      
      <!-- 排序选项 -->
      <div class="sort-section">
        <h4>排序方式</h4>
        
        <div class="sort-options">
          <label class="radio-label">
            <input 
              v-model="sortBy"
              type="radio"
              value="created_desc"
              @change="onSortChange"
            />
            创建时间（新到旧）
          </label>
          
          <label class="radio-label">
            <input 
              v-model="sortBy"
              type="radio"
              value="created_asc"
              @change="onSortChange"
            />
            创建时间（旧到新）
          </label>
          
          <label class="radio-label">
            <input 
              v-model="sortBy"
              type="radio"
              value="updated_desc"
              @change="onSortChange"
            />
            修改时间（新到旧）
          </label>
          
          <label class="radio-label">
            <input 
              v-model="sortBy"
              type="radio"
              value="title_asc"
              @change="onSortChange"
            />
            标题（A-Z）
          </label>
        </div>
      </div>
      
      <!-- 统计信息 -->
      <div class="stats-section">
        <h4>统计信息</h4>
        
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-label">总笔记数</span>
            <span class="stat-value">{{ totalNotes }}</span>
          </div>
          
          <div class="stat-item">
            <span class="stat-label">总标签数</span>
            <span class="stat-value">{{ totalTags }}</span>
          </div>
          
          <div class="stat-item">
            <span class="stat-label">筛选结果</span>
            <span class="stat-value">{{ filteredCount }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SidePanel',
  props: {
    notes: {
      type: Array,
      default: () => []
    },
    filteredCount: {
      type: Number,
      default: 0
    }
  },
  emits: ['search-change', 'filter-change', 'sort-change', 'category-filter', 'show-category-manager'],
  data() {
    return {
      isCollapsed: false,
      searchQuery: '',
      searchOptions: {
        includeTitle: true,
        includeContent: true,
        includeTags: true
      },
      selectedTags: [],
      sortBy: 'created_desc',
      searchTimer: null,
      semanticQuery: '',
      semanticResults: [],
      isSearching: false,
      searchSuggestions: [],
      searchHistory: [],
      searchTime: null,
      searchStatus: null,
      suggestionTimer: null,
      // 导入导出相关数据
      exportFormat: 'json',
      importMergeMode: 'add',
      selectedFile: null,
      isExporting: false,
      isImporting: false,
      importExportStatus: null,
      // 分类管理相关数据
      categories: [],
      selectedCategoryId: null,
      showCategoryManager: false
    };
  },
  computed: {
    availableTags() {
      const tagCounts = {};
      
      this.notes.forEach(note => {
        if (note.tags && Array.isArray(note.tags)) {
          note.tags.forEach(tag => {
            tagCounts[tag] = (tagCounts[tag] || 0) + 1;
          });
        }
      });
      
      return Object.entries(tagCounts)
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count);
    },
    
    totalNotes() {
      return this.notes.length;
    },
    
    totalTags() {
      return this.availableTags.length;
    }
  },
  methods: {
    togglePanel() {
      this.isCollapsed = !this.isCollapsed;
    },
    
    onSearchInput() {
      // 防抖搜索
      if (this.searchTimer) {
        clearTimeout(this.searchTimer);
      }
      
      this.searchTimer = setTimeout(() => {
        this.emitSearchChange();
      }, 300);
    },
    
    clearSearch() {
      this.searchQuery = '';
      this.emitSearchChange();
    },
    
    onSearchOptionsChange() {
      this.emitSearchChange();
    },
    
    emitSearchChange() {
      this.$emit('search-change', {
        query: this.searchQuery,
        options: { ...this.searchOptions }
      });
    },
    
    toggleTag(tagName) {
      const index = this.selectedTags.indexOf(tagName);
      if (index > -1) {
        this.selectedTags.splice(index, 1);
      } else {
        this.selectedTags.push(tagName);
      }
      
      this.emitFilterChange();
    },
    
    clearTagFilter() {
      this.selectedTags = [];
      this.emitFilterChange();
    },
    
    emitFilterChange() {
      this.$emit('filter-change', {
        tags: [...this.selectedTags]
      });
    },
    
    onSortChange() {
      this.$emit('sort-change', this.sortBy);
    },
    
    async performSemanticSearch() {
      if (!this.semanticQuery.trim()) return;
      
      const startTime = Date.now();
      this.isSearching = true;
      this.searchStatus = {
        type: 'info',
        icon: '🔍',
        message: '正在搜索中...'
      };
      
      try {
        const response = await fetch('http://localhost:5000/api/search/semantic', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            query: this.semanticQuery
          })
        });
        
        const data = await response.json();
        this.searchTime = Date.now() - startTime;
        
        if (data.success) {
          this.semanticResults = data.results;
          this.addToSearchHistory(this.semanticQuery);
          
          if (data.results.length === 0) {
            this.searchStatus = {
              type: 'warning',
              icon: '😔',
              message: '未找到相关结果，试试其他关键词吧'
            };
          } else {
            this.searchStatus = {
              type: 'success',
              icon: '✅',
              message: `找到 ${data.results.length} 条相关结果`
            };
          }
        } else {
          this.searchStatus = {
            type: 'error',
            icon: '❌',
            message: '搜索失败: ' + (data.error || '未知错误')
          };
        }
      } catch (error) {
        console.error('语义搜索错误:', error);
        this.searchStatus = {
          type: 'error',
          icon: '🚫',
          message: '网络连接失败，请检查网络设置'
        };
      } finally {
        this.isSearching = false;
        // 3秒后清除状态提示
        setTimeout(() => {
          this.searchStatus = null;
        }, 3000);
      }
    },
    
    clearSemanticResults() {
      this.semanticResults = [];
      this.semanticQuery = '';
      this.searchStatus = null;
      this.searchTime = null;
    },
    
    // 新增的搜索功能方法
    onSemanticInput() {
      // 清除之前的定时器
      if (this.suggestionTimer) {
        clearTimeout(this.suggestionTimer);
      }
      
      // 延迟生成搜索建议
      this.suggestionTimer = setTimeout(() => {
        this.generateSearchSuggestions();
      }, 300);
    },
    
    generateSearchSuggestions() {
      if (!this.semanticQuery.trim() || this.semanticQuery.length < 2) {
        this.searchSuggestions = [];
        return;
      }
      
      const suggestions = [];
      const query = this.semanticQuery.toLowerCase();
      
      // 基于现有笔记标题生成建议
      this.notes.forEach(note => {
        if (note.title && note.title.toLowerCase().includes(query)) {
          const suggestion = note.title;
          if (!suggestions.includes(suggestion) && suggestions.length < 5) {
            suggestions.push(suggestion);
          }
        }
      });
      
      // 基于标签生成建议
      this.availableTags.forEach(tag => {
        if (tag.name.toLowerCase().includes(query)) {
          const suggestion = `标签: ${tag.name}`;
          if (!suggestions.includes(suggestion) && suggestions.length < 5) {
            suggestions.push(suggestion);
          }
        }
      });
      
      // 添加一些常用搜索模板
      const templates = [
        `关于"${this.semanticQuery}"的笔记`,
        `包含"${this.semanticQuery}"的内容`,
        `"${this.semanticQuery}"相关资料`
      ];
      
      templates.forEach(template => {
        if (suggestions.length < 5) {
          suggestions.push(template);
        }
      });
      
      this.searchSuggestions = suggestions;
    },
    
    selectSuggestion(suggestion) {
      this.semanticQuery = suggestion.replace(/^标签: /, '');
      this.searchSuggestions = [];
      this.performSemanticSearch();
    },
    
    addToSearchHistory(query) {
      if (!query.trim()) return;
      
      // 移除重复项
      const index = this.searchHistory.indexOf(query);
      if (index > -1) {
        this.searchHistory.splice(index, 1);
      }
      
      // 添加到开头
      this.searchHistory.unshift(query);
      
      // 限制历史记录数量
      if (this.searchHistory.length > 10) {
        this.searchHistory = this.searchHistory.slice(0, 10);
      }
      
      // 保存到本地存储
      localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory));
    },
    
    selectHistoryItem(item) {
      this.semanticQuery = item;
      this.performSemanticSearch();
    },
    
    clearSearchHistory() {
      this.searchHistory = [];
      localStorage.removeItem('searchHistory');
    },
    
    // 结果处理方法
    getScoreClass(score) {
      if (score >= 20) return 'score-excellent';
      if (score >= 15) return 'score-good';
      if (score >= 10) return 'score-fair';
      return 'score-low';
    },
    
    getScoreText(score) {
      if (score >= 20) return '极高';
      if (score >= 15) return '高';
      if (score >= 10) return '中';
      return '低';
    },
    
    highlightText(text, query) {
      if (!text || !query) return text;
      
      const words = query.toLowerCase().split(' ').filter(word => word.length > 0);
      let highlightedText = text;
      
      words.forEach(word => {
        const regex = new RegExp(`(${word})`, 'gi');
        highlightedText = highlightedText.replace(regex, '<mark>$1</mark>');
      });
      
      return highlightedText;
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      const now = new Date();
      const diffTime = Math.abs(now - date);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays === 1) return '今天';
      if (diffDays === 2) return '昨天';
      if (diffDays <= 7) return `${diffDays}天前`;
      
      return date.toLocaleDateString('zh-CN', { 
        month: 'short', 
        day: 'numeric' 
      });
    },
    
    exportResults() {
      if (this.semanticResults.length === 0) return;
      
      const exportData = {
        query: this.semanticQuery,
        searchTime: this.searchTime,
        resultCount: this.semanticResults.length,
        results: this.semanticResults.map(result => ({
          title: result.title,
          snippet: result.snippet,
          tags: result.tags,
          relevanceScore: result.relevance_score,
          updatedAt: result.updated_at
        }))
      };
      
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `搜索结果_${this.semanticQuery}_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    },
    
    // 导入导出功能方法
    async exportNotes() {
      if (this.notes.length === 0) {
        this.showImportExportStatus('warning', '⚠️', '没有笔记可以导出');
        return;
      }
      
      this.isExporting = true;
      this.showImportExportStatus('info', '📤', '正在导出笔记...');
      
      try {
        const response = await fetch('http://localhost:5000/api/notes/export', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            format: this.exportFormat
          })
        });
        
        if (!response.ok) {
          throw new Error(`导出失败: ${response.status}`);
        }
        
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        
        const timestamp = new Date().toISOString().split('T')[0];
        const extension = this.exportFormat === 'json' ? 'json' : 
                         this.exportFormat === 'markdown' ? 'md' : 'txt';
        a.download = `笔记导出_${timestamp}.${extension}`;
        
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showImportExportStatus('success', '✅', `成功导出 ${this.notes.length} 条笔记`);
      } catch (error) {
        console.error('导出笔记失败:', error);
        this.showImportExportStatus('error', '❌', '导出失败: ' + error.message);
      } finally {
        this.isExporting = false;
      }
    },
    
    handleFileSelect(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedFile = file;
        this.showImportExportStatus('info', '📁', `已选择文件: ${file.name}`);
      }
    },
    
    clearSelectedFile() {
      this.selectedFile = null;
      this.$refs.fileInput.value = '';
      this.importExportStatus = null;
    },
    
    async importNotes() {
      if (!this.selectedFile) {
        this.showImportExportStatus('warning', '⚠️', '请先选择要导入的文件');
        return;
      }
      
      this.isImporting = true;
      this.showImportExportStatus('info', '📥', '正在导入笔记...');
      
      try {
        const formData = new FormData();
        formData.append('file', this.selectedFile);
        formData.append('merge_mode', this.importMergeMode);
        
        const response = await fetch('http://localhost:5000/api/notes/import', {
          method: 'POST',
          body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
          this.showImportExportStatus('success', '✅', 
            `导入成功: 新增 ${data.stats.added} 条，更新 ${data.stats.updated} 条，跳过 ${data.stats.skipped} 条`);
          
          // 触发笔记列表刷新
          this.$emit('notes-imported', data.stats);
          
          // 清除选中的文件
          this.clearSelectedFile();
        } else {
          this.showImportExportStatus('error', '❌', '导入失败: ' + (data.error || '未知错误'));
        }
      } catch (error) {
        console.error('导入笔记失败:', error);
        this.showImportExportStatus('error', '❌', '导入失败: ' + error.message);
      } finally {
        this.isImporting = false;
      }
    },
    
    formatFileSize(bytes) {
      if (bytes === 0) return '0 B';
      const k = 1024;
      const sizes = ['B', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    showImportExportStatus(type, icon, message) {
      this.importExportStatus = { type, icon, message };
      
      // 3秒后自动清除状态
      setTimeout(() => {
        this.importExportStatus = null;
      }, 3000);
    },
    
    // 分类管理相关方法
    async loadCategories() {
      try {
        const response = await fetch('http://localhost:5000/api/categories');
        const result = await response.json();
        if (response.ok) {
          this.categories = result;
        }
      } catch (error) {
        console.error('获取分类列表失败:', error);
      }
    },
    
    filterByCategory(categoryId) {
      this.selectedCategoryId = categoryId;
      this.$emit('category-filter', categoryId);
    }
  },
  
  mounted() {
    // 加载搜索历史
    const savedHistory = localStorage.getItem('searchHistory');
    if (savedHistory) {
      try {
        this.searchHistory = JSON.parse(savedHistory);
      } catch (error) {
        console.error('加载搜索历史失败:', error);
      }
    }
    this.loadCategories();
  },
  
  beforeUnmount() {
    if (this.searchTimer) {
      clearTimeout(this.searchTimer);
    }
    if (this.suggestionTimer) {
      clearTimeout(this.suggestionTimer);
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&display=swap');

.side-panel {
  width: 280px;
  background: #f8f9fa;
  border-left: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.panel-header {
  padding: 20px;
  border-bottom: 1px solid #e9ecef;
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #2c3e50;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  letter-spacing: 0.2px;
}

.panel-toggle {
  background: none;
  border: 1px solid #dee2e6;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 600;
  min-width: 50px;
  text-align: center;
  white-space: nowrap;
}

.panel-toggle:hover {
  background: #e9ecef;
}

.panel-toggle.collapsed {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  transition: all 0.3s;
}

.panel-content.collapsed {
  display: none;
}

.search-section,
.filter-section,
.sort-section,
.stats-section {
  margin-bottom: 30px;
}

.search-section h4,
.filter-section h4,
.sort-section h4,
.stats-section h4 {
  margin: 0 0 15px 0;
  font-size: 14px;
  font-weight: 700;
  color: #495057;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  letter-spacing: 0.2px;
}

.search-input-wrapper {
  position: relative;
  margin-bottom: 15px;
}

.search-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 400;
}

.search-input:focus {
  border-color: #007bff;
}

.semantic-search {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.semantic-input {
  border-color: #667eea;
}

.btn-search {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 600;
}

.btn-search:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  transform: translateY(-1px);
}

.btn-search:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.semantic-results {
  margin-top: 15px;
  border-top: 1px solid #eee;
  padding-top: 15px;
}

.semantic-results h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 700;
}

.search-result-item {
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.search-result-item:hover {
  background-color: #f8f9fa;
  border-color: #667eea;
}

.result-title {
  font-weight: 700;
  color: #333;
  margin-bottom: 4px;
  font-size: 14px;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.result-snippet {
  color: #666;
  font-size: 12px;
  margin-bottom: 6px;
  line-height: 1.4;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 400;
}

.result-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
}

.result-score {
  color: #667eea;
  font-weight: 700;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.result-tags {
  color: #888;
  font-style: italic;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 400;
}

.btn-clear {
  background: #f8f9fa;
  color: #666;
  border: 1px solid #ddd;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-top: 10px;
  width: 100%;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 600;
}

.btn-clear:hover {
  background: #e9ecef;
  border-color: #adb5bd;
}

.clear-search {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 18px;
  color: #6c757d;
  cursor: pointer;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-search:hover {
  color: #dc3545;
}

.search-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-label,
.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #495057;
  cursor: pointer;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 500;
}

.checkbox-label input,
.radio-label input {
  margin: 0;
}

.tags-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-filter {
  background: white;
  border: 1px solid #dee2e6;
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 12px;
  color: #495057;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 600;
}

.tag-filter:hover {
  border-color: #007bff;
  background: #f0f8ff;
}

.tag-filter.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.tag-count {
  font-size: 11px;
  opacity: 0.8;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 500;
}

.sort-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stats-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.stat-label {
  font-size: 13px;
  color: #6c757d;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 500;
}

.stat-value {
  font-size: 14px;
  font-weight: 700;
  color: #007bff;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

/* 滚动条样式 */
.panel-content::-webkit-scrollbar {
  width: 6px;
}

.panel-content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.panel-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.panel-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 搜索建议样式 */
.search-input-group {
  position: relative;
}

.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #dee2e6;
  border-top: none;
  border-radius: 0 0 6px 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}

.suggestion-item {
  padding: 8px 12px;
  color: #495057;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 1px solid #f8f9fa;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 400;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:hover {
  background: #f8f9fa;
  color: #007bff;
}

/* 搜索历史样式 */
.search-history {
  margin-top: 15px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.search-history h5 {
  margin: 0 0 8px 0;
  font-size: 12px;
  font-weight: 600;
  color: #6c757d;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.history-items {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.history-item {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 12px;
  padding: 4px 8px;
  font-size: 11px;
  color: #495057;
  cursor: pointer;
  transition: all 0.2s;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 500;
}

.history-item:hover {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.btn-clear-history {
  background: none;
  border: none;
  color: #dc3545;
  font-size: 11px;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.2s;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 500;
}

.btn-clear-history:hover {
  background: rgba(220, 53, 69, 0.1);
}

/* 搜索状态提示 */
.search-status {
  margin: 10px 0;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  animation: fadeIn 0.3s ease;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 500;
}

.search-status.info {
  background: #e3f2fd;
  border: 1px solid #bbdefb;
  color: #1976d2;
}

.search-status.success {
  background: #e8f5e8;
  border: 1px solid #c8e6c9;
  color: #388e3c;
}

.search-status.warning {
  background: #fff3e0;
  border: 1px solid #ffcc02;
  color: #f57c00;
}

.search-status.error {
  background: #ffebee;
  border: 1px solid #ffcdd2;
  color: #d32f2f;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 语义搜索结果样式 */
.semantic-results {
  margin-top: 15px;
  border-top: 1px solid #e9ecef;
  padding-top: 15px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f8f9fa;
}

.results-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  color: #495057;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.results-info {
  display: flex;
  gap: 8px;
  align-items: center;
}

.results-count {
  color: #6c757d;
  font-size: 12px;
  font-weight: 600;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.search-time {
  color: #adb5bd;
  font-size: 11px;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 400;
}

.results-container {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 12px;
}

.search-result-item {
  padding: 12px;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.search-result-item:hover {
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.1);
  transform: translateY(-1px);
}

.search-result-item.high-relevance {
  border-left: 4px solid #28a745;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.result-title {
  color: #007bff;
  font-size: 13px;
  font-weight: 600;
  line-height: 1.4;
  flex: 1;
  margin-right: 8px;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.result-score-badge {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  white-space: nowrap;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.result-score-badge.score-excellent {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.result-score-badge.score-good {
  background: #cce5ff;
  color: #004085;
  border: 1px solid #99d3ff;
}

.result-score-badge.score-fair {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.result-score-badge.score-low {
  background: #f8f9fa;
  color: #6c757d;
  border: 1px solid #dee2e6;
}

.result-snippet {
  color: #6c757d;
  font-size: 12px;
  line-height: 1.5;
  margin-bottom: 8px;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 400;
}

.result-snippet mark {
  background: #fff3cd;
  color: #856404;
  padding: 1px 2px;
  border-radius: 2px;
}

.result-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
}

.result-date {
  color: #adb5bd;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 400;
}

.result-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  align-items: center;
}

.tag-chip {
  background: #e3f2fd;
  color: #1976d2;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
  border: 1px solid #bbdefb;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 500;
}

.more-tags {
  color: #6c757d;
  font-size: 10px;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 500;
}

.results-actions {
  display: flex;
  gap: 8px;
}

.btn-export {
  background: #28a745;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 600;
}

.btn-export:hover {
  background: #218838;
  transform: translateY(-1px);
}

.loading-spinner {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 导入导出功能样式 */
.import-export-section {
  margin-bottom: 30px;
  padding: 15px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.import-export-section h4 {
  margin: 0 0 15px 0;
  font-size: 14px;
  font-weight: 700;
  color: #495057;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.export-controls,
.import-controls {
  margin-bottom: 20px;
}

.export-controls h5,
.import-controls h5 {
  margin: 0 0 10px 0;
  font-size: 13px;
  font-weight: 600;
  color: #6c757d;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.export-format-selector,
.merge-mode-selector {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.format-option,
.merge-option {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #495057;
  cursor: pointer;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 500;
}

.format-option input,
.merge-option input {
  margin: 0;
}

.btn-export,
.btn-import,
.btn-select-file {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.2s;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: center;
  width: 100%;
}

.btn-export:hover:not(:disabled),
.btn-import:hover:not(:disabled),
.btn-select-file:hover {
  background: linear-gradient(135deg, #218838 0%, #1ea085 100%);
  transform: translateY(-1px);
}

.btn-export:disabled,
.btn-import:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-select-file {
  background: linear-gradient(135deg, #007bff 0%, #6610f2 100%);
  margin-bottom: 10px;
}

.btn-select-file:hover {
  background: linear-gradient(135deg, #0056b3 0%, #520dc2 100%);
}

.file-upload-area {
  margin-bottom: 12px;
}

.selected-file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  font-size: 12px;
  margin-bottom: 10px;
}

.file-name {
  color: #495057;
  font-weight: 600;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  color: #6c757d;
  font-size: 11px;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.btn-clear-file {
  background: none;
  border: none;
  color: #dc3545;
  font-size: 16px;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.btn-clear-file:hover {
  background: rgba(220, 53, 69, 0.1);
}

.import-export-status {
  margin-top: 12px;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  animation: fadeIn 0.3s ease;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 500;
}

.import-export-status.info {
  background: #e3f2fd;
  border: 1px solid #bbdefb;
  color: #1976d2;
}

.import-export-status.success {
  background: #e8f5e8;
  border: 1px solid #c8e6c9;
  color: #388e3c;
}

.import-export-status.warning {
  background: #fff3e0;
  border: 1px solid #ffcc02;
  color: #f57c00;
}

.import-export-status.error {
  background: #ffebee;
  border: 1px solid #ffcdd2;
  color: #d32f2f;
}

.status-icon {
  font-size: 14px;
}

.status-message {
  flex: 1;
  line-height: 1.4;
}

/* 分类管理样式 */
.category-management-section {
  margin-bottom: 30px;
  padding: 15px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.category-management-section h4 {
  margin: 0 0 15px 0;
  font-size: 14px;
  font-weight: 700;
  color: #495057;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.category-controls {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.btn-category-manager {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.2s;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
}

.btn-category-manager:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  transform: translateY(-1px);
}

.btn-icon {
  font-size: 14px;
}

.category-filter h5 {
  margin: 0 0 10px 0;
  font-size: 13px;
  font-weight: 600;
  color: #6c757d;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.category-filter-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.category-filter-item {
  background: white;
  border: 1px solid #dee2e6;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  color: #495057;
  transition: all 0.2s;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  text-align: left;
  width: 100%;
}

.category-filter-item:hover {
  border-color: #007bff;
  background: #f0f8ff;
}

.category-filter-item.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.category-filter-item.active .note-count {
  color: rgba(255, 255, 255, 0.8);
}

.category-icon {
  font-size: 14px;
  width: 16px;
  text-align: center;
}

.category-name {
  flex: 1;
  font-weight: 500;
}

.note-count {
  font-size: 11px;
  color: #6c757d;
  font-weight: normal;
}

.no-categories-hint {
  padding: 15px;
  text-align: center;
  color: #6c757d;
  font-size: 12px;
  background: #f8f9fa;
  border: 1px dashed #dee2e6;
  border-radius: 6px;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.no-categories-hint p {
  margin: 0;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .side-panel {
    width: 100%;
    position: absolute;
    top: 0;
    right: 0;
    z-index: 1000;
    box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
    padding: 12px;
    /* 移动端触摸优化 */
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
  }
  
  .panel-header {
    margin-bottom: 12px;
    /* 移动端头部优化 */
    position: sticky;
    top: 0;
    background: white;
    z-index: 10;
    padding-bottom: 8px;
    border-bottom: 1px solid #f8f9fa;
  }
  
  .panel-header h3 {
    font-size: 16px;
    line-height: 1.3;
  }
  
  .panel-toggle {
    padding: 8px 16px;
    font-size: 13px;
    min-height: 44px;
    min-width: 80px;
    border-radius: 8px;
    /* 移动端按钮优化 */
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
  }
  
  .panel-content.collapsed {
    display: block;
    height: 0;
    padding: 0 20px;
    overflow: hidden;
  }
  
  .search-section,
  .filter-section,
  .sort-section,
  .stats-section,
  .import-export-section,
  .category-management-section {
    margin-bottom: 15px;
    padding: 12px;
    /* 移动端卡片优化 */
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }
  
  .search-section h4,
  .filter-section h4,
  .sort-section h4,
  .stats-section h4,
  .import-export-section h4,
  .category-management-section h4 {
    font-size: 14px;
    margin-bottom: 10px;
    line-height: 1.3;
  }
  
  .search-input,
  .semantic-input {
    padding: 12px 16px;
    font-size: 16px; /* 防止iOS缩放 */
    min-height: 44px;
    border-radius: 8px;
    /* 移动端输入框优化 */
    -webkit-appearance: none;
    touch-action: manipulation;
  }
  
  .btn,
  .btn-search,
  .btn-export,
  .btn-import,
  .btn-select-file,
  .btn-category-manager {
    padding: 12px 20px;
    font-size: 14px;
    min-height: 44px;
    border-radius: 8px;
    /* 移动端按钮优化 */
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
    font-weight: 600;
  }
  
  .tag-filter,
  .category-filter-item {
    padding: 8px 12px;
    font-size: 12px;
    margin: 4px;
    min-height: 36px;
    border-radius: 8px;
    /* 移动端标签优化 */
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
  }
  
  .category-filter-item {
    margin: 0 0 6px 0;
    padding: 12px 16px;
    min-height: 44px;
  }
  
  .no-categories-hint {
    padding: 16px;
    border-radius: 8px;
    font-size: 13px;
  }
  
  .radio-label,
  .checkbox-label,
  .format-option,
  .merge-option {
    font-size: 13px;
    margin-bottom: 8px;
    padding: 8px 0;
    /* 移动端选项优化 */
    min-height: 44px;
    display: flex;
    align-items: center;
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
  }
  
  .radio-label input,
  .checkbox-label input,
  .format-option input,
  .merge-option input {
    margin-right: 12px;
    transform: scale(1.2);
  }
  
  .stats-grid {
    gap: 10px;
  }
  
  .stat-item {
    padding: 12px;
    border-radius: 8px;
    min-height: 60px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  
  .stat-label {
    font-size: 11px;
    line-height: 1.3;
  }
  
  .stat-value {
    font-size: 16px;
    line-height: 1.2;
  }
  
  .search-suggestions {
    position: fixed;
    left: 20px;
    right: 20px;
  }
  
  .results-container {
    max-height: 300px;
  }
  
  .result-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .result-score-badge {
    align-self: flex-start;
  }
  
  /* 搜索结果移动端优化 */
  .search-result-item {
    padding: 16px;
    margin-bottom: 12px;
    border-radius: 12px;
    /* 移动端触摸优化 */
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
  }
  
  .result-title {
    font-size: 14px;
    line-height: 1.4;
  }
  
  .result-snippet {
    font-size: 13px;
    line-height: 1.5;
  }
  
  /* 导入导出移动端优化 */
  .export-format-selector,
  .merge-mode-selector {
    flex-direction: column;
    gap: 8px;
  }
  
  .selected-file-info {
    padding: 12px;
    border-radius: 8px;
    min-height: 44px;
  }
  
  .btn-clear-file {
    min-width: 32px;
    min-height: 32px;
    font-size: 18px;
  }
  
  /* 搜索建议移动端优化 */
  .suggestion-item {
    padding: 12px 16px;
    font-size: 14px;
    min-height: 44px;
    border-radius: 8px;
    /* 移动端触摸优化 */
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
  }
  
  .history-item {
    padding: 8px 12px;
    font-size: 12px;
    min-height: 36px;
    border-radius: 8px;
    /* 移动端触摸优化 */
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
  }
}
</style>