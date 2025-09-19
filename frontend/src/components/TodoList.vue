<template>
  <div class="todo-list">
    <div class="todo-header">
      <h3 class="todo-title">📝 待办事项</h3>
      <div class="todo-stats">
        <span class="stat-item">{{ completedCount }}/{{ todos.length }} 已完成</span>
        <span class="stat-item">{{ highPriorityCount }} 高优先级</span>
      </div>
    </div>

    <div class="todo-input-section">
      <div class="input-group">
        <input 
          v-model="newTodoText"
          @keyup.enter="addTodo"
          type="text" 
          placeholder="添加新的待办事项..."
          class="todo-input"
        />
        <select v-model="newTodoPriority" class="priority-select">
          <option value="low">低优先级</option>
          <option value="medium">中优先级</option>
          <option value="high">高优先级</option>
        </select>
        <input 
          v-model="newTodoDueDate"
          type="date"
          class="date-input"
          title="截止日期"
        />
        <button @click="addTodo" class="add-btn" :disabled="!newTodoText.trim()">
          <span>+</span>
        </button>
      </div>
    </div>

    <div class="filter-section">
      <div class="filter-buttons">
        <button 
          @click="filterType = 'all'"
          :class="{ active: filterType === 'all' }"
          class="filter-btn"
        >
          全部 ({{ todos.length }})
        </button>
        <button 
          @click="filterType = 'pending'"
          :class="{ active: filterType === 'pending' }"
          class="filter-btn"
        >
          待完成 ({{ pendingCount }})
        </button>
        <button 
          @click="filterType = 'completed'"
          :class="{ active: filterType === 'completed' }"
          class="filter-btn"
        >
          已完成 ({{ completedCount }})
        </button>
      </div>
    </div>

    <div class="todo-items">
      <div 
        v-for="todo in filteredTodos" 
        :key="todo.id"
        class="todo-item"
        :class="{ 
          'completed': todo.completed,
          'high-priority': todo.priority === 'high',
          'medium-priority': todo.priority === 'medium',
          'overdue': isOverdue(todo.dueDate)
        }"
      >
        <div class="todo-checkbox">
          <input 
            type="checkbox" 
            :id="'todo-' + todo.id"
            v-model="todo.completed"
            @change="toggleTodo(todo.id)"
          />
          <label :for="'todo-' + todo.id" class="checkbox-label"></label>
        </div>
        
        <div class="todo-content" @click="startEdit(todo.id)">
          <input 
            v-if="editingId === todo.id"
            v-model="editingText"
            @blur="saveEdit(todo.id)"
            @keyup.enter="saveEdit(todo.id)"
            @keyup.esc="cancelEdit"
            class="todo-edit-input"
            ref="editInput"
          />
          <div v-else class="todo-info">
            <span 
              class="todo-text"
              :class="{ 'completed-text': todo.completed }"
            >
              {{ todo.text }}
            </span>
            <div class="todo-meta">
              <span class="priority-badge" :class="todo.priority">
                {{ getPriorityText(todo.priority) }}
              </span>
              <span v-if="todo.dueDate" class="due-date" :class="{ 'overdue': isOverdue(todo.dueDate) }">
                📅 {{ formatDate(todo.dueDate) }}
              </span>
            </div>
          </div>
        </div>
        
        <div class="todo-actions">
          <button 
            @click="deleteTodo(todo.id)"
            class="delete-btn"
            title="删除"
          >
            ×
          </button>
        </div>
      </div>
    </div>

    <div v-if="filteredTodos.length === 0 && todos.length === 0" class="empty-state">
      <div class="empty-icon">📋</div>
      <p class="empty-text">暂无待办事项</p>
      <p class="empty-hint">在上方输入框中添加你的第一个待办事项吧！</p>
    </div>
    
    <div v-else-if="filteredTodos.length === 0 && todos.length > 0" class="empty-filtered-state">
      <div class="empty-icon">🔍</div>
      <p class="empty-text">当前筛选条件下暂无待办事项</p>
      <p class="empty-hint">试试切换到其他筛选条件查看</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TodoList',
  data() {
    return {
      todos: [],
      newTodoText: '',
      newTodoPriority: 'medium',
      newTodoDueDate: '',
      editingId: null,
      editingText: '',
      filterType: 'all',
      nextId: 1
    }
  },
  computed: {
    completedCount() {
      return this.todos.filter(todo => todo.completed).length;
    },
    pendingCount() {
      return this.todos.filter(todo => !todo.completed).length;
    },
    highPriorityCount() {
      return this.todos.filter(todo => todo.priority === 'high' && !todo.completed).length;
    },
    filteredTodos() {
      let filtered = this.todos;
      if (this.filterType === 'completed') {
        filtered = this.todos.filter(todo => todo.completed);
      } else if (this.filterType === 'pending') {
        filtered = this.todos.filter(todo => !todo.completed);
      }
      // 按优先级和截止日期排序
      return filtered.sort((a, b) => {
        if (a.completed !== b.completed) {
          return a.completed ? 1 : -1;
        }
        const priorityOrder = { high: 3, medium: 2, low: 1 };
        if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
          return priorityOrder[b.priority] - priorityOrder[a.priority];
        }
        if (a.dueDate && b.dueDate) {
          return new Date(a.dueDate) - new Date(b.dueDate);
        }
        return a.dueDate ? -1 : (b.dueDate ? 1 : 0);
      });
    }
  },
  mounted() {
    this.loadTodos();
  },
  methods: {
    addTodo() {
      if (!this.newTodoText.trim()) return;
      
      const newTodo = {
        id: this.nextId++,
        text: this.newTodoText.trim(),
        completed: false,
        priority: this.newTodoPriority,
        dueDate: this.newTodoDueDate || null,
        createdAt: new Date().toISOString()
      };
      
      this.todos.push(newTodo);
      this.saveTodos();
      
      this.newTodoText = '';
      this.newTodoPriority = 'medium';
      this.newTodoDueDate = '';
    },
    
    toggleTodo(id) {
      const todoIndex = this.todos.findIndex(t => t.id === id);
      if (todoIndex !== -1) {
        this.$set(this.todos, todoIndex, {
          ...this.todos[todoIndex],
          completed: !this.todos[todoIndex].completed
        });
        this.saveTodos();
      }
    },
    
    deleteTodo(id) {
      this.todos = this.todos.filter(t => t.id !== id);
      this.saveTodos();
    },
    
    startEdit(id) {
      const todo = this.todos.find(t => t.id === id);
      if (todo && !todo.completed) {
        this.editingId = id;
        this.editingText = todo.text;
        this.$nextTick(() => {
          const input = this.$refs.editInput?.[0];
          if (input) {
            input.focus();
            input.select();
          }
        });
      }
    },
    
    saveEdit(id) {
      if (!this.editingText.trim()) {
        this.cancelEdit();
        return;
      }
      
      const todo = this.todos.find(t => t.id === id);
      if (todo) {
        todo.text = this.editingText.trim();
        this.saveTodos();
      }
      
      this.editingId = null;
      this.editingText = '';
    },
    
    cancelEdit() {
      this.editingId = null;
      this.editingText = '';
    },
    
    // 数据持久化方法
    saveTodos() {
      try {
        localStorage.setItem('todos', JSON.stringify(this.todos));
        localStorage.setItem('nextId', this.nextId.toString());
      } catch (error) {
        console.error('保存待办事项失败:', error);
      }
    },
    
    loadTodos() {
      try {
        const savedTodos = localStorage.getItem('todos');
        const savedNextId = localStorage.getItem('nextId');
        
        if (savedTodos) {
          this.todos = JSON.parse(savedTodos);
        } else {
          // 初始化示例数据
          this.todos = [
            { 
              id: 1, 
              text: '完成项目文档', 
              completed: false, 
              priority: 'high',
              dueDate: new Date(Date.now() + 86400000).toISOString().split('T')[0],
              createdAt: new Date().toISOString()
            },
            { 
              id: 2, 
              text: '准备会议材料', 
              completed: true, 
              priority: 'medium',
              dueDate: null,
              createdAt: new Date().toISOString()
            },
            { 
              id: 3, 
              text: '回复重要邮件', 
              completed: false, 
              priority: 'low',
              dueDate: null,
              createdAt: new Date().toISOString()
            }
          ];
          this.nextId = 4;
          this.saveTodos();
        }
        
        if (savedNextId) {
          this.nextId = parseInt(savedNextId);
        }
      } catch (error) {
        console.error('加载待办事项失败:', error);
      }
    },
    
    // 工具方法
    getPriorityText(priority) {
      const priorityMap = {
        high: '高',
        medium: '中', 
        low: '低'
      };
      return priorityMap[priority] || '中';
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      const today = new Date();
      const tomorrow = new Date(today);
      tomorrow.setDate(today.getDate() + 1);
      
      if (date.toDateString() === today.toDateString()) {
        return '今天';
      } else if (date.toDateString() === tomorrow.toDateString()) {
        return '明天';
      } else {
        return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
      }
    },
    
    isOverdue(dateString) {
      if (!dateString) return false;
      const dueDate = new Date(dateString);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      dueDate.setHours(0, 0, 0, 0);
      return dueDate < today;
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&display=swap');

.todo-list {
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
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.todo-header {
  padding: 28px 28px 24px 28px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.15);
  margin-bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(248, 250, 255, 0.9));
  backdrop-filter: blur(12px);
  position: relative;
  z-index: 2;
  margin-top: 3px;
}

.todo-title {
  margin: 0 0 18px 0;
  font-size: 1.4rem;
  font-weight: 800;
  color: #2c3e50;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  letter-spacing: 0.3px;
}

.todo-stats {
  display: flex;
  gap: 15px;
}

.stat-item {
  font-size: 0.85rem;
  color: #7f8c8d;
  font-weight: 600;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.todo-input-section {
  margin: 20px 28px;
  padding: 0;
}

.input-group {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.todo-input {
  flex: 1;
  min-width: 200px;
  padding: 12px 16px;
  border: 2px solid rgba(108, 92, 231, 0.2);
  border-radius: 12px;
  font-size: 0.9rem;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
}

.priority-select {
  padding: 12px 14px;
  border: 2px solid rgba(108, 92, 231, 0.2);
  border-radius: 12px;
  font-size: 0.85rem;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 100px;
}

.priority-select:focus {
  outline: none;
  border-color: #6c5ce7;
  box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.1);
}

.date-input {
  padding: 12px 14px;
  border: 2px solid rgba(108, 92, 231, 0.2);
  border-radius: 12px;
  font-size: 0.85rem;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 140px;
}

.date-input:focus {
  outline: none;
  border-color: #6c5ce7;
  box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.1);
}

.todo-input:focus {
  outline: none;
  border-color: #6c5ce7;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.1);
}

.todo-input::placeholder {
  color: #bdc3c7;
  font-weight: 400;
}

.add-btn {
  padding: 14px 18px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  color: white;
  border: none;
  border-radius: 15px;
  font-size: 1.3rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.add-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 50%, #ee82e9 100%);
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.45), 0 4px 15px rgba(240, 147, 251, 0.2);
}

