<template>
  <div class="pomodoro-container">
    <div class="pomodoro-header">
      <div class="header-content">
        <div class="pomodoro-icon">🍅</div>
        <div class="header-text">
          <h3>番茄钟</h3>
          <p>专注时间管理</p>
        </div>
      </div>
      <button class="close-btn" @click="$emit('close')">
        <i class="fas fa-times"></i>
      </button>
    </div>
    
    <div class="timer-display">
      <div class="timer-circle">
        <svg class="progress-ring" width="200" height="200">
          <circle
            class="progress-ring-background"
            cx="100"
            cy="100"
            r="90"
          />
          <circle
            class="progress-ring-progress"
            cx="100"
            cy="100"
            r="90"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="strokeDashoffset"
          />
        </svg>
        <div class="timer-content">
          <div class="time-display">{{ formattedTime }}</div>
          <div class="session-type">{{ currentSessionName }}</div>
        </div>
      </div>
    </div>
    
    <div class="timer-controls">
      <button 
        class="control-btn primary"
        @click="toggleTimer"
        :disabled="timeRemaining === 0"
      >
        <i :class="isRunning ? 'fas fa-pause' : 'fas fa-play'"></i>
        {{ isRunning ? '暂停' : '开始' }}
      </button>
      
      <button class="control-btn secondary" @click="resetTimer">
        <i class="fas fa-redo"></i>
        重置
      </button>
      
      <button class="control-btn secondary" @click="skipSession">
        <i class="fas fa-forward"></i>
        跳过
      </button>
    </div>
    
    <div class="session-info">
      <div class="session-counter">
        <div class="counter-item">
          <span class="counter-number">{{ completedPomodoros }}</span>
          <span class="counter-label">已完成</span>
        </div>
        <div class="counter-item">
          <span class="counter-number">{{ totalSessions }}</span>
          <span class="counter-label">总轮次</span>
        </div>
      </div>
    </div>
    
    <div class="settings-section">
      <h4>⚙️ 设置</h4>
      <div class="settings-grid">
        <div class="setting-item">
          <label>专注时间</label>
          <div class="time-input">
            <button @click="adjustTime('work', -1)" :disabled="isRunning">-</button>
            <span>{{ settings.workDuration }}分钟</span>
            <button @click="adjustTime('work', 1)" :disabled="isRunning">+</button>
          </div>
        </div>
        
        <div class="setting-item">
          <label>短休息</label>
          <div class="time-input">
            <button @click="adjustTime('shortBreak', -1)" :disabled="isRunning">-</button>
            <span>{{ settings.shortBreakDuration }}分钟</span>
            <button @click="adjustTime('shortBreak', 1)" :disabled="isRunning">+</button>
          </div>
        </div>
        
        <div class="setting-item">
          <label>长休息</label>
          <div class="time-input">
            <button @click="adjustTime('longBreak', -1)" :disabled="isRunning">-</button>
            <span>{{ settings.longBreakDuration }}分钟</span>
            <button @click="adjustTime('longBreak', 1)" :disabled="isRunning">+</button>
          </div>
        </div>
        
        <div class="setting-item">
          <label>长休息间隔</label>
          <div class="time-input">
            <button @click="adjustTime('longBreakInterval', -1)" :disabled="isRunning">-</button>
            <span>{{ settings.longBreakInterval }}轮</span>
            <button @click="adjustTime('longBreakInterval', 1)" :disabled="isRunning">+</button>
          </div>
        </div>
      </div>
      
      <div class="sound-settings">
        <label class="checkbox-label">
          <input 
            type="checkbox" 
            v-model="settings.soundEnabled"
          >
          <span class="checkmark"></span>
          启用提示音
        </label>
        
        <label class="checkbox-label">
          <input 
            type="checkbox" 
            v-model="settings.autoStartBreaks"
          >
          <span class="checkmark"></span>
          自动开始休息
        </label>
      </div>
    </div>
    
    <div class="stats-section">
      <h4>📊 今日统计</h4>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-number">{{ todayStats.completedPomodoros }}</div>
          <div class="stat-label">完成番茄</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ formatDuration(todayStats.totalFocusTime) }}</div>
          <div class="stat-label">专注时间</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ todayStats.totalBreakTime }}</div>
          <div class="stat-label">休息次数</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PomodoroTimer',
  data() {
    return {
      // 计时器状态
      isRunning: false,
      timeRemaining: 25 * 60, // 25分钟，以秒为单位
      currentSession: 'work', // 'work', 'shortBreak', 'longBreak'
      completedPomodoros: 0,
      totalSessions: 0,
      
      // 设置
      settings: {
        workDuration: 25,
        shortBreakDuration: 5,
        longBreakDuration: 15,
        longBreakInterval: 4,
        soundEnabled: true,
        autoStartBreaks: false
      },
      
      // 统计数据
      todayStats: {
        completedPomodoros: 0,
        totalFocusTime: 0,
        totalBreakTime: 0
      },
      
      // 计时器
      timer: null,
      
      // 进度环
      circumference: 2 * Math.PI * 90
    }
  },
  computed: {
    formattedTime() {
      const minutes = Math.floor(this.timeRemaining / 60)
      const seconds = this.timeRemaining % 60
      return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
    },
    
    currentSessionName() {
      switch (this.currentSession) {
        case 'work':
          return '专注时间'
        case 'shortBreak':
          return '短休息'
        case 'longBreak':
          return '长休息'
        default:
          return '专注时间'
      }
    },
    
    strokeDashoffset() {
      const totalTime = this.getCurrentSessionDuration() * 60
      const progress = (totalTime - this.timeRemaining) / totalTime
      return this.circumference - (progress * this.circumference)
    }
  },
  mounted() {
    this.loadSettings()
    this.loadTodayStats()
    this.resetTimer()
  },
  beforeUnmount() {
    if (this.timer) {
      clearInterval(this.timer)
    }
    this.saveSettings()
    this.saveTodayStats()
  },
  methods: {
    toggleTimer() {
      if (this.isRunning) {
        this.pauseTimer()
      } else {
        this.startTimer()
      }
    },
    
    startTimer() {
      if (this.timeRemaining === 0) return
      
      this.isRunning = true
      this.timer = setInterval(() => {
        this.timeRemaining--
        
        if (this.timeRemaining === 0) {
          this.completeSession()
        }
      }, 1000)
    },
    
    pauseTimer() {
      this.isRunning = false
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
      }
    },
    
    resetTimer() {
      this.pauseTimer()
      this.timeRemaining = this.getCurrentSessionDuration() * 60
    },
    
    skipSession() {
      this.pauseTimer()
      this.completeSession()
    },
    
    completeSession() {
      this.pauseTimer()
      
      // 播放提示音
      if (this.settings.soundEnabled) {
        this.playNotificationSound()
      }
      
      // 更新统计
      this.updateStats()
      
      // 切换到下一个会话
      this.switchToNextSession()
      
      // 显示通知
      this.showSessionCompleteNotification()
      
      // 自动开始下一个会话（如果启用）
      if (this.settings.autoStartBreaks || this.currentSession === 'work') {
        setTimeout(() => {
          if (this.settings.autoStartBreaks) {
            this.startTimer()
          }
        }, 1000)
      }
    },
    
    switchToNextSession() {
      if (this.currentSession === 'work') {
        this.completedPomodoros++
        this.totalSessions++
        
        // 判断是长休息还是短休息
        if (this.completedPomodoros % this.settings.longBreakInterval === 0) {
          this.currentSession = 'longBreak'
        } else {
          this.currentSession = 'shortBreak'
        }
      } else {
        this.currentSession = 'work'
      }
      
      this.timeRemaining = this.getCurrentSessionDuration() * 60
    },
    
    getCurrentSessionDuration() {
      switch (this.currentSession) {
        case 'work':
          return this.settings.workDuration
        case 'shortBreak':
          return this.settings.shortBreakDuration
        case 'longBreak':
          return this.settings.longBreakDuration
        default:
          return this.settings.workDuration
      }
    },
    
    adjustTime(type, delta) {
      if (this.isRunning) return
      
      const minValues = {
        work: 1,
        shortBreak: 1,
        longBreak: 1,
        longBreakInterval: 2
      }
      
      const maxValues = {
        work: 60,
        shortBreak: 30,
        longBreak: 60,
        longBreakInterval: 10
      }
      
      const settingMap = {
        work: 'workDuration',
        shortBreak: 'shortBreakDuration',
        longBreak: 'longBreakDuration',
        longBreakInterval: 'longBreakInterval'
      }
      
      const setting = settingMap[type]
      const newValue = this.settings[setting] + delta
      
      if (newValue >= minValues[type] && newValue <= maxValues[type]) {
        this.settings[setting] = newValue
        
        // 如果调整的是当前会话的时间，重置计时器
        if ((type === 'work' && this.currentSession === 'work') ||
            (type === 'shortBreak' && this.currentSession === 'shortBreak') ||
            (type === 'longBreak' && this.currentSession === 'longBreak')) {
          this.resetTimer()
        }
      }
    },
    
    updateStats() {
      if (this.currentSession === 'work') {
        this.todayStats.completedPomodoros++
        this.todayStats.totalFocusTime += this.settings.workDuration
      } else {
        this.todayStats.totalBreakTime++
      }
    },
    
    playNotificationSound() {
      // 创建简单的提示音
      const audioContext = new (window.AudioContext || window.webkitAudioContext)()
      const oscillator = audioContext.createOscillator()
      const gainNode = audioContext.createGain()
      
      oscillator.connect(gainNode)
      gainNode.connect(audioContext.destination)
      
      oscillator.frequency.setValueAtTime(800, audioContext.currentTime)
      oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1)
      oscillator.frequency.setValueAtTime(800, audioContext.currentTime + 0.2)
      
      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime)
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3)
      
      oscillator.start(audioContext.currentTime)
      oscillator.stop(audioContext.currentTime + 0.3)
    },
    
    showSessionCompleteNotification() {
      const sessionName = this.currentSessionName
      const nextSession = this.currentSession === 'work' ? 
        (this.completedPomodoros % this.settings.longBreakInterval === 0 ? '长休息' : '短休息') : 
        '专注时间'
      
      // 简单的通知，可以后续集成更好的通知组件
      alert(`🎉 ${sessionName}完成！\n\n接下来是${nextSession}时间。`)
    },
    
    formatDuration(minutes) {
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60
      if (hours > 0) {
        return `${hours}h ${mins}m`
      }
      return `${mins}m`
    },
    
    loadSettings() {
      const saved = localStorage.getItem('pomodoro-settings')
      if (saved) {
        this.settings = { ...this.settings, ...JSON.parse(saved) }
      }
    },
    
    saveSettings() {
      localStorage.setItem('pomodoro-settings', JSON.stringify(this.settings))
    },
    
    loadTodayStats() {
      const today = new Date().toDateString()
      const saved = localStorage.getItem(`pomodoro-stats-${today}`)
      if (saved) {
        this.todayStats = { ...this.todayStats, ...JSON.parse(saved) }
      }
    },
    
    saveTodayStats() {
      const today = new Date().toDateString()
      localStorage.setItem(`pomodoro-stats-${today}`, JSON.stringify(this.todayStats))
    }
  }
}
</script>

