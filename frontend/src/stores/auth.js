import { defineStore } from 'pinia'

const TOKEN_KEY = 'asagent_token'
const ADMIN_KEY = 'asagent_is_admin'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    isAdmin: localStorage.getItem(ADMIN_KEY) === 'true'
  }),
  actions: {
    restore() {
      if (!this.token) {
        this.token = localStorage.getItem(TOKEN_KEY) || ''
        this.isAdmin = localStorage.getItem(ADMIN_KEY) === 'true'
      }
    },
    setAuth(token, isAdmin) {
      this.token = token
      this.isAdmin = !!isAdmin
      if (token) {
        localStorage.setItem(TOKEN_KEY, token)
      } else {
        localStorage.removeItem(TOKEN_KEY)
      }
      localStorage.setItem(ADMIN_KEY, String(this.isAdmin))
    },
    logout() {
      this.token = ''
      this.isAdmin = false
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(ADMIN_KEY)
    }
  }
})
