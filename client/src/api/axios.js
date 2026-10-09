import axios from 'axios'
import Cookies from 'js-cookie'

// axios.defaults.baseURL = 'http://127.0.0.1:8000'
// axios.defaults.withCredentials = true

axios.interceptors.request.use((config) => {
  const method = config.method?.toLowerCase()

  const unsafeMethods = ['post', 'put', 'patch', 'delete']

  if (unsafeMethods.includes(method)) {
    const csrfToken = Cookies.get('csrftoken')
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
  }

  return config
})

export default axios