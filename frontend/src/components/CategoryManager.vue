<template>
  <div class="category-manager">
    <!-- 分类管理头部 -->
    <div class="category-header">
      <h2 class="category-title">
        <i class="icon">📁</i>
        分类管理
      </h2>
      <button class="btn-create-category" @click="showCreateDialog = true">
        <i class="icon">➕</i>
        新建分类
      </button>
    </div>

    <!-- 分类列表 -->
    <div class="category-list">
      <div 
        v-for="category in categories" 
        :key="category.id" 
        class="category-item"
        :style="{ borderLeftColor: category.color }"
      >
        <div class="category-info">
          <div class="category-main">
            <span class="category-icon">{{ category.icon }}</span>
            <div class="category-details">
              <h3 class="category-name">{{ category.name }}</h3>
              <p class="category-description">{{ category.description || '暂无描述' }}</p>
            </div>
          </div>
          <div class="category-meta">
            <span class="note-count">{{ category.note_count || 0 }} 篇笔记</span>
            <div class="category-actions">
              <button class="btn-edit" @click="editCategory(category)">
                <i class="icon">✏️</i>
              </button>
              <button class="btn-delete" @click="deleteCategory(category)">
                <i class="icon">🗑️</i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="categories.length === 0" class="empty-state">
        <div class="empty-icon">📂</div>
        <h3>还没有分类</h3>
        <p>创建分类来更好地组织你的笔记</p>
        <button class="btn-create-first" @click="showCreateDialog = true">
          创建第一个分类
        </button>
      </div>
    </div>

    <!-- 创建/编辑分类对话框 -->
    <div v-if="showCreateDialog || showEditDialog" class="dialog-overlay" @click="closeDialogs">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>{{ isEditing ? '编辑分类' : '创建分类' }}</h3>
          <button class="btn-close" @click="closeDialogs">
            <i class="icon">✖️</i>
          </button>
        </div>
        
        <div class="dialog-content">
          <div class="form-group">
            <label>分类名称</label>
            <input 
              v-model="categoryForm.name" 
              type="text" 
              placeholder="请输入分类名称"
              class="form-input"
              maxlength="50"
            >
          </div>
          
          <div class="form-group">
            <label>分类描述</label>
            <textarea 
              v-model="categoryForm.description" 
              placeholder="请输入分类描述（可选）"
              class="form-textarea"
              maxlength="200"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>分类图标</label>
            <div class="icon-selector">
              <div 
                v-for="icon in iconOptions" 
                :key="icon"
                class="icon-option"
                :class="{ active: categoryForm.icon === icon }"
                @click="categoryForm.icon = icon"
              >
                {{ icon }}
              </div>
            </div>
          </div>
          
          <div class="form-group">
            <label>分类颜色</label>
            <div class="color-selector">
              <div 
                v-for="color in colorOptions" 
                :key="color"
                class="color-option"
                :class="{ active: categoryForm.color === color }"
                :style="{ backgroundColor: color }"
                @click="categoryForm.color = color"
              ></div>
            </div>
          </div>
        </div>
        
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeDialogs">取消</button>
          <button class="btn-confirm" @click="saveCategory" :disabled="!categoryForm.name.trim()">
            {{ isEditing ? '保存' : '创建' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { categoryApi } from '../api/category'

export default {
  name: 'CategoryManager',
  setup() {
    const categories = ref([])
    const showCreateDialog = ref(false)
    const showEditDialog = ref(false)
    const isEditing = ref(false)
    const editingCategory = ref(null)
    
    const categoryForm = reactive({
      name: '',
      description: '',
      icon: '📁',
      color: '#667eea'
    })
    
    const iconOptions = [
      '📁', '📂', '📋', '📝', '💼', '🎯', '💡', '🔖',
      '📚', '🎨', '💻', '🔬', '🏠', '🎵', '🍳', '✈️'
    ]
    
    const colorOptions = [
      '#667eea', '#764ba2', '#f093fb', '#4facfe',
      '#43e97b', '#38ef7d', '#ffecd2', '#fcb69f',
      '#a8edea', '#fed6e3', '#d299c2', '#fef9d7'
    ]
    
    // 获取分类列表
    const loadCategories = async () => {
      try {
        const response = await categoryApi.getCategories()
        categories.value = response.data
      } catch (error) {
        console.error('获取分类列表失败:', error)
      }
    }
    
    // 创建分类
    const createCategory = async () => {
      try {
        await categoryApi.createCategory(categoryForm)
        await loadCategories()
        closeDialogs()
      } catch (error) {
        console.error('创建分类失败:', error)
        alert(error.response?.data?.error || '创建分类失败')
      }
    }
    
    // 更新分类
    const updateCategory = async () => {
      try {
        await categoryApi.updateCategory(editingCategory.value.id, categoryForm)
        await loadCategories()
        closeDialogs()
      } catch (error) {
        console.error('更新分类失败:', error)
        alert(error.response?.data?.error || '更新分类失败')
      }
    }
    
    // 保存分类
    const saveCategory = () => {
      if (isEditing.value) {
        updateCategory()
      } else {
        createCategory()
      }
    }
    
    // 编辑分类
    const editCategory = (category) => {
      isEditing.value = true
      editingCategory.value = category
      categoryForm.name = category.name
      categoryForm.description = category.description || ''
      categoryForm.icon = category.icon
      categoryForm.color = category.color
      showEditDialog.value = true
    }
    
    // 删除分类
    const deleteCategory = async (category) => {
      if (confirm(`确定要删除分类「${category.name}」吗？`)) {
        try {
          await categoryApi.deleteCategory(category.id)
          await loadCategories()
        } catch (error) {
          console.error('删除分类失败:', error)
          alert('删除分类失败')
        }
      }
    }
    
    // 关闭对话框
    const closeDialogs = () => {
      showCreateDialog.value = false
      showEditDialog.value = false
      isEditing.value = false
      editingCategory.value = null
      
      // 重置表单
      categoryForm.name = ''
      categoryForm.description = ''
      categoryForm.icon = '📁'
      categoryForm.color = '#667eea'
    }
    
    onMounted(() => {
      loadCategories()
    })
    
    return {
      categories,
      showCreateDialog,
      showEditDialog,
      isEditing,
      categoryForm,
      iconOptions,
      colorOptions,
      editCategory,
      deleteCategory,
      saveCategory,
      closeDialogs
    }
  }
}
</script>

<style scoped>
.category-manager {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e1e8ed;
}

.category-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.btn-create-category {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-create-category:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.category-item {
  background: white;
  border-radius: 12px;
  border-left: 4px solid #667eea;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.category-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.category-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-main {
  display: flex;
  align-items: center;
  gap: 15px;
  flex: 1;
}

.category-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 10px;
}

.category-details {
  flex: 1;
}

.category-name {
  margin: 0 0 5px 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.category-description {
  margin: 0;
  font-size: 14px;
  color: #7f8c8d;
  line-height: 1.4;
}

.category-meta {
  display: flex;
  align-items: center;
  gap: 15px;
}

.note-count {
  font-size: 12px;
  color: #95a5a6;
  background: #ecf0f1;
  padding: 4px 8px;
  border-radius: 12px;
}

.category-actions {
  display: flex;
  gap: 8px;
}

.btn-edit, .btn-delete {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.btn-edit {
  background: #3498db;
  color: white;
}

.btn-edit:hover {
  background: #2980b9;
  transform: scale(1.1);
}

.btn-delete {
  background: #e74c3c;
  color: white;
}

.btn-delete:hover {
  background: #c0392b;
  transform: scale(1.1);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #2c3e50;
}

.empty-state p {
  margin: 0 0 30px 0;
  font-size: 14px;
}

.btn-create-first {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-create-first:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

/* 对话框样式 */
.dialog-overlay {
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
}

.dialog {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e1e8ed;
  background: #f8f9fa;
}

.dialog-header h3 {
  margin: 0;
  font-size: 18px;
  color: #2c3e50;
}

.btn-close {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.3s ease;
}

.btn-close:hover {
  background: #e9ecef;
}

.dialog-content {
  padding: 20px;
  max-height: 60vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #2c3e50;
}

.form-input, .form-textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: #667eea;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.icon-selector, .color-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.icon-option {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 18px;
}

.icon-option:hover, .icon-option.active {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.color-option {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  border: 3px solid transparent;
  transition: all 0.3s ease;
}

.color-option:hover, .color-option.active {
  border-color: #2c3e50;
  transform: scale(1.1);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #e1e8ed;
  background: #f8f9fa;
}

.btn-cancel, .btn-confirm {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel {
  background: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background: #5a6268;
}

.btn-confirm {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-confirm:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.icon {
  font-style: normal;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .category-manager {
    padding: 15px;
  }
  
  .category-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .category-title {
    justify-content: center;
  }
  
  .category-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .category-meta {
    width: 100%;
    justify-content: space-between;
  }
  
  .dialog {
    width: 95%;
    margin: 20px;
  }
  
  .icon-selector, .color-selector {
    justify-content: center;
  }
}
</style>