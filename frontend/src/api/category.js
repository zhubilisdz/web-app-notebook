import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 分类管理API
export const categoryApi = {
  // 获取所有分类
  getCategories() {
    return api.get('/categories')
  },

  // 创建分类
  createCategory(categoryData) {
    return api.post('/categories', categoryData)
  },

  // 更新分类
  updateCategory(categoryId, categoryData) {
    return api.put(`/categories/${categoryId}`, categoryData)
  },

  // 删除分类
  deleteCategory(categoryId) {
    return api.delete(`/categories/${categoryId}`)
  },

  // 获取分类下的笔记
  getCategoryNotes(categoryId) {
    return api.get(`/categories/${categoryId}/notes`)
  },

  // 将笔记添加到分类
  addNoteToCategory(noteId, categoryIds) {
    return api.post(`/notes/${noteId}/categories`, { category_ids: categoryIds })
  }
}

export default categoryApi