<template>
  <div class="note-editor">
    <div v-if="!note" class="empty-editor">
      <div class="empty-icon">✏️</div>
      <h3>选择一篇笔记开始编辑</h3>
      <p>从左侧列表中选择笔记，或创建新笔记</p>
    </div>
    
    <div v-else class="editor-container">
      <div class="editor-header">
        <input 
          v-model="localNote.title"
          class="title-input"
          placeholder="输入笔记标题..."
          @input="onTitleChange"
        />
        
        <div class="editor-actions">
          <button 
            class="btn-ai-rewrite"
            @click="aiRewrite"
            :disabled="isSaving || isAiRewriting || !localNote.content"
          >
            {{ isAiRewriting ? 'AI润色中...' : '✨ AI润色' }}
          </button>
          
          <button 
            class="btn-generate-tags"
            @click="generateTags"
            :disabled="isSaving || isGeneratingTags || (!localNote.content && !localNote.title)"
          >
            {{ isGeneratingTags ? '生成中...' : '🏷️ 生成标签' }}
          </button>
          
          <button 
            class="btn-save"
            :class="{ saving: isSaving }"
            @click="saveNote"
            :disabled="isSaving"
          >
            {{ isSaving ? '保存中...' : '保存' }}
          </button>
          
          <button 
            class="btn-delete"
            @click="deleteNote"
            :disabled="isSaving"
          >
            删除
          </button>
        </div>
      </div>
      
      <div class="editor-meta">
        <div class="meta-item">
          <span class="meta-label">创建时间：</span>
          <span class="meta-value">{{ formatDate(localNote.created_at) }}</span>
        </div>
        
        <div class="meta-item">
          <span class="meta-label">标签：</span>
          <div class="tags-input">
            <span 
              v-for="tag in localNote.tags" 
              :key="tag"
              class="tag"
            >
              {{ tag }}
              <button 
                class="tag-remove"
                @click="removeTag(tag)"
              >
                ×
              </button>
            </span>
            
            <input 
              v-model="newTag"
              class="tag-input"
              placeholder="添加标签..."
              @keyup.enter="addTag"
              @keyup.space="addTag"
            />
          </div>
        </div>
        
        <div class="meta-item">
          <span class="meta-label">分类：</span>
          <div class="categories-input">
            <span 
              v-for="category in selectedCategories" 
              :key="category.id"
              class="category-tag"
              :style="{ backgroundColor: category.color }"
            >
              <span class="category-icon">{{ category.icon }}</span>
              {{ category.name }}
              <button 
                class="category-remove"
                @click="removeCategory(category.id)"
              >
                ×
              </button>
            </span>
            
            <div class="category-selector">
              <button 
                class="btn-add-category"
                @click="showCategoryDropdown = !showCategoryDropdown"
                :disabled="availableCategories.length === 0"
              >
                <i class="icon">📁</i>
                {{ selectedCategories.length === 0 ? '选择分类' : '添加分类' }}
              </button>
              
              <div v-if="showCategoryDropdown" class="category-dropdown">
                <div 
                  v-for="category in availableCategories" 
                  :key="category.id"
                  class="category-option"
                  @click="addCategory(category)"
                >
                  <span class="category-icon">{{ category.icon }}</span>
                  <span class="category-name">{{ category.name }}</span>
                  <span class="category-description">{{ category.description || '暂无描述' }}</span>
                </div>
                
                <div v-if="availableCategories.length === 0" class="no-categories">
                  <span>暂无可选分类</span>
                  <button class="btn-create-category" @click="$emit('create-category')">
                    创建分类
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="editor-content">
        <textarea 
          v-model="localNote.content"
          class="content-textarea"
          placeholder="开始写下你的想法..."
          @input="onContentChange"
        ></textarea>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NoteEditor',
  props: {
    note: {
      type: Object,
      default: null
    }
  },
  emits: ['note-updated', 'note-deleted', 'create-category'],
  data() {
    return {
      localNote: null,
      newTag: '',
      isSaving: false,
      isAiRewriting: false,
      isGeneratingTags: false,
      autoSaveTimer: null,
      categories: [],
      selectedCategories: [],
      showCategoryDropdown: false
    };
  },
  watch: {
    note: {
      handler(newNote) {
        if (newNote) {
          this.localNote = { ...newNote };
          if (!this.localNote.tags) {
            this.localNote.tags = [];
          }
          // 同步分类信息
          if (newNote.categories) {
            this.selectedCategories = [...newNote.categories];
          } else {
            this.selectedCategories = [];
          }
        } else {
          this.localNote = null;
          this.selectedCategories = [];
        }
      },
      immediate: true
    }
  },
  mounted() {
    this.loadCategories();
    // 点击外部关闭下拉菜单
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  },
  computed: {
    availableCategories() {
      return this.categories.filter(category => 
        !this.selectedCategories.some(selected => selected.id === category.id)
      );
    }
  },
  methods: {
    onTitleChange() {
      this.scheduleAutoSave();
    },
    
    onContentChange() {
      this.scheduleAutoSave();
    },
    
    scheduleAutoSave() {
      if (this.autoSaveTimer) {
        clearTimeout(this.autoSaveTimer);
      }
      
      this.autoSaveTimer = setTimeout(() => {
        this.saveNote(true);
      }, 2000); // 2秒后自动保存
    },
    
    async saveNote(isAutoSave = false) {
      if (!this.localNote || this.isSaving) return;
      
      this.isSaving = true;
      
      try {
        // 生成内容摘要
        const content = this.localNote.content || '';
        const snippet = content.length > 100 
          ? content.substring(0, 100) + '...' 
          : content;
        
        const noteData = {
          ...this.localNote,
          snippet,
          categories: this.selectedCategories
        };
        
        this.$emit('note-updated', noteData, isAutoSave);
      } catch (error) {
        console.error('保存笔记失败:', error);
        this.showSaveError();
      } finally {
        this.isSaving = false;
      }
    },
    
    async deleteNote() {
      if (!this.localNote) return;
      
      if (confirm('确定要删除这篇笔记吗？此操作无法撤销。')) {
        this.$emit('note-deleted', this.localNote.id);
      }
    },
    
    addTag() {
      const tag = this.newTag.trim();
      if (tag && !this.localNote.tags.includes(tag)) {
        this.localNote.tags.push(tag);
        this.newTag = '';
        this.scheduleAutoSave();
      }
    },
    
    removeTag(tag) {
      const index = this.localNote.tags.indexOf(tag);
      if (index > -1) {
        this.localNote.tags.splice(index, 1);
        this.scheduleAutoSave();
      }
    },
    
    // 分类相关方法
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
    
    addCategory(category) {
      if (!this.selectedCategories.some(selected => selected.id === category.id)) {
        this.selectedCategories.push(category);
        this.showCategoryDropdown = false;
        this.scheduleAutoSave();
      }
    },
    
    removeCategory(categoryId) {
      const index = this.selectedCategories.findIndex(category => category.id === categoryId);
      if (index > -1) {
        this.selectedCategories.splice(index, 1);
        this.scheduleAutoSave();
      }
    },
     
     handleClickOutside(event) {
       const categorySelector = this.$el.querySelector('.category-selector');
       if (categorySelector && !categorySelector.contains(event.target)) {
         this.showCategoryDropdown = false;
       }
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
        // 今天
        return '今天 ' + date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit',
          timeZone: 'Asia/Shanghai'
        });
      } else if (diffDays === 1) {
        // 昨天
        return '昨天 ' + date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit',
          timeZone: 'Asia/Shanghai'
        });
      } else if (diffDays < 7) {
        // 一周内
        const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
        return weekdays[date.getDay()] + ' ' + date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit',
          timeZone: 'Asia/Shanghai'
        });
      } else {
        // 超过一周
        return date.toLocaleDateString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          timeZone: 'Asia/Shanghai'
        }) + ' ' + date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit',
          timeZone: 'Asia/Shanghai'
        });
      }
    },
    
    showSaveSuccess() {
      // 显示保存成功提示
      console.log('笔记保存成功');
      alert('✅ 笔记保存成功！\n\n您的笔记已安全保存到数据库中，可以在左侧笔记列表中查看。');
    },

    showSaveError() {
      // 显示保存失败提示
      console.error('笔记保存失败');
      alert('❌ 笔记保存失败！\n\n请检查网络连接或稍后重试。');
    },
    
    showSaveSuccess() {
      alert('✅ 笔记保存成功！\n\n您的笔记已安全保存到数据库中。');
    },
    
    async aiRewrite() {
      if (!this.localNote || !this.localNote.content || this.isAiRewriting) return;
      
      this.isAiRewriting = true;
      
      try {
        const response = await fetch('http://localhost:5000/api/ai/rewrite', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            text: this.localNote.content
          })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
          const rewrittenContent = result.rewritten_text;
          
          // 显示润色结果并询问用户是否应用
          const userConfirmed = confirm(
            `✨ AI润色完成！\n\n原文：\n${this.localNote.content.substring(0, 100)}${this.localNote.content.length > 100 ? '...' : ''}\n\n润色后：\n${rewrittenContent.substring(0, 100)}${rewrittenContent.length > 100 ? '...' : ''}\n\n是否应用润色结果？`
          );
          
          if (userConfirmed) {
            this.localNote.content = rewrittenContent;
            this.scheduleAutoSave();
            alert('✅ 润色结果已应用！');
          }
        } else {
          alert(result.error || 'AI润色失败，请稍后重试');
        }
      } catch (error) {
        console.error('AI润色请求失败:', error);
        alert('AI润色请求失败，请检查网络连接');
      } finally {
        this.isAiRewriting = false;
      }
    },
    
    async generateTags() {
      if (!this.localNote || (!this.localNote.content && !this.localNote.title) || this.isGeneratingTags) return;
      
      this.isGeneratingTags = true;
      
      try {
        const response = await fetch('http://localhost:5000/api/ai/generate-tags', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            title: this.localNote.title || '',
            text: this.localNote.content || ''
          })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
          // 合并新标签，避免重复
          const newTags = result.tags.filter(tag => !this.localNote.tags.includes(tag));
          
          if (newTags.length > 0) {
            // 直接添加新标签
            this.localNote.tags = [...this.localNote.tags, ...newTags];
            this.scheduleAutoSave();
            alert(`🏷️ 已自动添加标签：${newTags.join(', ')}`);
          } else {
            alert('AI生成的标签与现有标签重复，无需添加');
          }
        } else {
          alert(result.error || 'AI标签生成失败，请稍后重试');
        }
      } catch (error) {
        console.error('AI标签生成请求失败:', error);
        alert('AI标签生成请求失败，请检查网络连接');
      } finally {
        this.isGeneratingTags = false;
      }
    }
  },
  
  beforeUnmount() {
    if (this.autoSaveTimer) {
      clearTimeout(this.autoSaveTimer);
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&display=swap');

.note-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(252, 253, 255, 0.95));
  backdrop-filter: blur(15px);
  border-radius: 0;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.12);
  overflow: hidden;
  border: none;
  position: relative;
}

