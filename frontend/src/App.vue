<template>
  <div id="app">
    <div class="app-header">
      <div class="header-left">
        <h1 class="app-title">🐶 史迪仔小本本</h1>
        <div class="app-subtitle">今日事今日毕 我是最棒哒</div>
      </div>
      <div class="header-actions">
        <button 
          class="header-btn ai-btn" 
          :class="{ active: activeNavItem === 'ai' }"
          @click="handleNavClick('ai', openAIChat)" 
          @mouseenter="hoveredNavItem = 'ai'"
          @mouseleave="hoveredNavItem = null"
          title="AI智能助手"
        >
          <i class="fas fa-robot"></i>
          <span>AI助手</span>
        </button>
        <button 
          class="header-btn pomodoro-btn" 
          :class="{ active: activeNavItem === 'pomodoro' }"
          @click="handleNavClick('pomodoro', openPomodoroTimer)" 
          @mouseenter="hoveredNavItem = 'pomodoro'"
          @mouseleave="hoveredNavItem = null"
          title="番茄钟"
        >
          <i class="fas fa-clock"></i>
          <span>番茄钟</span>
        </button>
        <button 
          class="header-btn project-btn" 
          :class="{ active: activeNavItem === 'project' }"
          @click="handleNavClick('project', openProjectManager)" 
          @mouseenter="hoveredNavItem = 'project'"
          @mouseleave="hoveredNavItem = null"
          title="项目管理"
        >
          <i class="fas fa-project-diagram"></i>
          <span>项目管理</span>
        </button>
        
        <!-- 动画mascot元素 -->
        <div 
          v-if="hoveredNavItem" 
          class="anime-mascot"
          :class="`mascot-${hoveredNavItem}`"
        >
          <div class="mascot-container">
            <div class="mascot-head" :class="{ 'mascot-excited': hoveredNavItem }">
              <div class="mascot-eye left-eye" :class="{ 'eye-blink': hoveredNavItem }"></div>
              <div class="mascot-eye right-eye" :class="{ 'eye-blink': hoveredNavItem }"></div>
              <div class="mascot-cheek left-cheek"></div>
              <div class="mascot-cheek right-cheek"></div>
              <div class="mascot-mouth" :class="{ 'mouth-happy': hoveredNavItem }"></div>
              <div v-if="hoveredNavItem" class="sparkle sparkle-1">✨</div>
              <div v-if="hoveredNavItem" class="sparkle sparkle-2">✨</div>
            </div>
            <div class="mascot-tail" :class="{ 'tail-wag': hoveredNavItem }"></div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="app-content">
      <div class="left-panel">
        <NoteList 
          :notes="filteredNotes"
          :selected-note-id="selectedNoteId"
          @note-selected="selectNote"
          @note-create="createNote"
        />
      </div>
      
      <div class="main-panel">
        <NoteEditor 
          ref="noteEditor"
          :note="selectedNote"
          @note-updated="updateNote"
          @note-deleted="deleteNote"
          @create-category="handleShowCategoryManager"
        />
      </div>
      
      <div class="right-panel">
        <SidePanel 
          ref="sidePanel"
          :notes="notes"
          :filtered-count="filteredNotes.length"
          @search-change="handleSearch"
          @filter-change="handleFilter"
          @sort-change="handleSort"
          @select-note="selectNote"
          @notes-imported="handleNotesImported"
          @category-filter="handleCategoryFilter"
          @show-category-manager="handleShowCategoryManager"
        />
      </div>
      
      <div class="todo-panel">
        <TodoList />
      </div>
    </div>
    
    <!-- 分类管理弹窗 -->
    <div v-if="showCategoryManager" class="category-manager-overlay" @click="closeCategoryManager">
      <div class="category-manager-modal" @click.stop>
        <CategoryManager @close="closeCategoryManager" @category-updated="handleCategoryUpdated" />
      </div>
    </div>
    
    <!-- AI对话弹窗 -->
    <div v-if="showAIChat" class="ai-chat-overlay" @click="closeAIChat">
      <div class="ai-chat-modal" @click.stop>
        <AIChat @close="closeAIChat" />
      </div>
    </div>
    
    <!-- 番茄钟弹窗 -->
    <div v-if="showPomodoroTimer" class="pomodoro-overlay" @click="closePomodoroTimer">
      <div class="pomodoro-modal" @click.stop>
        <PomodoroTimer @close="closePomodoroTimer" />
      </div>
    </div>
    
    <!-- 项目管理弹窗 -->
    <div v-if="showProjectManager" class="project-manager-overlay" @click="closeProjectManager">
      <div class="project-manager-modal" @click.stop>
        <ProjectManager @close="closeProjectManager" />
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import NoteList from './components/NoteList.vue'
import NoteEditor from './components/NoteEditor.vue'
import SidePanel from './components/SidePanel.vue'
import TodoList from './components/TodoList.vue'
import CategoryManager from './components/CategoryManager.vue'
import AIChat from './components/AIChat.vue'
import PomodoroTimer from './components/PomodoroTimer.vue'
import ProjectManager from './components/ProjectManager.vue'

