<template>
  <div class="ai-chat-container">
    <div class="ai-chat-header">
      <div class="header-content">
        <div class="ai-avatar">🤖</div>
        <div class="header-text">
          <h3>AI 智能助手</h3>
          <p>史迪仔的贴心小助手</p>
        </div>
      </div>
      <button class="close-btn" @click="$emit('close')">
        <i class="fas fa-times"></i>
      </button>
    </div>
    
    <div class="chat-messages" ref="messagesContainer">
      <div v-for="message in messages" :key="message.id" 
           :class="['message', message.type]">
        <div class="message-avatar">
          <span v-if="message.type === 'ai'">🤖</span>
          <span v-else>🐶</span>
        </div>
        <div class="message-content">
          <div class="message-text" v-html="formatMessage(message.content)"></div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>
      
      <div v-if="isTyping" class="message ai typing">
        <div class="message-avatar">🤖</div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="chat-input-container">
      <div class="quick-actions">
        <button class="quick-btn" @click="sendQuickMessage('帮我总结一下今天的笔记')">
          📝 总结笔记
        </button>
        <button class="quick-btn" @click="sendQuickMessage('给我一些学习建议')">
          💡 学习建议
        </button>
        <button class="quick-btn" @click="sendQuickMessage('帮我制定今日计划')">
          📅 制定计划
        </button>
      </div>
      
      <div class="input-area">
        <textarea 
          v-model="inputMessage" 
          @keydown.enter.prevent="handleEnter"
          @input="adjustTextareaHeight"
          placeholder="和史迪仔的AI助手聊聊吧..."
          class="message-input"
          ref="messageInput"
          :disabled="isTyping"
        ></textarea>
        <button 
          class="send-btn" 
          @click="sendMessage" 
          :disabled="!inputMessage.trim() || isTyping"
        >
          <i class="fas fa-paper-plane"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

export default {
  name: 'AIChat',
  data() {
    return {
      messages: [
        {
          id: 1,
          type: 'ai',
          content: '你好！我是史迪仔的AI助手 🤖✨<br>我可以帮你：<br>• 总结和分析笔记内容<br>• 提供学习建议和计划<br>• 回答各种问题<br>• 协助整理思路<br><br>有什么可以帮助你的吗？',
          timestamp: new Date()
        }
      ],
      inputMessage: '',
      isTyping: false,
      messageIdCounter: 2
    }
  },
  mounted() {
    this.scrollToBottom()
    this.$refs.messageInput.focus()
  },
  methods: {
    async sendMessage() {
      if (!this.inputMessage.trim() || this.isTyping) return
      
      const userMessage = {
        id: this.messageIdCounter++,
        type: 'user',
        content: this.inputMessage.trim(),
        timestamp: new Date()
      }
      
      this.messages.push(userMessage)
      const messageToSend = this.inputMessage.trim()
      this.inputMessage = ''
      this.adjustTextareaHeight()
      
      this.scrollToBottom()
      this.isTyping = true
      
      try {
        const response = await axios.post(`${API_BASE_URL}/ai/chat`, {
          message: messageToSend,
          context: this.getRecentContext()
        })
        
        const aiMessage = {
          id: this.messageIdCounter++,
          type: 'ai',
          content: response.data.response || '抱歉，我现在无法回答这个问题。',
          timestamp: new Date()
        }
        
        this.messages.push(aiMessage)
      } catch (error) {
        console.error('AI聊天请求失败:', error)
        const errorMessage = {
          id: this.messageIdCounter++,
          type: 'ai',
          content: '抱歉，我现在遇到了一些技术问题。请稍后再试，或者尝试重新表述你的问题。',
          timestamp: new Date()
        }
        this.messages.push(errorMessage)
      } finally {
        this.isTyping = false
        this.scrollToBottom()
        this.$nextTick(() => {
          this.$refs.messageInput.focus()
        })
      }
    },
    
    sendQuickMessage(message) {
      this.inputMessage = message
      this.sendMessage()
    },
    
    handleEnter(event) {
      if (event.shiftKey) {
        // Shift+Enter 换行
        return
      }
      this.sendMessage()
    },
    
    adjustTextareaHeight() {
      const textarea = this.$refs.messageInput
      if (textarea) {
        textarea.style.height = 'auto'
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
      }
    },
    
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    },
    
    formatMessage(content) {
      return content.replace(/\n/g, '<br>')
    },
    
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    getRecentContext() {
      // 获取最近的对话上下文，用于AI理解对话历史
      return this.messages.slice(-6).map(msg => ({
        type: msg.type,
        content: msg.content.replace(/<br>/g, '\n')
      }))
    }
  }
}
</script>

<style scoped>
.ai-chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 255, 0.95));
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(102, 126, 234, 0.15);
}

.ai-chat-header {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.ai-avatar {
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

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message {
  display: flex;
  gap: 12px;
  animation: fadeInUp 0.3s ease;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.message.ai .message-avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.message.user .message-avatar {
  background: linear-gradient(135deg, #ffeaa7, #fab1a0);
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.message.ai .message-content {
  align-items: flex-start;
}

.message.user .message-content {
  align-items: flex-end;
}

.message-text {
  background: white;
  padding: 12px 16px;
  border-radius: 18px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  word-wrap: break-word;
  text-align: left;
}

.message.user .message-text {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.message-time {
  font-size: 0.75rem;
  color: #999;
  padding: 0 8px;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: white;
  border-radius: 18px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #667eea;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

.chat-input-container {
  padding: 20px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(102, 126, 234, 0.1);
}

.quick-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.quick-btn {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  border: 1px solid rgba(102, 126, 234, 0.2);
  color: #667eea;
  padding: 8px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.quick-btn:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
  transform: translateY(-1px);
}

.input-area {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 20px;
  padding: 12px 16px;
  font-size: 0.9rem;
  resize: none;
  min-height: 44px;
  max-height: 120px;
  background: white;
  transition: all 0.3s ease;
  font-family: inherit;
}

.message-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.message-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.send-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  color: white;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.1);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 3px;
  transition: background 0.3s ease;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .ai-chat-header {
    padding: 15px;
  }
  
  .header-text h3 {
    font-size: 1.1rem;
  }
  
  .header-text p {
    font-size: 0.8rem;
  }
  
  .chat-messages {
    padding: 15px;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .chat-input-container {
    padding: 15px;
  }
  
  .quick-actions {
    gap: 6px;
  }
  
  .quick-btn {
    font-size: 0.75rem;
    padding: 6px 10px;
  }
}
</style>