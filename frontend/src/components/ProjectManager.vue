<template>
  <div class="project-manager">
    <div class="project-manager-header">
      <h2 class="manager-title">
        <i class="fas fa-project-diagram"></i>
        项目管理
      </h2>
      <div class="view-toggle">
        <button 
          :class="['toggle-btn', { active: currentView === 'list' }]"
          @click="currentView = 'list'"
        >
          列表视图
        </button>
        <button 
          :class="['toggle-btn', { active: currentView === 'calendar' }]"
          @click="currentView = 'calendar'"
        >
          日历视图
        </button>
      </div>
      <button class="close-btn" @click="$emit('close')" title="关闭">
        <i class="fas fa-times"></i>
      </button>
    </div>
    
    <div class="project-manager-content">
      <!-- 列表视图 -->
      <template v-if="currentView === 'list'">
        <!-- 左侧项目列表 -->
        <div class="project-list-panel">
        <div class="panel-header">
          <h3>项目列表</h3>
          <button class="add-project-btn" @click="showAddProject = true" title="新建项目">
            <i class="fas fa-plus"></i>
          </button>
        </div>
        
        <div class="project-list">
          <div 
            v-for="project in projects" 
            :key="project.id"
            class="project-item"
            :class="{ active: selectedProjectId === project.id }"
            @click="selectProject(project.id)"
          >
            <div class="project-info">
              <h4 class="project-name">{{ project.name }}</h4>
              <span class="task-count">{{ getTaskCount(project.id) }} 个任务</span>
            </div>
            <div class="project-actions">
              <button 
                class="edit-btn" 
                @click.stop="editProject(project)"
                title="编辑项目"
              >
                <i class="fas fa-edit"></i>
              </button>
              <button 
                class="delete-btn" 
                @click.stop="deleteProject(project.id)"
                title="删除项目"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
          
          <div v-if="projects.length === 0" class="empty-state">
            <i class="fas fa-folder-open"></i>
            <p>暂无项目</p>
            <p class="empty-hint">点击右上角 + 号创建第一个项目</p>
          </div>
        </div>
        </div>
        
        <!-- 右侧任务列表 -->
        <div class="task-list-panel">
        <div class="panel-header">
          <h3>{{ selectedProject ? selectedProject.name : '选择项目' }}</h3>
          <button 
            v-if="selectedProject"
            class="add-task-btn" 
            @click="showAddTask = true"
            title="新建任务"
          >
            <i class="fas fa-plus"></i>
          </button>
        </div>
        
        <div class="task-list" v-if="selectedProject">
          <div 
            v-for="task in selectedProjectTasks" 
            :key="task.id"
            class="task-item"
            :class="{ completed: task.is_completed }"
          >
            <div class="task-checkbox">
              <input 
                type="checkbox" 
                :checked="task.is_completed"
                @change="toggleTaskComplete(task.id)"
              >
            </div>
            <div class="task-content">
              <h4 class="task-title" :class="{ completed: task.is_completed }">
                {{ task.title }}
              </h4>
              <p class="task-description" v-if="task.description">
                {{ task.description }}
              </p>
              <div class="task-meta">
                <span v-if="task.deadline" class="task-deadline">
                  <i class="fas fa-calendar"></i>
                  {{ formatDate(task.deadline) }}
                </span>
              </div>
            </div>
            <div class="task-actions">
              <button 
                class="edit-btn" 
                @click="editTask(task)"
                title="编辑任务"
              >
                <i class="fas fa-edit"></i>
              </button>
              <button 
                class="delete-btn" 
                @click="deleteTask(task.id)"
                title="删除任务"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
          
          <div v-if="selectedProjectTasks.length === 0" class="empty-state">
            <i class="fas fa-tasks"></i>
            <p>暂无任务</p>
            <p class="empty-hint">点击右上角 + 号创建第一个任务</p>
          </div>
        </div>
        
        <div v-else class="no-project-selected">
          <i class="fas fa-arrow-left"></i>
          <p>请从左侧选择一个项目</p>
        </div>
        </div>
      </template>
      
      <!-- 日历视图 -->
      <template v-else-if="currentView === 'calendar'">
        <div class="calendar-panel">
          <TaskCalendar 
            :tasks="allTasks"
            @update-task="updateTaskFromCalendar"
          />
        </div>
      </template>
    </div>
    
    <!-- 新建项目弹窗 -->
    <div v-if="showAddProject" class="modal-overlay" @click="showAddProject = false">
      <div class="modal" @click.stop>
        <h3>{{ editingProject ? '编辑项目' : '新建项目' }}</h3>
        <input 
          v-model="projectForm.name" 
          type="text" 
          placeholder="请输入项目名称"
          class="project-name-input"
          @keyup.enter="saveProject"
        >
        <div class="modal-actions">
          <button class="cancel-btn" @click="cancelProjectEdit">取消</button>
          <button class="save-btn" @click="saveProject" :disabled="!projectForm.name.trim()">保存</button>
        </div>
      </div>
    </div>
    
    <!-- 新建任务弹窗 -->
    <div v-if="showAddTask" class="modal-overlay" @click="showAddTask = false">
      <div class="modal" @click.stop>
        <h3>{{ editingTask ? '编辑任务' : '新建任务' }}</h3>
        <input 
          v-model="taskForm.title" 
          type="text" 
          placeholder="请输入任务标题"
          class="task-input"
        >
        <textarea 
          v-model="taskForm.description" 
          placeholder="任务描述（可选）"
          class="task-textarea"
        ></textarea>
        <input 
          v-model="taskForm.deadline" 
          type="date" 
          class="task-date-input"
        >
        <div class="modal-actions">
          <button class="cancel-btn" @click="cancelTaskEdit">取消</button>
          <button class="save-btn" @click="saveTask" :disabled="!taskForm.title.trim()">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import TaskCalendar from './TaskCalendar.vue'