const API_BASE_URL = 'http://localhost:5000/api'

export default {
  name: 'App',
  components: {
    NoteList,
    NoteEditor,
    SidePanel,
    TodoList,
    CategoryManager,
    AIChat,
    PomodoroTimer,
    ProjectManager
  },
  data() {
    return {
      notes: [],
      filteredNotes: [],
      selectedNoteId: null,
      isLoading: false,
      searchQuery: '',
      searchOptions: {
        includeTitle: true,
        includeContent: true,
        includeTags: true
      },
      filterTags: [],
      sortBy: 'created_desc',
      selectedCategoryId: null,
      showCategoryManager: false,
      showAIChat: false,
      showPomodoroTimer: false,
      showProjectManager: false,
      activeNavItem: null,
      hoveredNavItem: null
    }
  },
  computed: {
    selectedNote() {
      return this.notes.find(note => note.id === this.selectedNoteId) || null
    }
  },
  async mounted() {
    // 延迟加载笔记，避免后端服务未完全启动
    setTimeout(async () => {
      await this.loadNotes()
    }, 1000)
  },
  methods: {
    async loadNotes() {
      this.isLoading = true
      try {
        const response = await axios.get(`${API_BASE_URL}/notes`)
        this.notes = response.data
        this.applyFiltersAndSort()
      } catch (error) {
        console.error('加载笔记失败:', error)
        // 静默处理错误，不显示弹窗
        console.log('后端服务可能还在启动中，将在后台重试...')
        // 5秒后重试
        setTimeout(() => {
          this.loadNotes()
        }, 5000)
      } finally {
        this.isLoading = false
      }
    },
    
    async createNote() {
      try {
        const newNote = {
          title: '新建笔记',
          content: '',
          tags: []
        }
        
        const response = await axios.post(`${API_BASE_URL}/notes`, newNote)
        const createdNote = response.data
        
        this.notes.unshift(createdNote)
        this.applyFiltersAndSort()
        this.selectNote(createdNote.id)
      } catch (error) {
        console.error('创建笔记失败:', error)
        this.showError('创建笔记失败')
      }
    },
    
    async updateNote(noteData, isAutoSave = false) {
      try {
        const response = await axios.put(`${API_BASE_URL}/notes/${noteData.id}`, noteData)
        const updatedNote = response.data
        
        const index = this.notes.findIndex(note => note.id === noteData.id)
        if (index > -1) {
          this.notes.splice(index, 1, updatedNote)
          this.applyFiltersAndSort()
        }
        
        if (!isAutoSave) {
          console.log('笔记保存成功')
          // 触发保存成功提示
          this.$nextTick(() => {
            if (this.$refs.noteEditor && this.$refs.noteEditor.showSaveSuccess) {
              this.$refs.noteEditor.showSaveSuccess()
            } else {
              alert('✅ 笔记保存成功！\n\n您的笔记已安全保存到数据库中，可以在左侧笔记列表中查看。')
            }
          })
        }
      } catch (error) {
        console.error('更新笔记失败:', error)
        this.showError('保存笔记失败')
        // 触发保存失败提示
        this.$refs.noteEditor?.showSaveError()
      }
    },
    
    async deleteNote(noteId) {
      try {
        await axios.delete(`${API_BASE_URL}/notes/${noteId}`)
        
        this.notes = this.notes.filter(note => note.id !== noteId)
        this.applyFiltersAndSort()
        
        if (this.selectedNoteId === noteId) {
          this.selectedNoteId = null
        }
        
        console.log('笔记删除成功')
      } catch (error) {
        console.error('删除笔记失败:', error)
        this.showError('删除笔记失败')
      }
    },
    
    selectNote(noteId) {
      this.selectedNoteId = noteId
    },
    
    closeEditor() {
      this.selectedNoteId = null
    },
    
    handleSearch({ query, options }) {
      this.searchQuery = query
      this.searchOptions = options
      this.applyFiltersAndSort()
    },
    
    handleFilter({ tags }) {
      this.filterTags = tags
      this.applyFiltersAndSort()
    },
    
    handleSort(sortBy) {
      this.sortBy = sortBy
      this.applyFiltersAndSort()
    },
    
    handleNotesImported(stats) {
      // 导入成功后重新加载笔记列表
      this.loadNotes()
      
      // 显示导入统计信息
      console.log('笔记导入统计:', stats)
    },
    
    handleCategoryFilter(categoryId) {
      this.selectedCategoryId = categoryId
      this.applyFiltersAndSort()
    },
    
    handleShowCategoryManager() {
      this.showCategoryManager = true
    },
    
    closeCategoryManager() {
      this.showCategoryManager = false
    },
    
    handleNavClick(navItem, callback) {
      // 设置活跃状态
      this.activeNavItem = navItem
      // 调用原有的打开方法
      callback()
    },
    
    openAIChat() {
      this.showAIChat = true
    },
    
    closeAIChat() {
      this.showAIChat = false
      this.activeNavItem = null
    },
    
    openPomodoroTimer() {
      this.showPomodoroTimer = true
    },
    
    closePomodoroTimer() {
      this.showPomodoroTimer = false
      this.activeNavItem = null
    },
    
    openProjectManager() {
      this.showProjectManager = true
    },
    
    closeProjectManager() {
      this.showProjectManager = false
      this.activeNavItem = null
    },
    
    handleCategoryUpdated() {
      // 分类更新后，重新加载笔记以获取最新的分类信息
      this.loadNotes()
      // 通知SidePanel刷新分类列表
      this.$nextTick(() => {
        if (this.$refs.sidePanel && this.$refs.sidePanel.loadCategories) {
          this.$refs.sidePanel.loadCategories()
        }
      })
    },
    
    applyFiltersAndSort() {
      let filtered = [...this.notes]
      
      // 应用搜索过滤
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(note => {
          let matches = false
          
          if (this.searchOptions.includeTitle && note.title) {
            matches = matches || note.title.toLowerCase().includes(query)
          }
          
          if (this.searchOptions.includeContent && note.content) {
            matches = matches || note.content.toLowerCase().includes(query)
          }
          
          if (this.searchOptions.includeTags && note.tags) {
            matches = matches || note.tags.some(tag => 
              tag.toLowerCase().includes(query)
            )
          }
          
          return matches
        })
      }
      
      // 应用标签过滤
      if (this.filterTags.length > 0) {
        filtered = filtered.filter(note => {
          return note.tags && this.filterTags.some(tag => 
            note.tags.includes(tag)
          )
        })
      }
      
      // 应用分类过滤
      if (this.selectedCategoryId !== null) {
        filtered = filtered.filter(note => {
          return note.categories && note.categories.some(category => 
            category.id === this.selectedCategoryId
          )
        })
      }
      
      // 应用排序
      filtered.sort((a, b) => {
        switch (this.sortBy) {
          case 'created_desc':
            return new Date(b.created_at) - new Date(a.created_at)
          case 'created_asc':
            return new Date(a.created_at) - new Date(b.created_at)
          case 'updated_desc':
            return new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at)
          case 'title_asc':
            return (a.title || '').localeCompare(b.title || '')
          default:
            return 0
        }
      })
      
      this.filteredNotes = filtered
    },
    
    showError(message) {
      // 简单的错误提示，可以后续集成更好的通知组件
      alert(message)
    }
  }
}
</script>

