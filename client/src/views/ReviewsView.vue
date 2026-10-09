<script setup>
import { ref, computed, onBeforeMount } from 'vue'
import axios from '@/api/axios'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isAuthenticated = computed(() => userStore.isAuthenticated)

const reviews = ref([])
const laptops = ref([])
const loading = ref(false)
const errorMessage = ref('')
const stats = ref(null)

const filters = ref({
  author: '',
  laptop: '',
  text: '',
})

const reviewToAdd = ref({
  author_name: '',
  text: '',
  laptop: null,
})

const reviewToEdit = ref({
  id: null,
  author_name: '',
  text: '',
  laptop: null,
})

const filteredReviews = computed(() => {
  let result = reviews.value
  if (filters.value.author) {
    result = result.filter(r => 
      r.author_name.toLowerCase().includes(filters.value.author.toLowerCase())
    )
  }
  if (filters.value.laptop) {
    result = result.filter(r => 
      r.laptop_name && r.laptop_name.toLowerCase().includes(filters.value.laptop.toLowerCase())
    )
  }
  if (filters.value.text) {
    result = result.filter(r => 
      r.text.toLowerCase().includes(filters.value.text.toLowerCase())
    )
  }
  return result
})

async function fetchReviews() {
  try {
    const r = await axios.get('/api/reviews/')
    reviews.value = r.data
    errorMessage.value = ''
  } catch (error) {
    reviews.value = []
    errorMessage.value = 'Ошибка загрузки отзывов'
  }
}

async function fetchLaptops() {
  try {
    const r = await axios.get('/api/laptops/')
    laptops.value = r.data
  } catch {
    errorMessage.value = 'Ошибка загрузки списка ноутбуков'
  }
}

async function fetchStats() {
  try {
    const r = await axios.get('/api/reviews/stats/')
    stats.value = r.data
  } catch {
    stats.value = null
  }
}

async function onAddReview() {
  try {
    await axios.post('/api/reviews/', {
      author_name: reviewToAdd.value.author_name,
      text: reviewToAdd.value.text,
      laptop: reviewToAdd.value.laptop,
    })
    reviewToAdd.value = { author_name: '', text: '', laptop: null }
    await fetchReviews()
    await fetchStats()
  } catch (error) {
    errorMessage.value = 'Не удалось добавить отзыв'
  }
}


async function onEditClick(review) {
  reviewToEdit.value = {
    id: review.id,
    author_name: review.author_name,
    text: review.text,
    laptop: review.laptop,
  }
}

async function onUpdateReview() {
  try {
    await axios.patch(`/api/reviews/${reviewToEdit.value.id}/`, {
      author_name: reviewToEdit.value.author_name,
      text: reviewToEdit.value.text,
      laptop: reviewToEdit.value.laptop,
    })
    reviewToEdit.value = { id: null, author_name: '', text: '', laptop: null }
    await fetchReviews()
    await fetchStats()
  } catch (error) {
    errorMessage.value = 'Не удалось обновить отзыв'
  }
}

async function onRemoveClick(review) {
  try {
    await axios.delete(`/api/reviews/${review.id}/`)
    await fetchReviews()
    await fetchStats()
  } catch (error) {
    errorMessage.value = 'Не удалось удалить отзыв'
  }
}

function resetFilters() {
  filters.value = { author: '', laptop: '', text: '' }
}

onBeforeMount(async () => {
  loading.value = true
  await fetchReviews()
  await fetchLaptops()
  await fetchStats()
  loading.value = false
})
</script>