<style scoped>
.pomodoro-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 255, 0.95));
  border-radius: 20px;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(102, 126, 234, 0.15);
}

.pomodoro-header {
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 20px rgba(255, 107, 107, 0.3);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.pomodoro-icon {
  font-size: 2rem;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.header-text h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
}

.header-text p {
  margin: 2px 0 0 0;
  font-size: 0.85rem;
  opacity: 0.9;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 35px;
  height: 35px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.timer-display {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 30px;
}

.timer-circle {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-ring {
  transform: rotate(-90deg);
}

.progress-ring-background {
  fill: none;
  stroke: rgba(255, 107, 107, 0.1);
  stroke-width: 8;
}

.progress-ring-progress {
  fill: none;
  stroke: #ff6b6b;
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.3s ease;
}

.timer-content {
  position: absolute;
  text-align: center;
}

.time-display {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2d3436;
  margin-bottom: 5px;
  font-family: 'Courier New', monospace;
}

.session-type {
  font-size: 1rem;
  color: #636e72;
  font-weight: 600;
}

.timer-controls {
  display: flex;
  justify-content: center;
  gap: 15px;
  padding: 0 30px 30px;
}

.control-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 25px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-btn.primary {
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

.control-btn.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

.control-btn.secondary {
  background: rgba(255, 107, 107, 0.1);
  color: #ff6b6b;
  border: 2px solid rgba(255, 107, 107, 0.2);
}

.control-btn.secondary:hover {
  background: rgba(255, 107, 107, 0.2);
  transform: translateY(-1px);
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.session-info {
  padding: 0 30px 20px;
}

.session-counter {
  display: flex;
  justify-content: center;
  gap: 40px;
}

.counter-item {
  text-align: center;
}

.counter-number {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: #ff6b6b;
  margin-bottom: 5px;
}

.counter-label {
  font-size: 0.85rem;
  color: #636e72;
  font-weight: 600;
}

.settings-section, .stats-section {
  padding: 20px 30px;
  border-top: 1px solid rgba(255, 107, 107, 0.1);
}

.settings-section h4, .stats-section h4 {
  margin: 0 0 15px 0;
  color: #2d3436;
  font-size: 1rem;
  font-weight: 700;
}

.settings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-item label {
  font-size: 0.85rem;
  color: #636e72;
  font-weight: 600;
}

.time-input {
  display: flex;
  align-items: center;
  gap: 10px;
  background: white;
  border: 2px solid rgba(255, 107, 107, 0.2);
  border-radius: 15px;
  padding: 8px 12px;
}

.time-input button {
  background: #ff6b6b;
  color: white;
  border: none;
  width: 25px;
  height: 25px;
  border-radius: 50%;
  cursor: pointer;
  font-weight: 700;
  transition: all 0.3s ease;
}

.time-input button:hover:not(:disabled) {
  background: #ee5a24;
  transform: scale(1.1);
}

.time-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.time-input span {
  flex: 1;
  text-align: center;
  font-weight: 600;
  color: #2d3436;
}

.sound-settings {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 0.9rem;
  color: #2d3436;
  font-weight: 600;
}

.checkbox-label input[type="checkbox"] {
  display: none;
}

.checkmark {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 107, 107, 0.3);
  border-radius: 4px;
  position: relative;
  transition: all 0.3s ease;
}

.checkbox-label input[type="checkbox"]:checked + .checkmark {
  background: #ff6b6b;
  border-color: #ff6b6b;
}

.checkbox-label input[type="checkbox"]:checked + .checkmark::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: 700;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.stat-item {
  text-align: center;
  background: white;
  padding: 15px;
  border-radius: 15px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #ff6b6b;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.8rem;
  color: #636e72;
  font-weight: 600;
}

.pomodoro-container::-webkit-scrollbar {
  width: 6px;
}

.pomodoro-container::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.pomodoro-container::-webkit-scrollbar-thumb {
  background: rgba(255, 107, 107, 0.3);
  border-radius: 3px;
  transition: background 0.3s ease;
}

.pomodoro-container::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 107, 107, 0.5);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .pomodoro-header {
    padding: 15px;
  }
  
  .timer-display {
    padding: 20px;
  }
  
  .progress-ring {
    width: 160px;
    height: 160px;
  }
  
  .progress-ring-background,
  .progress-ring-progress {
    r: 70;
  }
  
  .time-display {
    font-size: 2rem;
  }
  
  .timer-controls {
    padding: 0 20px 20px;
    gap: 10px;
  }
  
  .control-btn {
    padding: 10px 16px;
    font-size: 0.8rem;
  }
  
  .session-counter {
    gap: 30px;
  }
  
  .counter-number {
    font-size: 1.5rem;
  }
  
  .settings-section, .stats-section {
    padding: 15px 20px;
  }
  
  .settings-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }
}
</style>