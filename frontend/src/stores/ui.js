import { defineStore } from 'pinia'

const THEME_KEY = 'asagent_theme'

function systemTheme() {
  if (typeof window === 'undefined' || !window.matchMedia) return 'dark'
  return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'
}

export const useUiStore = defineStore('ui', {
  state: () => ({
    theme: localStorage.getItem(THEME_KEY) || 'dark',
    railCollapsed: false, // icon rail collapsed (icon-only)
    canvasOpen: true // artifact canvas visibility on the chat workspace
  }),
  actions: {
    applyTheme() {
      const html = document.documentElement
      html.setAttribute('data-theme', this.theme)
    },
    setTheme(t) {
      this.theme = t === 'light' ? 'light' : 'dark'
      try {
        localStorage.setItem(THEME_KEY, this.theme)
      } catch (e) {
        /* ignore storage errors */
      }
      this.applyTheme()
    },
    toggleTheme() {
      this.setTheme(this.theme === 'dark' ? 'light' : 'dark')
    },
    toggleRail() {
      this.railCollapsed = !this.railCollapsed
    },
    toggleCanvas() {
      this.canvasOpen = !this.canvasOpen
    }
  }
})
