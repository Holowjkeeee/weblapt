<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const loading = ref(false)

async function onLogin() {
  loading.value = true
  errorMessage.value = ''

  try {
    await userStore.login(username.value, password.value)
    router.push('/')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || error.message || 'Ошибка входа'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-5">
        <div class="card shadow-sm">
          <div class="card-body">
            <h3 class="card-title mb-4 text-center">Вход в систему</h3>

            <div v-if="errorMessage" class="alert alert-danger">
              {{ errorMessage }}
            </div>

            <form @submit.prevent="onLogin">
              <div class="mb-3">
                <label class="form-label">Логин</label>
                <input
                  v-model="username"
                  type="text"
                  class="form-control"
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Пароль</label>
                <input
                  v-model="password"
                  type="password"
                  class="form-control"
                />
              </div>

              <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                {{ loading ? 'Вход...' : 'Войти' }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>