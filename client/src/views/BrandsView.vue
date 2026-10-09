<script setup>
import { computed, ref, onBeforeMount } from 'vue'
import axios from 'axios'

const brands = ref([])
const laptops = ref([])
const selectedBrandId = ref(null)
const brandToAdd = ref({})
const brandToEdit = ref({})
const loading = ref(false)

const brandsPictureRef = ref()
const brandAddImageUrl = ref(null)

const brandEditPictureRef = ref()
const brandEditImageUrl = ref(null)

const selectedImage = ref(null)

const filteredLaptops = computed(() => {
  if (!selectedBrandId.value) return laptops.value
  return laptops.value.filter(x => x.brand === selectedBrandId.value)
})

function openImage(url) {
  selectedImage.value = url
}

function closeImage() {
  selectedImage.value = null
}

async function fetchBrands() {
  const r = await axios.get('/api/brands/')
  brands.value = r.data
}

async function fetchLaptops() {
  const r = await axios.get('/api/laptops/')
  laptops.value = r.data
}

async function onBrandAdd() {
  const formData = new FormData()
  if (brandsPictureRef.value?.files?.[0]) {
    formData.append('picture', brandsPictureRef.value.files[0])
  }
  formData.set('name', brandToAdd.value.name || '')
  await axios.post('/api/brands/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  brandToAdd.value = {}
  brandAddImageUrl.value = null
  if (brandsPictureRef.value) brandsPictureRef.value.value = null
  await fetchBrands()
}

async function onBrandEditClick(brand) {
  brandToEdit.value = { ...brand }
  brandEditImageUrl.value = brand.picture || null
  if (brandEditPictureRef.value) brandEditPictureRef.value.value = null
}

async function onUpdateBrand() {
  const formData = new FormData()
  if (brandEditPictureRef.value?.files?.[0]) {
    formData.append('picture', brandEditPictureRef.value.files[0])
  }
  formData.set('name', brandToEdit.value.name || '')
  await axios.put(`/api/brands/${brandToEdit.value.id}/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  brandToEdit.value = {}
  brandEditImageUrl.value = null
  if (brandEditPictureRef.value) brandEditPictureRef.value.value = null
  await fetchBrands()
}

async function onRemoveClick(brand) {
  await axios.delete(`/api/brands/${brand.id}/`)
  await fetchBrands()
  if (selectedBrandId.value === brand.id) selectedBrandId.value = null
}

function brandsAddPictureChange() {
  if (brandsPictureRef.value?.files?.[0]) {
    brandAddImageUrl.value = URL.createObjectURL(brandsPictureRef.value.files[0])
  }
}

function brandsEditPictureChange() {
  if (brandEditPictureRef.value?.files?.[0]) {
    brandEditImageUrl.value = URL.createObjectURL(brandEditPictureRef.value.files[0])
  }
}

onBeforeMount(async () => {
  loading.value = true
  await fetchBrands()
  await fetchLaptops()
  loading.value = false
})
</script>

<template>
  <!-- Модалки для добавления/редактирования  -->
  <div class="modal fade" id="addBrandModal" tabindex="-1" aria-labelledby="addBrandModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="addBrandModalLabel">Добавление бренда</h1>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Закрыть"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="onBrandAdd">
            <div class="form-floating mb-3">
              <input type="text" class="form-control" id="brandName" placeholder="Название бренда" v-model="brandToAdd.name" required>
              <label for="brandName">Название бренда</label>
            </div>
            <div class="col-auto mb-3">
              <input class="form-control" type="file" ref="brandsPictureRef" @change="brandsAddPictureChange">
            </div>
            <div class="col-auto mb-3" v-if="brandAddImageUrl">
              <img :src="brandAddImageUrl" style="max-height: 60px; cursor: pointer;" @click="openImage(brandAddImageUrl)">
            </div>
            <button type="submit" class="btn btn-primary" data-bs-dismiss="modal">Добавить</button>
          </form>
        </div>
      </div>
    </div>
  </div>

  <div class="modal fade" id="editBrandModal" tabindex="-1" aria-labelledby="editBrandModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="editBrandModalLabel">Редактирование бренда</h1>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Закрыть"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="onUpdateBrand">
            <div class="form-floating mb-3">
              <input type="text" class="form-control" id="editBrandName" placeholder="Название бренда" v-model="brandToEdit.name" required>
              <label for="editBrandName">Название бренда</label>
            </div>
            <div class="col-12 mb-3">
              <input class="form-control" type="file" ref="brandEditPictureRef" @change="brandsEditPictureChange">
            </div>
            <div class="col-12 mb-3" v-if="brandEditImageUrl">
              <img :src="brandEditImageUrl" style="max-height: 60px; cursor: pointer;" @click="openImage(brandEditImageUrl)">
            </div>
            <button type="submit" class="btn btn-primary" data-bs-dismiss="modal">Сохранить изменения</button>
          </form>
        </div>
      </div>
    </div>
  </div>

  <!-- Основной контент -->
  <div class="container-fluid">
    <div class="row mb-3">
      <div class="col">
        <div class="form-floating">
          <select class="form-select" id="brandSelect" v-model="selectedBrandId">
            <option :value="null">Все бренды</option>
            <option :value="b.id" v-for="b in brands" :key="b.id">{{ b.name }}</option>
          </select>
          <label for="brandSelect">Выберите бренд</label>
        </div>
      </div>
      <div class="col-auto">
        <button type="button" class="btn btn-primary h-100" data-bs-toggle="modal" data-bs-target="#addBrandModal">Добавить</button>
      </div>
    </div>

    <div v-if="loading">Грузится...</div>

    <div v-for="item in brands" :key="item.id" class="brands-item">
      <b>{{ item.name }}</b>
      <div v-show="item.picture">
        <img :src="item.picture" style="max-height: 60px; cursor: pointer;" @click="openImage(item.picture)">
      </div>
      <button type="button" class="btn btn-success" @click="onBrandEditClick(item)" data-bs-toggle="modal" data-bs-target="#editBrandModal">
        <i class="bi bi-pen-fill"></i>
      </button>
      <button type="button" class="btn btn-danger" @click="onRemoveClick(item)">
        <i class="bi bi-trash-fill"></i>
      </button>
    </div>

    <hr class="my-4" />

    <div v-for="item in filteredLaptops" :key="item.id" class="laptops-item">
      <b>{{ item.name }}</b>
    </div>
  </div>

  <div v-if="selectedImage" class="image-modal" @click="closeImage">
    <img :src="selectedImage" class="image-modal-content">
  </div>
</template>

<style scoped>
.brands-item {
  display: grid;
  grid-template-columns: 1fr auto auto auto;
  align-items: center;
  gap: 16px;
  padding: 0.5rem;
  margin: 0.5rem 0;
  border: 1px solid silver;
  border-radius: 8px;
}
.laptops-item {
  display: grid;
  grid-template-columns: 1fr;
  padding: 0.5rem;
  margin: 0.5rem 0;
  border: 1px solid silver;
  border-radius: 8px;
}
.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.image-modal-content {
  max-width: 90%;
  max-height: 90%;
}
</style>