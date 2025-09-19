<template>
  <div class="note-list">
    <div class="note-list-header">
      <h2>笔记列表</h2>
      <button class="btn-create" @click="createNote">
        <span class="icon">+</span>
        新建笔记
      </button>
    </div>
    
    <div class="note-list-content">
      <div 
        v-for="note in notes" 
        :key="note.id"
        class="note-item"
        :class="{ active: selectedNoteId === note.id }"
        @click="selectNote(note.id)"
      >
        <div class="note-title">{{ note.title || '无标题笔记' }}</div>
        <div class="note-snippet">{{ note.snippet }}</div>
        <div class="note-meta">
          <span class="note-date">{{ formatDate(note.created_at) }}</span>
          <div class="note-tags">
            <span 
              v-for="tag in note.tags" 
              :key="tag"
              class="tag"
            >
              {{ tag }}
            </span>
          </div>
        </div>
      </div>
      
      <div v-if="notes.length === 0" class="empty-state">
        <div class="empty-icon">📝</div>
        <p>还没有笔记，点击上方按钮创建第一篇笔记吧！</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NoteList',
  props: {
    notes: {
      type: Array,
      default: () => []
    },
    selectedNoteId: {
      type: Number,
      default: null
    }
  },
  emits: ['note-selected', 'note-create'],
  methods: {
    selectNote(noteId) {
      this.$emit('note-selected', noteId);
    },
    
    createNote() {
      this.$emit('note-create');
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      
      // 确保使用本地时区的正确时间
      const date = new Date(dateString);
      const now = new Date();
      
      // 计算时间差（以本地时间为准）
      const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const startOfNoteDay = new Date(date.getFullYear(), date.getMonth(), date.getDate());
      const diffMs = startOfToday - startOfNoteDay;
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      
      if (diffDays === 0) {
        // 今天 - 显示具体时间
        return '今天 ' + date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit',
          timeZone: 'Asia/Shanghai'
        });
      } else if (diffDays === 1) {
        // 昨天 - 显示具体时间
        return '昨天 ' + date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit',
          timeZone: 'Asia/Shanghai'
        });
      } else if (diffDays < 7) {
        // 一周内 - 显示星期和时间
        const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
        return weekdays[date.getDay()] + ' ' + date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit',
          timeZone: 'Asia/Shanghai'
        });
      } else {
        // 超过一周 - 显示日期和时间
        return date.toLocaleDateString('zh-CN', {
          month: '2-digit',
          day: '2-digit',
          timeZone: 'Asia/Shanghai'
        }) + ' ' + date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit',
          timeZone: 'Asia/Shanghai'
        });
      }
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&display=swap');

.note-list {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: transparent;
  position: relative;
}

.note-list-header {
  padding: 25px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 255, 0.95));
  backdrop-filter: blur(15px);
  border-radius: 0;
  border-bottom: 1px solid rgba(102, 126, 234, 0.15);
  position: relative;
  z-index: 2;
  margin-top: 3px;
}

.note-list-header h2 {
  margin: 0 0 18px 0;
  font-size: 1.4rem;
  font-weight: 800;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  letter-spacing: 0.3px;
}

.note-list-header h2::before {
  content: '📋';
  font-size: 1.2rem;
}

.btn-create {
  width: 100%;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.35), 0 2px 8px rgba(118, 75, 162, 0.2);
  position: relative;
  overflow: hidden;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  letter-spacing: 0.3px;
  border: 2px solid transparent;
}

.btn-create::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.btn-create:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.45), 0 4px 15px rgba(240, 147, 251, 0.3);
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 50%, #ee82e9 100%);
}

.btn-create:hover::before {
  left: 100%;
}

.btn-create:active {
  transform: translateY(0);
}

.icon {
  font-size: 18px;
  font-weight: bold;
}

.note-list-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 255, 0.95));
  backdrop-filter: blur(15px);
  border-radius: 0;
}

.note-item {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.95), rgba(252, 253, 255, 0.9));
  backdrop-filter: blur(12px);
  border: 1px solid rgba(102, 126, 234, 0.12);
  border-radius: 18px;
  padding: 22px;
  margin-bottom: 18px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 6px 25px rgba(102, 126, 234, 0.08), 0 2px 10px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
}

.note-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.note-item:hover {
  transform: translateY(-6px) scale(1.01);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2), 0 4px 15px rgba(240, 147, 251, 0.1);
  border-color: rgba(102, 126, 234, 0.25);
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 255, 0.95));
}

.note-item:hover::before {
  transform: scaleX(1);
}

.note-item.active {
  border-color: rgba(102, 126, 234, 0.4);
  background: linear-gradient(145deg, rgba(102, 126, 234, 0.08), rgba(240, 147, 251, 0.05));
  box-shadow: 0 10px 35px rgba(102, 126, 234, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.5);
  transform: translateY(-4px) scale(1.02);
}

.note-item.active::before {
  transform: scaleX(1);
}

.note-title {
  font-size: 17px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 10px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  letter-spacing: 0.2px;
}

.note-snippet {
  font-size: 14px;
  color: #6c757d;
  line-height: 1.6;
  margin-bottom: 15px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 400;
}

.note-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  margin-top: 8px;
}