.empty-editor {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  padding: 40px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-editor h3 {
  margin: 0 0 10px 0;
  font-size: 20px;
  font-weight: 700;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  letter-spacing: 0.2px;
}

.empty-editor p {
  margin: 0;
  font-size: 14px;
  opacity: 0.8;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 500;
}

.editor-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-header {
  padding: 28px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.15);
  display: flex;
  align-items: flex-start;
  gap: 18px;
  flex-wrap: wrap;
  min-height: 90px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(248, 250, 255, 0.9));
  backdrop-filter: blur(12px);
  position: relative;
  z-index: 2;
  margin-top: 3px;
}

.title-input {
  flex: 1;
  font-size: 24px;
  font-weight: 700;
  border: none;
  outline: none;
  color: #2c3e50;
  background: transparent;
  padding: 8px 0;
  transition: all 0.3s ease;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  letter-spacing: 0.3px;
}

.title-input::placeholder {
  color: #adb5bd;
}

.editor-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
  width: 100%;
  justify-content: flex-start;
}

.btn-save, .btn-delete, .btn-ai-rewrite, .btn-generate-tags {
  padding: 12px 20px;
  border: 2px solid transparent;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  min-width: 80px;
  text-align: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  letter-spacing: 0.2px;
}

.btn-save::before, .btn-delete::before, .btn-ai-rewrite::before, .btn-generate-tags::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.btn-save:hover::before, .btn-delete:hover::before, .btn-ai-rewrite:hover::before, .btn-generate-tags:hover::before {
  left: 100%;
}