.add-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.filter-section {
  margin: 0 28px 20px 28px;
  padding: 0;
}

.filter-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 8px 16px;
  border: 2px solid rgba(108, 92, 231, 0.2);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.8);
  color: #6c5ce7;
  font-size: 0.8rem;
  font-weight: 600;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.filter-btn:hover {
  background: rgba(108, 92, 231, 0.1);
  border-color: #6c5ce7;
  transform: translateY(-2px);
}

.filter-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.todo-items {
  flex: 1;
  overflow-y: auto;
}

.todo-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 16px 24px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.7), rgba(248, 250, 255, 0.5));
  margin: 2px 8px;
  border-radius: 12px;
  position: relative;
}

.todo-item:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08), rgba(240, 147, 251, 0.05));
  transform: translateX(6px) scale(1.02);
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
}

.todo-item.high-priority {
  border-left: 4px solid #e74c3c;
}

.todo-item.medium-priority {
  border-left: 4px solid #f39c12;
}

.todo-item.overdue {
  background: linear-gradient(135deg, rgba(231, 76, 60, 0.1), rgba(231, 76, 60, 0.05));
}

.todo-checkbox {
  position: relative;
}

.todo-checkbox input[type="checkbox"] {
  opacity: 0;
  position: absolute;
  width: 20px;
  height: 20px;
}