<style>
  @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&display=swap');
  
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  }

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #a8e6cf 0%, #dcedc1 50%, #ffd3a5 100%);
  min-height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

#app {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  max-width: 100%;
  opacity: 0;
  animation: pageLoadFadeIn 1s ease-out 0.3s forwards;
}

@keyframes pageLoadFadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 史迪仔背景装饰 - 增强版 */
#app::before {
  content: '🐶';
  position: absolute;
  bottom: 20px;
  right: 30px;
  font-size: 120px;
  opacity: 0.15;
  z-index: 0;
  pointer-events: none;
  animation: float 6s ease-in-out infinite;
  text-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
}

#app::after {
  content: '✨';
  position: absolute;
  top: 100px;
  left: 50px;
  font-size: 60px;
  opacity: 0;
  z-index: 0;
  pointer-events: none;
  animation: sparkle 4s ease-in-out infinite 1s;
  animation-fill-mode: forwards;
}

/* 添加更多装饰元素 */
.app-content::before {
  content: '🌟';
  position: absolute;
  top: 50%;
  right: 20px;
  font-size: 40px;
  opacity: 0;
  z-index: 0;
  pointer-events: none;
  animation: twinkle 3s ease-in-out infinite 0.8s;
  animation-fill-mode: forwards;
}

