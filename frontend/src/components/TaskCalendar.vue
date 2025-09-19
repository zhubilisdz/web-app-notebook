<template>
  <div class="task-calendar">
    <div class="calendar-header">
      <button @click="previousMonth" class="nav-btn">&lt;</button>
      <h3>{{ currentMonthYear }}</h3>
      <button @click="nextMonth" class="nav-btn">&gt;</button>
    </div>
    
    <div class="calendar-grid">
      <div class="weekday-header">
        <div v-for="day in weekdays" :key="day" class="weekday">{{ day }}</div>
      </div>
      
      <div class="calendar-body">
        <div 
          v-for="date in calendarDates" 
          :key="date.key"
          :class="[
            'calendar-date',
            { 
              'other-month': !date.isCurrentMonth,
              'today': date.isToday,
              'has-tasks': date.tasks.length > 0
            }
          ]"
          @click="selectDate(date)"
        >
          <span class="date-number">{{ date.day }}</span>
          <div v-if="date.tasks.length > 0" class="task-indicators">
            <div 
              v-for="task in date.tasks.slice(0, 3)" 
              :key="task.id"
              :class="[
                'task-dot',
                { 'completed': task.completed }
              ]"
              :title="task.title"
            ></div>
            <div v-if="date.tasks.length > 3" class="more-tasks">+{{ date.tasks.length - 3 }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 选中日期的任务详情 -->
    <div v-if="selectedDate" class="selected-date-tasks">
      <h4>{{ formatSelectedDate }} 的任务</h4>
      <div v-if="selectedDate.tasks.length === 0" class="no-tasks">
        暂无任务
      </div>
      <div v-else class="task-list">
        <div 
          v-for="task in selectedDate.tasks" 
          :key="task.id"
          :class="['task-item', { 'completed': task.completed }]"
        >
          <input 
            type="checkbox" 
            v-model="task.completed"
            @change="updateTaskStatus(task)"
          >
          <span class="task-title">{{ task.title }}</span>
          <span v-if="task.deadline" class="task-due">{{ formatTime(task.deadline) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TaskCalendar',
  props: {
    tasks: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      currentDate: new Date(),
      selectedDate: null,
      weekdays: ['日', '一', '二', '三', '四', '五', '六']
    }
  },
  computed: {
    currentMonthYear() {
      return `${this.currentDate.getFullYear()}年${this.currentDate.getMonth() + 1}月`
    },
    formatSelectedDate() {
      if (!this.selectedDate) return ''
      return `${this.selectedDate.year}年${this.selectedDate.month}月${this.selectedDate.day}日`
    },
    calendarDates() {
      const year = this.currentDate.getFullYear()
      const month = this.currentDate.getMonth()
      const today = new Date()
      
      // 获取当月第一天和最后一天
      const firstDay = new Date(year, month, 1)
      const lastDay = new Date(year, month + 1, 0)
      
      // 获取日历开始日期（包含上月末尾几天）
      const startDate = new Date(firstDay)
      startDate.setDate(startDate.getDate() - firstDay.getDay())
      
      // 获取日历结束日期（包含下月开头几天）
      const endDate = new Date(lastDay)
      const remainingDays = 6 - lastDay.getDay()
      endDate.setDate(endDate.getDate() + remainingDays)
      
      const dates = []
      const currentDateIter = new Date(startDate)
      
      while (currentDateIter <= endDate) {
        const dateStr = this.formatDateString(currentDateIter)
        const dayTasks = this.getTasksForDate(currentDateIter)
        
        dates.push({
          key: dateStr,
          day: currentDateIter.getDate(),
          month: currentDateIter.getMonth() + 1,
          year: currentDateIter.getFullYear(),
          date: new Date(currentDateIter),
          isCurrentMonth: currentDateIter.getMonth() === month,
          isToday: this.isSameDate(currentDateIter, today),
          tasks: dayTasks
        })
        
        currentDateIter.setDate(currentDateIter.getDate() + 1)
      }
      
      return dates
    }
  },
  methods: {
    previousMonth() {
      this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() - 1, 1)
      this.selectedDate = null
    },
    nextMonth() {
      this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 1)
      this.selectedDate = null
    },
    selectDate(date) {
      this.selectedDate = date
    },
    getTasksForDate(date) {
      return this.tasks.filter(task => {
        if (!task.deadline) return false
        const taskDate = new Date(task.deadline)
        return this.isSameDate(taskDate, date)
      })
    },
    isSameDate(date1, date2) {
      return date1.getFullYear() === date2.getFullYear() &&
             date1.getMonth() === date2.getMonth() &&
             date1.getDate() === date2.getDate()
    },
    formatDateString(date) {
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    },
    formatTime(dateStr) {
      const date = new Date(dateStr)
      return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    },
    updateTaskStatus(task) {
      this.$emit('update-task', task)
    }
  }
}
</script>

<style scoped>
.task-calendar {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.calendar-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.nav-btn {
  background: #f0f0f0;
  border: none;
  border-radius: 6px;
  width: 32px;
  height: 32px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: #666;
  transition: all 0.2s;
}

.nav-btn:hover {
  background: #e0e0e0;
  color: #333;
}

.calendar-grid {
  width: 100%;
}

.weekday-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  margin-bottom: 8px;
}

.weekday {
  text-align: center;
  padding: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #666;
  background: #f8f9fa;
}

.calendar-body {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: #e9ecef;
  border-radius: 8px;
  overflow: hidden;
}

.calendar-date {
  background: white;
  min-height: 80px;
  padding: 8px;
  cursor: pointer;
  position: relative;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
}

.calendar-date:hover {
  background: #f8f9fa;
}

.calendar-date.other-month {
  background: #f8f9fa;
  color: #ccc;
}

.calendar-date.today {
  background: #e3f2fd;
  border: 2px solid #2196f3;
}

.calendar-date.has-tasks {
  background: #fff3e0;
}

.calendar-date.has-tasks.today {
  background: #e1f5fe;
}

.date-number {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.task-indicators {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  margin-top: auto;
}

.task-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ff9800;
  flex-shrink: 0;
}

.task-dot.completed {
  background: #4caf50;
}

.more-tasks {
  font-size: 10px;
  color: #666;
  margin-left: 2px;
}

.selected-date-tasks {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.selected-date-tasks h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #333;
}

.no-tasks {
  color: #999;
  font-style: italic;
  text-align: center;
  padding: 20px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  transition: all 0.2s;
}

.task-item:hover {
  background: #e9ecef;
}

.task-item.completed {
  opacity: 0.6;
}

.task-item.completed .task-title {
  text-decoration: line-through;
}

.task-title {
  flex: 1;
  font-size: 14px;
}

.task-due {
  font-size: 12px;
  color: #666;
  background: #e3f2fd;
  padding: 2px 6px;
  border-radius: 4px;
}
</style>