.btn-save {
  background: linear-gradient(135deg, #28a745 0%, #20c997 50%, #17a2b8 100%);
  color: white;
  border: 2px solid transparent;
  font-weight: 700;
  min-width: 90px;
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
}

.btn-save:hover:not(:disabled) {
  background: linear-gradient(135deg, #218838 0%, #1ea085 50%, #138496 100%);
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 10px 30px rgba(40, 167, 69, 0.45), 0 4px 15px rgba(32, 201, 151, 0.2);
}

.btn-save.saving {
  background: #6c757d;
  border-color: #6c757d;
  cursor: not-allowed;
}

.btn-delete {
  background: linear-gradient(135deg, #dc3545 0%, #e83e8c 50%, #fd7e14 100%);
  color: white;
  border: 2px solid transparent;
  box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);
}

.btn-delete:hover:not(:disabled) {
  background: linear-gradient(135deg, #c82333 0%, #d6336c 50%, #e8590c 100%);
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 10px 30px rgba(220, 53, 69, 0.45), 0 4px 15px rgba(232, 62, 140, 0.2);
}

.btn-ai-rewrite {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-ai-rewrite:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 50%, #ee82e9 100%);
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.45), 0 4px 15px rgba(240, 147, 251, 0.2);
}

.btn-generate-tags {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #fd79a8 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(240, 147, 251, 0.3);
}

.btn-generate-tags:hover:not(:disabled) {
  background: linear-gradient(135deg, #ee82e9 0%, #f3455a 50%, #fc6c9d 100%);
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 10px 30px rgba(240, 147, 251, 0.45), 0 4px 15px rgba(245, 87, 108, 0.2);
}

.btn-save:disabled, .btn-delete:disabled, .btn-ai-rewrite:disabled, .btn-generate-tags:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.editor-meta {
  padding: 18px 24px;
  background: rgba(248, 249, 250, 0.8);
  backdrop-filter: blur(5px);
  border-bottom: 1px solid rgba(233, 236, 239, 0.3);
  display: flex;
  gap: 30px;
  align-items: center;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.meta-label {
  color: #6c757d;
  font-weight: 600;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.meta-value {
  color: #495057;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 500;
}

.tags-input {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.tag {
  background: linear-gradient(135deg, #e9ecef 0%, #f8f9fa 100%);
  color: #495057;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  border: 1px solid rgba(233, 236, 239, 0.5);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 600;
}

.tag:hover {
  background: linear-gradient(135deg, #dee2e6 0%, #e9ecef 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.tag-remove {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tag-remove:hover {
  color: #dc3545;
}

.tag-input {
  border: none;
  outline: none;
  background: rgba(255, 255, 255, 0.8);
  font-size: 12px;
  min-width: 80px;
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid rgba(233, 236, 239, 0.5);
  transition: all 0.3s ease;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 500;
}

.tag-input:focus {
  background: rgba(255, 255, 255, 0.95);
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.tag-input::placeholder {
  color: #adb5bd;
}

.editor-content {
  flex: 1;
  padding: 24px;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(3px);
}

.content-textarea {
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  font-size: 16px;
  line-height: 1.7;
  color: #2c3e50;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 400;
  background: transparent;
  padding: 16px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.content-textarea:focus {
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.content-textarea::placeholder {
  color: #adb5bd;
}

/* 滚动条样式 */
.content-textarea::-webkit-scrollbar {
  width: 6px;
}

.content-textarea::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.content-textarea::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.content-textarea::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .note-editor {
    /* 移动端触摸优化 */
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
  }
  
  .editor-header {
    padding: 16px;
    min-height: auto;
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    /* 移动端头部优化 */
    position: sticky;
    top: 0;
    z-index: 10;
  }
  
  .title-input {
    font-size: 18px;
    padding: 12px 0;
    margin-bottom: 0;
    min-height: 44px;
    /* 移动端输入框优化 */
    -webkit-appearance: none;
    touch-action: manipulation;
    font-size: 16px; /* 防止iOS缩放 */
  }
  
  .editor-actions {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .btn-save, .btn-delete, .btn-ai-rewrite, .btn-generate-tags {
    padding: 12px 16px;
    font-size: 14px;
    min-width: 100px;
    min-height: 44px;
    flex: 1;
    /* 移动端按钮优化 */
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
    border-radius: 8px;
    font-weight: 600;
  }
  
  .editor-meta {
    padding: 12px 16px;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    /* 移动端元数据区域优化 */
    background: rgba(248, 249, 250, 0.95);
  }
  
  .meta-item {
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .tags-input {
    width: 100%;
    min-height: 44px;
  }
  
  .tag {
    padding: 8px 12px;
    font-size: 13px;
    min-height: 32px;
    /* 移动端标签优化 */
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
  }
  
  .tag-input {
    padding: 8px 12px;
    font-size: 14px;
    min-width: 120px;
    min-height: 32px;
    /* 移动端标签输入优化 */
    -webkit-appearance: none;
    touch-action: manipulation;
  }
  
  .tag-remove {
    min-width: 24px;
    min-height: 24px;
    font-size: 16px;
    /* 移动端删除按钮优化 */
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
  }
  
  .editor-content {
    padding: 16px;
    flex: 1;
    /* 移动端内容区域优化 */
    -webkit-overflow-scrolling: touch;
  }
  
  .content-textarea {
    font-size: 16px; /* 防止iOS缩放 */
    line-height: 1.6;
    padding: 16px;
    min-height: 300px;
    /* 移动端文本区域优化 */
    -webkit-appearance: none;
    touch-action: manipulation;
    resize: none;
  }
  
  .empty-editor {
    padding: 32px 20px;
    /* 移动端空状态优化 */
    text-align: center;
  }
  
  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }
  
  .empty-editor h3 {
    font-size: 18px;
    margin-bottom: 8px;
    line-height: 1.3;
  }
  
  .empty-editor p {
    font-size: 14px;
    line-height: 1.4;
  }
}

@media (max-width: 480px) {
  .editor-header {
    padding: 12px;
  }
  
  .title-input {
    font-size: 16px;
    padding: 10px 0;
  }
  
  .editor-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .btn-save, .btn-delete, .btn-ai-rewrite, .btn-generate-tags {
    width: 100%;
    justify-content: center;
    min-width: auto;
    padding: 14px 20px;
    font-size: 15px;
  }
  
  .editor-meta {
    padding: 10px 12px;
  }
  
  .editor-content {
    padding: 12px;
  }
  
  .content-textarea {
    padding: 12px;
    min-height: 250px;
  }
  
  .empty-editor {
    padding: 24px 16px;
  }
  
  .empty-icon {
    font-size: 40px;
    margin-bottom: 12px;
  }
  
  .empty-editor h3 {
    font-size: 16px;
  }
  
  .empty-editor p {
    font-size: 13px;
  }
}

/* 分类选择器样式 */
.categories-input {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  min-height: 32px;
}

.category-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: #667eea;
  color: white;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.category-icon {
  font-size: 14px;
}

.category-remove {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0;
  margin-left: 4px;
  font-size: 14px;
  font-weight: bold;
  opacity: 0.8;
  transition: opacity 0.2s ease;
}

.category-remove:hover {
  opacity: 1;
}

.category-selector {
  position: relative;
}

.btn-add-category {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #f8f9fa;
  border: 2px dashed #dee2e6;
  border-radius: 16px;
  color: #6c757d;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-add-category:hover:not(:disabled) {
  background: #e9ecef;
  border-color: #adb5bd;
  color: #495057;
}

.btn-add-category:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.category-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
  margin-top: 4px;
}

.category-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid #f8f9fa;
}

.category-option:last-child {
  border-bottom: none;
}

.category-option:hover {
  background: #f8f9fa;
}

.category-option .category-icon {
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.category-option .category-name {
  font-weight: 500;
  color: #2c3e50;
  flex: 1;
}

.category-option .category-description {
  font-size: 12px;
  color: #6c757d;
  max-width: 150px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.no-categories {
  padding: 16px;
  text-align: center;
  color: #6c757d;
  font-size: 14px;
}

.btn-create-category {
  margin-top: 8px;
  padding: 6px 12px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn-create-category:hover {
  background: #5a67d8;
}

/* 移动端分类选择器适配 */
@media (max-width: 480px) {
  .categories-input {
    gap: 6px;
  }
  
  .category-tag {
    padding: 4px 8px;
    font-size: 11px;
  }
  
  .btn-add-category {
    padding: 4px 8px;
    font-size: 11px;
  }
  
  .category-dropdown {
    left: -10px;
    right: -10px;
  }
  
  .category-option {
    padding: 10px;
  }
  
  .category-option .category-description {
    display: none;
  }
}

/* 移动端通用触摸优化 */
@media (max-width: 768px) {
  .note-editor * {
    -webkit-tap-highlight-color: transparent;
  }
  
  .note-editor button,
  .note-editor input,
  .note-editor textarea {
    touch-action: manipulation;
    -webkit-appearance: none;
  }
  
  /* 滚动条移动端优化 */
  .content-textarea::-webkit-scrollbar {
    width: 4px;
  }
  
  .content-textarea::-webkit-scrollbar-track {
    background: transparent;
  }
  
  .content-textarea::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 2px;
  }
  
  .content-textarea::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0.3);
  }
}
</style>