.app-content::after {
  content: '💫';
  position: absolute;
  bottom: 30%;
  left: 20px;
  font-size: 35px;
  opacity: 0;
  z-index: 0;
  pointer-events: none;
  animation: rotate 8s linear infinite 1.5s;
  animation-fill-mode: forwards;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  33% {
    transform: translateY(-8px) rotate(2deg);
  }
  66% {
    transform: translateY(-15px) rotate(-1deg);
  }
}

@keyframes sparkle {
  0% {
    transform: scale(1) rotate(0deg);
    opacity: 0.2;
  }
  50% {
    transform: scale(1.2) rotate(180deg);
    opacity: 0.4;
  }
  100% {
    transform: scale(1) rotate(0deg);
    opacity: 0.2;
  }
}

@keyframes twinkle {
  0% {
    transform: scale(1);
    opacity: 0.1;
  }
  50% {
    transform: scale(1.3);
    opacity: 0.25;
  }
  100% {
    transform: scale(1);
    opacity: 0.1;
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.app-header {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.9), rgba(118, 75, 162, 0.8));
  backdrop-filter: blur(25px);
  color: white;
  padding: 20px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  margin: 15px;
  border-radius: 25px;
  z-index: 1;
  position: relative;
  overflow: visible;
  min-width: 0;
  width: calc(100% - 30px);
  max-width: calc(100vw - 30px);
}

.app-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  animation: shimmer 3s ease-in-out infinite;
  pointer-events: none;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%) translateY(-100%) rotate(45deg);
  }
  50% {
    transform: translateX(100%) translateY(100%) rotate(45deg);
  }
  100% {
    transform: translateX(-100%) translateY(-100%) rotate(45deg);
  }
}

.header-left {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  flex: 1;
  min-width: 300px;
  max-width: 60%;
}

.app-title {
    font-size: 2rem;
    font-weight: 800;
    margin: 0 0 8px 0;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    gap: 12px;
    font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
    letter-spacing: 0.5px;
    white-space: nowrap;
    overflow: visible;
  }

.app-subtitle {
    font-size: 1rem;
    opacity: 0.9;
    font-weight: 600;
    font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
    letter-spacing: 0.3px;
    margin: 0;
  }

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(16px);
  padding: 8px;
  border-radius: 50px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.header-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  padding: 12px 24px;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  white-space: nowrap;
  position: relative;
  overflow: hidden;
}

.header-btn:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(255, 255, 255, 0.1);
}

.header-btn.active {
  color: white;
  background: rgba(255, 255, 255, 0.15);
}

.header-btn.active::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shine 3s ease-in-out infinite;
}

@keyframes shine {
  0% {
    transform: translateX(-100%);
  }
  50% {
    transform: translateX(100%);
  }
  100% {
    transform: translateX(-100%);
  }
}