<template>
  <!-- Модалка добавления -->
  <div class="modal fade" id="addReviewModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Добавить отзыв</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="onAddReview">
            <div class="form-floating mb-3">
              <input type="text" class="form-control" v-model="reviewToAdd.author_name" placeholder="Автор" required>
              <label>Автор</label>
            </div>
            <div class="form-floating mb-3">
              <select class="form-select" v-model="reviewToAdd.laptop" required>
                <option :value="null">Выберите ноутбук</option>
                <option :value="l.id" v-for="l in laptops" :key="l.id">{{ l.name }}</option>
              </select>
              <label>Ноутбук</label>
            </div>
            <div class="form-floating mb-3">
              <textarea class="form-control" v-model="reviewToAdd.text" placeholder="Текст отзыва" style="height: 100px" required></textarea>
              <label>Текст отзыва</label>
            </div>
            <button type="submit" class="btn btn-primary" data-bs-dismiss="modal">Добавить</button>
          </form>
        </div>
      </div>
    </div>
  </div>

  <!-- Модалка редактирования -->
  <div class="modal fade" id="editReviewModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать отзыв</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="onUpdateReview">
            <div class="form-floating mb-3">
              <input type="text" class="form-control" v-model="reviewToEdit.author_name" placeholder="Автор" required>
              <label>Автор</label>
            </div>
            <div class="form-floating mb-3">
              <select class="form-select" v-model="reviewToEdit.laptop" required>
                <option :value="null">Выберите ноутбук</option>
                <option :value="l.id" v-for="l in laptops" :key="l.id">{{ l.name }}</option>
              </select>
              <label>Ноутбук</label>
            </div>
            <div class="form-floating mb-3">
              <textarea class="form-control" v-model="reviewToEdit.text" placeholder="Текст отзыва" style="height: 100px" required></textarea>
              <label>Текст отзыва</label>
            </div>
            <button type="submit" class="btn btn-primary" data-bs-dismiss="modal">Сохранить</button>
          </form>
        </div>
      </div>
    </div>
  </div>

  <!-- Основная страница -->
  <div class="container-fluid">
    <!-- Фильтры -->
    <div class="card mb-4 p-3">
      <h5>Фильтры</h5>
      <div class="row g-2">
        <div class="col-md-3">
          <input type="text" class="form-control" v-model="filters.author" placeholder="Фильтр по автору">
        </div>
        <div class="col-md-3">
          <input type="text" class="form-control" v-model="filters.laptop" placeholder="Фильтр по ноутбуку">
        </div>
        <div class="col-md-4">
          <input type="text" class="form-control" v-model="filters.text" placeholder="Фильтр по тексту">
        </div>
        <div class="col-md-auto">
          <button class="btn btn-secondary" @click="resetFilters">Сбросить</button>
        </div>
      </div>
    </div>

    <!-- Статистика -->
    <div v-if="stats" class="alert alert-info">
      <b>Статистика:</b> Всего отзывов: {{ stats.count }}
    </div>

    <!-- Кнопка добавления -->
    <div class="mb-3" v-if="isAuthenticated">
      <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addReviewModal">Добавить отзыв</button>
    </div>

    <div v-if="loading">Загрузка...</div>
    <div v-if="errorMessage" class="alert alert-warning">{{ errorMessage }}</div>

    <!-- Список отзывов -->
    <div v-for="review in filteredReviews" :key="review.id" class="review-item">
      <div>
        <b>{{ review.author_name }}</b>
        <span class="text-muted ms-2">на «{{ review.laptop_name || review.laptop }}»</span>
        <p>{{ review.text }}</p>
      </div>
      <div v-if="isAuthenticated" class="review-actions">
        <button class="btn btn-success btn-sm me-1" @click="onEditClick(review)" data-bs-toggle="modal" data-bs-target="#editReviewModal">✎</button>
        <button class="btn btn-danger btn-sm" @click="onRemoveClick(review)">✖</button>
      </div>
    </div>
    <div v-if="!loading && filteredReviews.length === 0" class="text-muted">
      Нет отзывов, соответствующих фильтрам.
    </div>
  </div>
</template>

<style scoped>
.review-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  margin: 0.5rem 0;
  border: 1px solid #dee2e6;
  border-radius: 8px;
}
.review-actions {
  display: flex;
  gap: 4px;
}
</style>