export default {
  name: 'ProjectManager',
  components: {
    TaskCalendar
  },
  data() {
    return {
      currentView: 'list',
      projects: [],
      tasks: [],
      selectedProjectId: null,
      showAddProject: false,
      showAddTask: false,
      editingProject: null,
      editingTask: null,
      projectForm: {
        name: ''
      },
      taskForm: {
        title: '',
        description: '',
        deadline: ''
      }
    }
  },
  computed: {
    selectedProject() {
      return this.projects.find(p => p.id === this.selectedProjectId) || null
    },
    selectedProjectTasks() {
      return this.tasks.filter(t => t.projectId === this.selectedProjectId)
    },
    allTasks() {
      return this.tasks
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    loadData() {
      // 从 LocalStorage 加载数据
      const savedProjects = localStorage.getItem('projects')
      const savedTasks = localStorage.getItem('tasks')
      
      this.projects = savedProjects ? JSON.parse(savedProjects) : []
      this.tasks = savedTasks ? JSON.parse(savedTasks) : []
      
      // 如果有项目，默认选择第一个
      if (this.projects.length > 0 && !this.selectedProjectId) {
        this.selectedProjectId = this.projects[0].id
      }
    },
    
    saveData() {
      // 保存到 LocalStorage
      localStorage.setItem('projects', JSON.stringify(this.projects))
      localStorage.setItem('tasks', JSON.stringify(this.tasks))
    },
    
    selectProject(projectId) {
      this.selectedProjectId = projectId
    },
    
    editProject(project) {
      this.editingProject = project
      this.projectForm.name = project.name
      this.showAddProject = true
    },
    
    saveProject() {
      if (!this.projectForm.name.trim()) return
      
      if (this.editingProject) {
        // 编辑项目
        const index = this.projects.findIndex(p => p.id === this.editingProject.id)
        if (index > -1) {
          this.projects[index].name = this.projectForm.name.trim()
        }
      } else {
        // 新建项目
        const newProject = {
          id: Date.now().toString(),
          name: this.projectForm.name.trim()
        }
        this.projects.push(newProject)
        this.selectedProjectId = newProject.id
      }
      
      this.saveData()
      this.cancelProjectEdit()
    },
    
    cancelProjectEdit() {
      this.showAddProject = false
      this.editingProject = null
      this.projectForm.name = ''
    },
    
    deleteProject(projectId) {
      if (confirm('确定要删除这个项目吗？项目下的所有任务也会被删除。')) {
        // 删除项目
        this.projects = this.projects.filter(p => p.id !== projectId)
        // 删除项目下的所有任务
        this.tasks = this.tasks.filter(t => t.projectId !== projectId)
        
        // 如果删除的是当前选中的项目，重新选择
        if (this.selectedProjectId === projectId) {
          this.selectedProjectId = this.projects.length > 0 ? this.projects[0].id : null
        }
        
        this.saveData()
      }
    },
    
    editTask(task) {
      this.editingTask = task
      this.taskForm.title = task.title
      this.taskForm.description = task.description || ''
      this.taskForm.deadline = task.deadline || ''
      this.showAddTask = true
    },
    
    saveTask() {
      if (!this.taskForm.title.trim()) return
      
      if (this.editingTask) {
        // 编辑任务
        const index = this.tasks.findIndex(t => t.id === this.editingTask.id)
        if (index > -1) {
          this.tasks[index] = {
            ...this.tasks[index],
            title: this.taskForm.title.trim(),
            description: this.taskForm.description.trim(),
            deadline: this.taskForm.deadline
          }
        }
      } else {
        // 新建任务
        const newTask = {
          id: Date.now().toString(),
          projectId: this.selectedProjectId,
          title: this.taskForm.title.trim(),
          description: this.taskForm.description.trim(),
          deadline: this.taskForm.deadline,
          is_completed: false
        }
        this.tasks.push(newTask)
      }
      
      this.saveData()
      this.cancelTaskEdit()
    },
    
    cancelTaskEdit() {
      this.showAddTask = false
      this.editingTask = null
      this.taskForm = {
        title: '',
        description: '',
        deadline: ''
      }
    },
    
    deleteTask(taskId) {
      if (confirm('确定要删除这个任务吗？')) {
        this.tasks = this.tasks.filter(t => t.id !== taskId)
        this.saveData()
      }
    },
    
    toggleTaskComplete(taskId) {
      const task = this.tasks.find(t => t.id === taskId)
      if (task) {
        task.is_completed = !task.is_completed
        this.saveData()
      }
    },
    
    getTaskCount(projectId) {
      return this.tasks.filter(t => t.projectId === projectId).length
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    },
    
    updateTaskFromCalendar(updatedTask) {
      const index = this.tasks.findIndex(t => t.id === updatedTask.id)
      if (index > -1) {
        this.tasks[index] = { ...this.tasks[index], ...updatedTask }
        this.saveData()
      }
    }
  }
}
</script>

<style scoped>
.project-manager {
  width: 100%;
  height: 100%;
  background: white;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.project-manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.view-toggle {
  display: flex;
  gap: 8px;
}

.toggle-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.toggle-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.toggle-btn.active {
  background: white;
  color: #667eea;
  border-color: white;
}

.calendar-panel {
  flex: 1;
  padding: 20px;
  overflow: auto;
}

.manager-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.project-manager-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.project-list-panel,
.task-list-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.project-list-panel {
  border-right: 1px solid #e5e7eb;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}

.add-project-btn,
.add-task-btn {
  background: #ff9999;
  border: 2px solid #fff;
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-size: 18px;
  font-weight: bold;
  box-shadow: 0 3px 6px rgba(255, 153, 153, 0.3);
}

.add-project-btn:hover,
.add-task-btn:hover {
  background: #ff7777;
  transform: scale(1.1);
  box-shadow: 0 5px 12px rgba(255, 119, 119, 0.4);
  border-color: #fff;
}

.project-list,
.task-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.project-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.project-item:hover {
  background: #f3f4f6;
}

.project-item.active {
  background: #eff6ff;
  border-color: #3b82f6;
}

.project-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.task-count {
  font-size: 12px;
  color: #6b7280;
}

.project-actions {
  display: flex;
  gap: 4px;
  opacity: 1;
  transition: opacity 0.2s;
}

.project-item:hover .project-actions {
  opacity: 1;
}

.edit-btn,
.delete-btn {
  background: none;
  border: none;
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  min-width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.edit-btn {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  color: #475569;
}

.edit-btn:hover {
  background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
  color: #334155;
}

.delete-btn {
  background: linear-gradient(135deg, #fef3f2 0%, #fee2e2 100%);
  color: #dc2626;
}

.delete-btn:hover {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #b91c1c;
}

.task-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  margin-bottom: 4px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
}

.task-item:hover {
  border-color: #d1d5db;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.task-item.completed {
  opacity: 0.6;
}

.task-checkbox input {
  margin: 0;
  cursor: pointer;
}

.task-content {
  flex: 1;
}

.task-title {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.task-title.completed {
  text-decoration: line-through;
}

.task-description {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #6b7280;
  line-height: 1.4;
}

.task-meta {
  display: flex;
  gap: 12px;
}

.task-deadline {
  font-size: 12px;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 4px;
}

.task-actions {
  display: flex;
  gap: 4px;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.task-item:hover .task-actions {
  opacity: 1;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  margin: 8px 0;
}

.empty-hint {
  font-size: 12px;
  opacity: 0.7;
}

.no-project-selected {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6b7280;
}

.no-project-selected i {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.modal-overlay {
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

.modal {
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: 400px;
  max-width: 90vw;
}

.modal h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #374151;
}

.project-name-input,
.task-input,
.task-textarea,
.task-date-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  margin-bottom: 12px;
  box-sizing: border-box;
}

.task-textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: 16px;
}

.cancel-btn,
.save-btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.cancel-btn {
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  color: #374151;
}

.cancel-btn:hover {
  background: #e5e7eb;
}

.save-btn {
  background: #3b82f6;
  border: 1px solid #3b82f6;
  color: white;
}

.save-btn:hover:not(:disabled) {
  background: #2563eb;
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .project-manager-content {
    flex-direction: column;
  }
  
  .project-list-panel,
  .task-list-panel {
    min-height: 300px;
  }
  
  .project-list-panel {
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
  }
  
  .project-item {
    padding: 16px;
  }
  
  .project-actions {
    gap: 8px;
  }
  
  .edit-btn,
  .delete-btn {
    padding: 8px 12px;
    min-width: 40px;
    height: 40px;
    font-size: 16px;
  }
  
  .task-actions {
    gap: 8px;
  }
  
  .task-item {
    padding: 16px;
  }
  
  .panel-header {
    padding: 20px;
  }
  
  .add-project-btn,
  .add-task-btn {
    width: 44px;
    height: 44px;
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .project-manager-header {
    padding: 16px 20px;
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .manager-title {
    font-size: 18px;
  }
  
  .view-toggle {
    order: 3;
    width: 100%;
    justify-content: center;
  }
  
  .toggle-btn {
    flex: 1;
    max-width: 120px;
  }
  
  .project-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .project-actions {
    align-self: flex-end;
    gap: 12px;
  }
  
  .edit-btn,
  .delete-btn {
    padding: 10px 16px;
    min-width: 48px;
    height: 48px;
    border-radius: 8px;
    font-size: 18px;
  }
  
  .task-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .task-actions {
    align-self: flex-end;
    gap: 12px;
  }
  
  .modal {
    margin: 20px;
    padding: 20px;
  }
}
</style>