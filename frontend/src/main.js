import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// 防止字体加载闪烁
function initApp() {
  const app = createApp(App)
  
  // 检测字体加载状态
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(() => {
      document.body.classList.add('font-loaded')
      app.mount('#app')
    })
  } else {
    // 降级处理：延迟一小段时间后挂载
    setTimeout(() => {
      document.body.classList.add('font-loaded')
      app.mount('#app')
    }, 100)
  }
}

// DOM准备就绪后初始化应用
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp)
} else {
  initApp()
}
