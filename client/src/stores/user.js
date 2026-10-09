import { defineStore } from 'pinia'
import axios from '@/api/axios'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    isAuthChecked: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
  },

  actions: {
    async fetchCsrf() {
      await axios.get('/api/auth/csrf/')
    },

    async login(username, password) {
      await this.fetchCsrf()
      const { data } = await axios.post('/api/auth/login/', {
        username,
        password,
      })
      this.user = data
      this.isAuthChecked = true
      return data
    },

    async fetchMe() {
      try {
        const { data } = await axios.get('/api/auth/me/')
        this.user = data
      } catch (error) {
        this.user = null
      } finally {
        this.isAuthChecked = true
      }
    },

    async logout() {
      await this.fetchCsrf()
      await axios.post('/api/auth/logout/')
      this.user = null
      this.isAuthChecked = true
    },
  },
})