.header-btn i {
  font-size: 1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.header-btn:hover i {
  transform: scale(1.1) rotate(5deg);
}

.header-btn.active i {
  transform: scale(1.05);
  filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.3));
}

.header-actions::before {
  content: '';
  position: absolute;
  inset: -2px;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  border-radius: 50px;
  opacity: 0;
  animation: border-glow 4s ease-in-out infinite;
}

@keyframes border-glow {
  0%, 100% {
    opacity: 0;
    transform: rotate(0deg);
  }
  50% {
    opacity: 1;
    transform: rotate(180deg);
  }
}

/* 动画mascot样式 */
.anime-mascot {
  position: absolute;
  top: -48px;
  left: 50%;
  transform: translateX(-50%);
  pointer-events: none;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  z-index: 10;
}

.mascot-ai {
  left: 20%;
}

.mascot-pomodoro {
  left: 50%;
}

.mascot-project {
  left: 80%;
}

.mascot-container {
  position: relative;
  width: 48px;
  height: 48px;
}

.mascot-head {
  position: absolute;
  width: 40px;
  height: 40px;
  background: white;
  border-radius: 50%;
  left: 50%;
  transform: translateX(-50%);
  animation: float 2s ease-in-out infinite;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.mascot-excited {
  animation: excited 0.5s ease-in-out;
}

.mascot-eye {
  position: absolute;
  width: 8px;
  height: 8px;
  background: black;
  border-radius: 50%;
  top: 40%;
}

.left-eye {
  left: 25%;
}

.right-eye {
  right: 25%;
}

.eye-blink {
  animation: blink 0.2s ease-in-out;
}

.mascot-cheek {
  position: absolute;
  width: 8px;
  height: 6px;
  background: #ffc0cb;
  border-radius: 50%;
  top: 55%;
  opacity: 0.6;
}

.left-cheek {
  left: 15%;
}

.right-cheek {
  right: 15%;
}

.mascot-mouth {
  position: absolute;
  width: 16px;
  height: 8px;
  border-bottom: 2px solid black;
  border-radius: 0 0 16px 16px;
  left: 30%;
  top: 60%;
  transition: all 0.3s ease;
}

.mouth-happy {
  transform: scaleY(1.5) translateY(-4px);
}

.mascot-tail {
  position: absolute;
  bottom: -4px;
  left: 50%;
  width: 16px;
  height: 16px;
  background: white;
  transform: translateX(-50%) rotate(45deg);
  border-radius: 0 0 0 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.tail-wag {
  animation: wag 0.3s ease-in-out infinite alternate;
}

.sparkle {
  position: absolute;
  font-size: 12px;
  animation: sparkle-appear 0.6s ease-out;
}

.sparkle-1 {
  top: -4px;
  right: -4px;
}

.sparkle-2 {
  top: -8px;
  left: 0;
  animation-delay: 0.1s;
}

@keyframes float {
  0%, 100% {
    transform: translateX(-50%) translateY(0px);
  }
  50% {
    transform: translateX(-50%) translateY(-12px);
  }
}

@keyframes excited {
  0%, 100% {
    transform: translateX(-50%) scale(1) rotate(0deg);
  }
  25% {
    transform: translateX(-50%) scale(1.1) rotate(-5deg);
  }
  75% {
    transform: translateX(-50%) scale(1.1) rotate(5deg);
  }
}

@keyframes blink {
  0%, 100% {
    transform: scaleY(1);
  }
  50% {
    transform: scaleY(0.2);
  }
}

@keyframes wag {
  0% {
    transform: translateX(-50%) rotate(45deg);
  }
  100% {
    transform: translateX(-50%) rotate(25deg);
  }
}

@keyframes sparkle-appear {
  0% {
    opacity: 0;
    transform: scale(0);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
  100% {
    opacity: 0;
    transform: scale(0.8);
  }
}

.project-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.project-btn:hover {
  background: linear-gradient(135deg, #764ba2, #667eea);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(118, 75, 162, 0.4);
}

.pomodoro-btn:hover {
  background: rgba(255, 107, 107, 0.3);
}

.app-content {
  flex: 1;
  display: grid;
  grid-template-columns: 1.2fr 2fr 1fr 1fr;
  gap: 0;
  padding: 0;
  width: 100%;
  max-width: 100vw;
  min-height: calc(100vh - 70px);
  z-index: 1;
  position: relative;
  overflow: hidden;
}

.left-panel {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.95), rgba(248, 250, 255, 0.9));
  backdrop-filter: blur(25px);
  border-right: 1px solid rgba(102, 126, 234, 0.15);
  padding: 0;
  min-height: calc(100vh - 80px);
  overflow: hidden;
  box-shadow: inset -1px 0 0 rgba(102, 126, 234, 0.1);
  position: relative;
}

.left-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
  z-index: 1;
}



.right-panel {
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.95), rgba(248, 250, 255, 0.9));
    backdrop-filter: blur(25px);
    border-left: 1px solid rgba(102, 126, 234, 0.15);
    padding: 25px;
    min-height: calc(100vh - 70px);
    overflow-y: auto;
    box-shadow: inset 1px 0 0 rgba(102, 126, 234, 0.1);
    position: relative;
  }

  .right-panel::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #f093fb, #764ba2, #667eea);
    z-index: 1;
  }

  .main-panel {
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(252, 253, 255, 0.95));
    backdrop-filter: blur(25px);
    border-left: 1px solid rgba(102, 126, 234, 0.15);
    border-right: 1px solid rgba(102, 126, 234, 0.15);
    padding: 0;
    min-height: calc(100vh - 70px);
    overflow: hidden;
    box-shadow: inset 1px 0 0 rgba(102, 126, 234, 0.08), inset -1px 0 0 rgba(102, 126, 234, 0.08);
    position: relative;
  }

  .main-panel::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #667eea, #f093fb, #667eea);
    z-index: 1;
  }

  .right-panel::-webkit-scrollbar {
    width: 6px;
  }

  .right-panel::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.05);
    border-radius: 3px;
  }

  .right-panel::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 3px;
    transition: background 0.3s ease;
  }

  .right-panel::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0.4);
  }

  .todo-panel {
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.95), rgba(248, 250, 255, 0.9));
    backdrop-filter: blur(25px);
    border-left: 1px solid rgba(102, 126, 234, 0.15);
    padding: 25px;
    min-height: calc(100vh - 70px);
    overflow-y: auto;
    box-shadow: inset 1px 0 0 rgba(102, 126, 234, 0.1);
    position: relative;
  }

  .todo-panel::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #f093fb, #667eea, #764ba2);
    z-index: 1;
  }

  .todo-panel::-webkit-scrollbar {
    width: 6px;
  }

  .todo-panel::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.05);
    border-radius: 3px;
  }

  .todo-panel::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 3px;
    transition: background 0.3s ease;
  }

  .todo-panel::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0.4);
  }

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(102, 126, 234, 0.2);
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-overlay p {
  color: #667eea;
  font-size: 16px;
  font-weight: 500;
}

