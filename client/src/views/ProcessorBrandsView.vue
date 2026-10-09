<script setup>
import { ref, onBeforeMount } from 'vue'
import axios from '@/api/axios'

const items = ref([])
const families = ref([])               
const expandedBrandId = ref(null)    
const itemToAdd = ref({ name: '' })
const itemToEdit = ref({ id: null, name: '' })
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
    const r = await axios.get('/api/processor-brands/')
    items.value = r.data
    errorMessage.value = ''
  } catch {
    errorMessage.value = 'Ошибка загрузки производителей'
  }
}

async function fetchFamilies() {
  try {
    const r = await axios.get('/api/processor-families/')
    families.value = r.data
  } catch {
  }
}

async function fetchStats() {
  try {
    const r = await axios.get('/api/processor-brands/stats/')
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
    formData.set('name', itemToAdd.value.name || '')
    await axios.post('/api/processor-brands/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    itemToAdd.value = { name: '' }
    addImageUrl.value = null
    if (pictureRef.value) pictureRef.value.value = null
    await fetchItems()
    await fetchStats()
  } catch {
    errorMessage.value = 'Не удалось добавить производителя'
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
    formData.set('name', itemToEdit.value.name || '')
    await axios.patch(`/api/processor-brands/${itemToEdit.value.id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    itemToEdit.value = { id: null, name: '' }
    editImageUrl.value = null
    if (editPictureRef.value) editPictureRef.value.value = null
    await fetchItems()
    await fetchStats()
  } catch {
    errorMessage.value = 'Не удалось обновить производителя'
  }
}

async function onRemove(item) {
  try {
    await axios.delete(`/api/processor-brands/${item.id}/`)
    await fetchItems()
    await fetchStats()
  } catch {
    errorMessage.value = 'Не удалось удалить производителя'
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

function toggleBrand(brandId) {
  expandedBrandId.value = expandedBrandId.value === brandId ? null : brandId
}

function getFamiliesForBrand(brandId) {
  return families.value.filter(f => f.brand === brandId)
}

onBeforeMount(async () => {
  loading.value = true
  await fetchItems()
  await fetchFamilies()
  await fetchStats()
  loading.value = false
})
</script>

<template>

  <div class="modal fade" id="addModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Добавить производителя процессора</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="onAdd">
            <div class="form-floating mb-3">
              <input type="text" class="form-control" v-model="itemToAdd.name" placeholder="Название" required>
              <label>Название производителя</label>
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

  <div class="modal fade" id="editModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать производителя</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="onUpdate">
            <div class="form-floating mb-3">
              <input type="text" class="form-control" v-model="itemToEdit.name" placeholder="Название" required>
              <label>Название производителя</label>
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
      <b>Статистика:</b> Количество производителей: {{ stats.count }}
    </div>

    <!-- Список производителей с аккордеоном -->
    <div v-for="brand in items" :key="brand.id" class="brand-card">
      <div class="brand-header" @click="toggleBrand(brand.id)">
        <div class="brand-info">
          <b>{{ brand.name }}</b>
          <img v-if="brand.picture" :src="brand.picture" style="max-height:40px; margin-left:10px; cursor:pointer" @click.stop="openImage(brand.picture)">
        </div>
        <div class="brand-actions">
          <button class="btn btn-sm btn-success" @click.stop="onEditClick(brand)" data-bs-toggle="modal" data-bs-target="#editModal">✎</button>
          <button class="btn btn-sm btn-danger" @click.stop="onRemove(brand)">✖</button>
          <span class="toggle-icon">{{ expandedBrandId === brand.id ? '▲' : '▼' }}</span>
        </div>
      </div>
      <div v-if="expandedBrandId === brand.id" class="family-list">
        <div v-if="getFamiliesForBrand(brand.id).length === 0" class="text-muted">Нет линеек</div>
        <div v-for="fam in getFamiliesForBrand(brand.id)" :key="fam.id" class="family-item">
          <span>{{ fam.name }}</span>
          <img v-if="fam.picture" :src="fam.picture" style="max-height:30px; cursor:pointer" @click.stop="openImage(fam.picture)">
        </div>
      </div>
    </div>
  </div>

  <div v-if="selectedImage" class="image-modal" @click="closeImage">
    <img :src="selectedImage" class="image-modal-content">
  </div>
</template>

<style scoped>
.brand-card {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  margin-bottom: 8px;
  overflow: hidden;
}
.brand-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: #f8f9fa;
  cursor: pointer;
  transition: background 0.2s;
}
.brand-header:hover {
  background: #e9ecef;
}
.brand-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
.brand-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.toggle-icon {
  font-size: 0.8rem;
  margin-left: 8px;
}
.family-list {
  padding: 10px 15px;
  background: #fff;
  border-top: 1px solid #dee2e6;
}
.family-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 0;
}
.image-modal {
  position: fixed; top:0; left:0; width:100%; height:100%;
  background: rgba(0,0,0,0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}
.image-modal-content { max-width:90%; max-height:90%; }
</style>