.checkbox-label {
  display: block;
  width: 22px;
  height: 22px;
  border: 2px solid #667eea;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(248, 250, 255, 0.7));
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.todo-checkbox input[type="checkbox"]:checked + .checkbox-label {
  background: linear-gradient(135deg, #28a745 0%, #20c997 50%, #17a2b8 100%);
  border-color: #28a745;
  box-shadow: 0 3px 12px rgba(40, 167, 69, 0.4);
}

.todo-checkbox input[type="checkbox"]:checked + .checkbox-label::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.todo-content {
  flex: 1;
  cursor: pointer;
}

.todo-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.todo-meta {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.priority-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.priority-badge.high {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
}

.priority-badge.medium {
  background: linear-gradient(135deg, #f39c12, #e67e22);
  color: white;
}

.priority-badge.low {
  background: linear-gradient(135deg, #27ae60, #2ecc71);
  color: white;
}

.due-date {
  font-size: 0.75rem;
  color: #7f8c8d;
  font-weight: 500;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.due-date.overdue {
  color: #e74c3c;
  font-weight: 700;
}

.todo-text {
  font-size: 0.9rem;
  color: #2c3e50;
  font-weight: 500;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  line-height: 1.4;
  transition: all 0.3s ease;
}

.completed-text {
  text-decoration: line-through;
  color: #95a5a6;
  opacity: 0.7;
}

.todo-edit-input {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid #6c5ce7;
  border-radius: 6px;
  font-size: 0.9rem;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
  font-weight: 500;
  background: white;
}

.todo-edit-input:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(108, 92, 231, 0.2);
}

.todo-actions {
  opacity: 0;
  transition: opacity 0.3s ease;
}

.todo-item:hover .todo-actions {
  opacity: 1;
}

.delete-btn {
  padding: 6px 10px;
  background: linear-gradient(135deg, #dc3545 0%, #e83e8c 50%, #fd7e14 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0.85;
  box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
}

.delete-btn:hover {
  background: linear-gradient(135deg, #c82333 0%, #d6336c 50%, #e8590c 100%);
  opacity: 1;
  transform: scale(1.1) translateY(-2px);
  box-shadow: 0 6px 20px rgba(220, 53, 69, 0.45), 0 2px 8px rgba(232, 62, 140, 0.2);
}

.empty-state,
.empty-filtered-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-text {
  font-size: 1.1rem;
  color: #7f8c8d;
  margin: 0 0 8px 0;
  font-weight: 600;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.empty-hint {
  font-size: 0.9rem;
  color: #bdc3c7;
  margin: 0;
  font-weight: 400;
  font-family: 'Nunito', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.empty-filtered-state {
  padding: 30px 20px;
}

.empty-filtered-state .empty-text {
  font-size: 1rem;
  color: #6c757d;
}

.empty-filtered-state .empty-hint {
  color: #868e96;
}

/* 滚动条样式 */
.todo-items::-webkit-scrollbar {
  width: 6px;
}

.todo-items::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.todo-items::-webkit-scrollbar-thumb {
  background: rgba(108, 92, 231, 0.3);
  border-radius: 3px;
}

.todo-items::-webkit-scrollbar-thumb:hover {
  background: rgba(108, 92, 231, 0.5);
}
</style>