.note-date {
  color: #868e96;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.note-date::before {
  content: '🕒';
  font-size: 11px;
}

.note-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  max-width: 60%;
}

.tag {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  color: #667eea;
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
  border: 1px solid rgba(102, 126, 234, 0.2);
  transition: all 0.2s ease;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.tag:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
  transform: scale(1.05);
}

.empty-state {
  text-align: center;
  padding: 80px 30px;
  color: #6c757d;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 20px;
  margin: 20px;
  backdrop-filter: blur(10px);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.7;
}

.empty-state p {
  margin: 0;
  font-size: 16px;
  line-height: 1.6;
  font-weight: 600;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

/* 滚动条样式 */
.note-list-content::-webkit-scrollbar {
  width: 8px;
}

.note-list-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.note-list-content::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3));
  border-radius: 4px;
  transition: background 0.3s ease;
}

.note-list-content::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.5), rgba(118, 75, 162, 0.5));
}

/* 响应式设计 */
@media (max-width: 768px) {
  .note-list {
    /* 移动端触摸优化 */
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
  }
  
  .note-list-header {
    padding: 20px;
    border-radius: 16px 16px 0 0;
    /* 移动端头部优化 */
    position: sticky;
    top: 0;
    z-index: 10;
  }
  
  .note-list-header h2 {
    font-size: 1.2rem;
    margin-bottom: 15px;
    line-height: 1.3;
  }
  
  .btn-create {
    padding: 14px 18px;
    font-size: 15px;
    border-radius: 12px;
    min-height: 48px;
    /* 移动端按钮优化 */
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
    font-weight: 700;
  }
  
  .note-list-content {
    padding: 16px;
    border-radius: 0 0 16px 16px;
    /* 移动端滚动优化 */
    -webkit-overflow-scrolling: touch;
    overscroll-behavior: contain;
  }
  
  .note-item {
    padding: 18px;
    margin-bottom: 14px;
    border-radius: 14px;
    min-height: 120px;
    /* 移动端笔记项优化 */
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }
  
  .note-item:hover {
    transform: translateY(-2px) scale(1.005);
  }
  
  .note-item:active {
    transform: translateY(0) scale(0.98);
    transition: all 0.1s ease;
  }
  
  .note-title {
    font-size: 16px;
    line-height: 1.4;
    margin-bottom: 12px;
  }
  
  .note-snippet {
    font-size: 14px;
    line-height: 1.5;
    margin-bottom: 16px;
  }
  
  .note-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .note-date {
    font-size: 13px;
    font-weight: 600;
  }
  
  .note-tags {
    max-width: 100%;
    gap: 8px;
  }
  
  .tag {
    padding: 6px 10px;
    font-size: 12px;
    border-radius: 10px;
    min-height: 28px;
    /* 移动端标签优化 */
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
  }
  
  .empty-state {
    padding: 60px 24px;
    margin: 20px;
    border-radius: 18px;
  }
  
  .empty-icon {
    font-size: 56px;
    margin-bottom: 18px;
  }
  
  .empty-state p {
    font-size: 15px;
    line-height: 1.5;
  }
}

@media (max-width: 480px) {
  .note-list-header {
    padding: 16px;
    border-radius: 12px 12px 0 0;
  }
  
  .note-list-header h2 {
    font-size: 1.1rem;
    margin-bottom: 12px;
  }
  
  .btn-create {
    padding: 16px 20px;
    font-size: 14px;
    min-height: 52px;
  }
  
  .note-list-content {
    padding: 12px;
    border-radius: 0 0 12px 12px;
  }
  
  .note-item {
    padding: 16px;
    margin-bottom: 12px;
    border-radius: 12px;
    min-height: 110px;
  }
  
  .note-title {
    font-size: 15px;
  }
  
  .note-snippet {
    font-size: 13px;
    line-height: 1.4;
  }
  
  .note-date {
    font-size: 12px;
  }
  
  .tag {
    padding: 5px 8px;
    font-size: 11px;
    min-height: 26px;
  }
  
  .empty-state {
    padding: 50px 20px;
    margin: 16px;
    border-radius: 16px;
  }
  
  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }
  
  .empty-state p {
    font-size: 14px;
  }
}

/* 移动端通用触摸优化 */
@media (max-width: 768px) {
  .note-list * {
    -webkit-tap-highlight-color: transparent;
  }
  
  .note-list button {
    touch-action: manipulation;
    -webkit-appearance: none;
  }
  
  /* 滚动条移动端优化 */
  .note-list-content::-webkit-scrollbar {
    width: 4px;
  }
  
  .note-list-content::-webkit-scrollbar-track {
    background: transparent;
  }
  
  .note-list-content::-webkit-scrollbar-thumb {
    background: rgba(102, 126, 234, 0.3);
    border-radius: 2px;
  }
  
  .note-list-content::-webkit-scrollbar-thumb:hover {
    background: rgba(102, 126, 234, 0.5);
  }
  
  /* 移动端手势支持 */
  .note-item {
    position: relative;
    overflow: hidden;
  }
  
  .note-item::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(102, 126, 234, 0.05);
    opacity: 0;
    transition: opacity 0.2s ease;
    pointer-events: none;
  }
  
  .note-item:active::after {
    opacity: 1;
  }
}
</style>