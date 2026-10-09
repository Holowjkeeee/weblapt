<script setup>
import { ref, onBeforeMount, computed } from 'vue'
import axios from '@/api/axios'

const items = ref([])
const processorBrands = ref([])   // для выпадающего списка
const itemToAdd = ref({ brand: null, name: '' })
const itemToEdit = ref({ id: null, brand: null, name: '' })
const loading = ref(false)
const errorMessage = ref('')
const stats = ref(null)

const pictureRef = ref()
const addImageUrl = ref(null)
const editPictureRef = ref()
const editImageUrl = ref(null)
const selectedImage = ref(null)

function openImage(url) { selectedImage.value = url }
function closeImage() { selectedImage.value = null }

async function fetchItems() {
  try {
    const r = await axios.get('/api/processor-families/')
    items.value = r.data
    errorMessage.value = ''
  } catch {
    errorMessage.value = 'Ошибка загрузки линеек'
  }
}

async function fetchProcessorBrands() {
  try {
    const r = await axios.get('/api/processor-brands/')
    processorBrands.value = r.data
  } catch {
    errorMessage.value = 'Ошибка загрузки производителей'
  }
}

async function fetchStats() {
  try {
    const r = await axios.get('/api/processor-families/stats/')
    stats.value = r.data
  } catch {
    stats.value = null
  }
}

async function onAdd() {
  try {
    const formData = new FormData()
    if (pictureRef.value?.files?.[0]) {
      formData.append('picture', pictureRef.value.files[0])
    }
    formData.set('brand', itemToAdd.value.brand || '')
    formData.set('name', itemToAdd.value.name || '')
    await axios.post('/api/processor-families/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    itemToAdd.value = { brand: null, name: '' }
    addImageUrl.value = null
    if (pictureRef.value) pictureRef.value.value = null
    await fetchItems()
    await fetchStats()
  } catch {
    errorMessage.value = 'Не удалось добавить линейку'
  }
}

async function onEditClick(item) {
  itemToEdit.value = { ...item }
  editImageUrl.value = item.picture || null
  if (editPictureRef.value) editPictureRef.value.value = null
}

async function onUpdate() {
  try {
    const formData = new FormData()
    if (editPictureRef.value?.files?.[0]) {
      formData.append('picture', editPictureRef.value.files[0])
    }
    formData.set('brand', itemToEdit.value.brand || '')
    formData.set('name', itemToEdit.value.name || '')
    await axios.patch(`/api/processor-families/${itemToEdit.value.id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    itemToEdit.value = { id: null, brand: null, name: '' }
    editImageUrl.value = null
    if (editPictureRef.value) editPictureRef.value.value = null
    await fetchItems()
    await fetchStats()
  } catch {
    errorMessage.value = 'Не удалось обновить линейку'
  }
}

async function onRemove(item) {
  try {
    await axios.delete(`/api/processor-families/${item.id}/`)
    await fetchItems()
    await fetchStats()
  } catch {
    errorMessage.value = 'Не удалось удалить линейку'
  }
}

function addPictureChange() {
  if (pictureRef.value?.files?.[0]) {
    addImageUrl.value = URL.createObjectURL(pictureRef.value.files[0])
  }
}
function editPictureChange() {
  if (editPictureRef.value?.files?.[0]) {
    editImageUrl.value = URL.createObjectURL(editPictureRef.value.files[0])
  }
}


function getBrandName(brandId) {
  const found = processorBrands.value.find(b => b.id === brandId)
  return found ? found.name : '-'
}

onBeforeMount(async () => {
  loading.value = true
  await fetchProcessorBrands()
  await fetchItems()
  await fetchStats()
  loading.value = false
})
</script>

<template>
  <!-- Модалка добавления -->
  <div class="modal fade" id="addModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Добавить линейку процессора</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="onAdd">
            <div class="form-floating mb-3">
              <select class="form-select" v-model="itemToAdd.brand" required>
                <option :value="null">Выберите производителя</option>
                <option :value="b.id" v-for="b in processorBrands" :key="b.id">{{ b.name }}</option>
              </select>
              <label>Производитель</label>
            </div>
            <div class="form-floating mb-3">
              <input type="text" class="form-control" v-model="itemToAdd.name" placeholder="Название линейки" required>
              <label>Название линейки (например, Core i7)</label>
            </div>
            <div class="mb-3">
              <input class="form-control" type="file" ref="pictureRef" @change="addPictureChange">
            </div>
            <div v-if="addImageUrl" class="mb-3">
              <img :src="addImageUrl" style="max-height:60px; cursor:pointer" @click="openImage(addImageUrl)">
            </div>
            <button type="submit" class="btn btn-primary" data-bs-dismiss="modal">Добавить</button>
          </form>
        </div>
      </div>
    </div>
  </div>

  <!-- Модалка редактирования -->
  <div class="modal fade" id="editModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать линейку</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="onUpdate">
            <div class="form-floating mb-3">
              <select class="form-select" v-model="itemToEdit.brand" required>
                <option :value="null">Выберите производителя</option>
                <option :value="b.id" v-for="b in processorBrands" :key="b.id">{{ b.name }}</option>
              </select>
              <label>Производитель</label>
            </div>
            <div class="form-floating mb-3">
              <input type="text" class="form-control" v-model="itemToEdit.name" placeholder="Название линейки" required>
              <label>Название линейки</label>
            </div>
            <div class="mb-3">
              <input class="form-control" type="file" ref="editPictureRef" @change="editPictureChange">
            </div>
            <div v-if="editImageUrl" class="mb-3">
              <img :src="editImageUrl" style="max-height:60px; cursor:pointer" @click="openImage(editImageUrl)">
            </div>
            <button type="submit" class="btn btn-primary" data-bs-dismiss="modal">Сохранить</button>
          </form>
        </div>
      </div>
    </div>
  </div>

  <!-- Основная страница -->
  <div class="container-fluid">
    <div class="row mb-3">
      <div class="col">
        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addModal">Добавить</button>
      </div>
    </div>

    <div v-if="loading">Загрузка...</div>
    <div v-if="errorMessage" class="alert alert-warning">{{ errorMessage }}</div>

    <div v-if="stats" class="alert alert-info">
      <b>Статистика:</b> Количество линеек: {{ stats.count }}
    </div>

    <div v-for="item in items" :key="item.id" class="item">
      <div>
        <b>{{ item.name }}</b>
        <span class="text-muted"> ({{ getBrandName(item.brand) }})</span>
      </div>
      <div v-if="item.picture">
        <img :src="item.picture" style="max-height:60px; cursor:pointer" @click="openImage(item.picture)">
      </div>
      <button class="btn btn-success btn-sm" @click="onEditClick(item)" data-bs-toggle="modal" data-bs-target="#editModal">✎</button>
      <button class="btn btn-danger btn-sm" @click="onRemove(item)">✖</button>
    </div>
  </div>

  <!-- Модальное окно просмотра картинки -->
  <div v-if="selectedImage" class="image-modal" @click="closeImage">
    <img :src="selectedImage" class="image-modal-content">
  </div>
</template>

<style scoped>
.item {
  display: grid;
  grid-template-columns: 2fr auto auto auto;
  align-items: center;
  gap: 16px;
  padding: 0.5rem;
  margin: 0.5rem 0;
  border: 1px solid silver;
  border-radius: 8px;
}
.image-modal {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}
.image-modal-content {
  max-width: 90%;
  max-height: 90%;
}
</style>