/* 分类管理弹窗样式 */
.category-manager-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.category-manager-modal {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 100%;
  max-height: 80vh;
  overflow: hidden;
  animation: modalSlideIn 0.3s ease-out;
}

/* AI对话弹窗样式 */
.ai-chat-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
  animation: fadeIn 0.3s ease;
}

.ai-chat-modal {
  width: 90%;
  max-width: 800px;
  height: 80vh;
  max-height: 600px;
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideInUp 0.3s ease;
}

/* 番茄钟弹窗样式 */
.pomodoro-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
  animation: fadeIn 0.3s ease;
}

.pomodoro-modal {
  width: 90%;
  max-width: 500px;
  height: 80vh;
  max-height: 700px;
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideInUp 0.3s ease;
}

/* 项目管理弹窗样式 */
.project-manager-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
  animation: fadeIn 0.3s ease;
}

.project-manager-modal {
  width: 90%;
  max-width: 1200px;
  height: 80vh;
  max-height: 800px;
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideInUp 0.3s ease;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 移动端适配 - 分类管理弹窗 */
@media (max-width: 768px) {
  .category-manager-overlay {
    padding: 10px;
  }
  
  .category-manager-modal {
    max-width: 100%;
    max-height: 90vh;
    margin: 0;
  }
  
  .header-actions {
    gap: 8px;
  }
  
  .header-btn {
    padding: 8px 12px;
    font-size: 0.8rem;
  }
  
  .header-btn span {
    display: none;
  }
  
  .ai-chat-modal,
  .pomodoro-modal,
  .project-manager-modal {
    width: 95%;
    height: 85vh;
  }
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}



/* 响应式设计 */
@media (max-width: 1024px) {
  .right-panel {
    display: none;
  }
}

@media (max-width: 768px) {
  #app::before,
  #app::after {
    display: none;
  }
  
  .app-header {
    margin: 10px;
    padding: 20px;
    border-radius: 16px;
    /* 移动端触摸优化 */
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
    flex-direction: column;
    gap: 15px;
    width: calc(100% - 20px);
    max-width: calc(100vw - 20px);
  }
  
  .header-left {
    min-width: auto;
    width: 100%;
    max-width: 100%;
  }
  
  .header-actions {
    justify-content: center;
    width: 100%;
    padding: 6px;
    gap: 6px;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(20px);
  }
  
  .header-btn {
    padding: 10px 16px;
    font-size: 0.8rem;
  }
  
  .header-btn span {
    display: none;
  }
  
  .header-btn i {
    font-size: 1.1rem;
  }
  
  .app-content {
    flex-direction: column;
    padding: 0 15px 15px 15px;
    gap: 15px;
    /* 移动端滚动优化 */
    -webkit-overflow-scrolling: touch;
  }
  
  .left-panel {
    width: 100%;
    height: auto;
    max-height: 40vh;
    min-height: 200px;
    resize: none;
    border-radius: 16px;
    /* 移动端侧边栏优化 */
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .main-panel {
    flex: 1;
    min-height: 60vh;
    height: auto;
    border-radius: 16px;
    /* 移动端主面板优化 */
    overflow: hidden;
  }
  
  .app-title {
    font-size: 1.6rem;
    line-height: 1.2;
    min-width: auto;
    white-space: normal;
    text-align: center;
    width: 100%;
  }
  
  .app-subtitle {
    font-size: 1rem;
    line-height: 1.3;
  }
  
  /* 移动端手势支持 */
  .left-panel {
    position: relative;
  }
  
  .left-panel::before {
    content: '';
    position: absolute;
    top: 8px;
    left: 50%;
    transform: translateX(-50%);
    width: 40px;
    height: 4px;
    background: #dee2e6;
    border-radius: 2px;
    z-index: 10;
  }
}

@media (max-width: 480px) {
  .app-header {
    margin: 8px;
    padding: 16px;
    border-radius: 12px;
    width: calc(100% - 16px);
    max-width: calc(100vw - 16px);
  }
  
  .app-content {
    padding: 0 10px 10px 10px;
    gap: 10px;
  }
  
  .left-panel {
    max-height: 35vh;
    min-height: 180px;
    border-radius: 12px;
  }
  
  .main-panel {
    min-height: 65vh;
    border-radius: 12px;
  }
  
  .app-title {
    font-size: 1.4rem;
    line-height: 1.2;
    white-space: normal;
    text-align: center;
    word-break: keep-all;
  }
  
  .app-subtitle {
    font-size: 0.9rem;
    line-height: 1.3;
  }
  
  /* 超小屏幕优化 */
  .left-panel::before {
    width: 35px;
    height: 3px;
  }
}

/* 移动端通用触摸优化 */
@media (max-width: 768px) {
  * {
    -webkit-tap-highlight-color: transparent;
  }
  
  button, input, textarea, select {
    touch-action: manipulation;
    -webkit-appearance: none;
    border-radius: 8px;
  }
  
  /* 提升触摸目标大小 */
  button {
    min-height: 44px;
    min-width: 44px;
  }
  
  input, textarea {
    min-height: 44px;
    font-size: 16px; /* 防止iOS缩放 */
  }
  
  /* 滚动条优化 */
  ::-webkit-scrollbar {
    width: 6px;
  }
  
  ::-webkit-scrollbar-track {
    background: transparent;
  }
  
  ::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 3px;
  }
  
  ::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0.3);
  }
}
</style>
