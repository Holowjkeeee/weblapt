<script setup>
import { computed, ref, onBeforeMount } from 'vue'
import axios from '@/api/axios'
import { useUserStore } from '@/stores/user'
import _ from 'lodash'

const userStore = useUserStore()
const isAuthenticated = computed(() => userStore.isAuthenticated)

const laptops = ref([])
const brands = ref([])
const processorBrands = ref([])
const processorFamilies = ref([])

const laptopToAdd = ref({
  name: '',
  description: '',
  brand: null,
  processor_brand: null,
  processor_family: null,
  processor_model: '',
  price: '',
  ram: '',
  storage: ''
})

const laptopToEdit = ref({
  id: null,
  name: '',
  description: '',
  brand: null,
  processor_brand: null,
  processor_family: null,
  processor_model: '',
  price: '',
  ram: '',
  storage: ''
})

const newFamily = ref({
  brand: null,
  name: ''
})

const loading = ref(false)
const errorMessage = ref('')
const stats = ref(null)

const laptopsPictureRef = ref(null)
const laptopEditPictureRef = ref(null)

const laptopAddImageUrl = ref(null)
const laptopEditImageUrl = ref(null)
const selectedImage = ref(null)

const filters = ref({
  brand: null,
  processor_brand: null,
  processor_family: null,
  price_min: '',
  price_max: '',
  ram: '',
  storage: '',
  name: ''
})

const brandsById = computed(() => _.keyBy(brands.value, 'id'))
const processorBrandsById = computed(() => _.keyBy(processorBrands.value, 'id'))
const processorFamiliesById = computed(() => _.keyBy(processorFamilies.value, 'id'))

const filteredFamiliesForAdd = computed(() => {
  if (!laptopToAdd.value.processor_brand) {
    return []
  }

  return processorFamilies.value.filter(
    family => family.brand === laptopToAdd.value.processor_brand
  )
})

const filteredFamiliesForEdit = computed(() => {
  if (!laptopToEdit.value.processor_brand) {
    return []
  }

  return processorFamilies.value.filter(
    family => family.brand === laptopToEdit.value.processor_brand
  )
})

const filteredProcessorFamilies = computed(() => {
  if (!filters.value.processor_brand) {
    return processorFamilies.value
  }

  return processorFamilies.value.filter(
    family => family.brand === filters.value.processor_brand
  )
})

function openImage(url) {
  selectedImage.value = url
}

function closeImage() {
  selectedImage.value = null
}

function resetLaptopToAdd() {
  laptopToAdd.value = {
    name: '',
    description: '',
    brand: null,
    processor_brand: null,
    processor_family: null,
    processor_model: '',
    price: '',
    ram: '',
    storage: ''
  }

  laptopAddImageUrl.value = null

  if (laptopsPictureRef.value) {
    laptopsPictureRef.value.value = null
  }
}

function resetLaptopToEdit() {
  laptopToEdit.value = {
    id: null,
    name: '',
    description: '',
    brand: null,
    processor_brand: null,
    processor_family: null,
    processor_model: '',
    price: '',
    ram: '',
    storage: ''
  }

  laptopEditImageUrl.value = null

  if (laptopEditPictureRef.value) {
    laptopEditPictureRef.value.value = null
  }
}

async function fetchBrands() {
  try {
    const response = await axios.get('/api/brands/')
    brands.value = response.data
  } catch {
    errorMessage.value = 'Не удалось загрузить бренды'
  }
}

async function fetchProcessorBrands() {
  try {
    const response = await axios.get('/api/processor-brands/')
    processorBrands.value = response.data
  } catch {
    errorMessage.value = 'Не удалось загрузить производителей процессоров'
  }
}

async function fetchProcessorFamilies() {
  try {
    const response = await axios.get('/api/processor-families/')
    processorFamilies.value = response.data
  } catch {
    errorMessage.value = 'Не удалось загрузить линейки процессоров'
  }
}

async function fetchLaptops() {
  try {
    const response = await axios.get('/api/laptops/')
    laptops.value = response.data
  } catch {
    laptops.value = []
    errorMessage.value = 'Не удалось загрузить ноутбуки'
  }
}

async function fetchStats() {
  try {
    const response = await axios.get('/api/laptops/stats/')
    stats.value = response.data
  } catch {
    stats.value = null
  }
}

async function applyFilters() {
  loading.value = true
  errorMessage.value = ''

  try {
    const params = {}

    if (filters.value.brand) {
      params.brand = filters.value.brand
    }

    if (filters.value.processor_brand) {
      params.processor_brand = filters.value.processor_brand
    }

    if (filters.value.processor_family) {
      params.processor_family = filters.value.processor_family
    }

    if (filters.value.price_min) {
      params.price_min = filters.value.price_min
    }

    if (filters.value.price_max) {
      params.price_max = filters.value.price_max
    }

    if (filters.value.ram) {
      params.ram = filters.value.ram
    }

    if (filters.value.storage) {
      params.storage = filters.value.storage
    }

    if (filters.value.name) {
      params.name = filters.value.name
    }

    const response = await axios.get('/api/laptops/', {
      params
    })

    laptops.value = response.data

    await fetchStats()
  } catch {
    errorMessage.value = 'Ошибка применения фильтров'
  } finally {
    loading.value = false
  }
}

async function resetFilters() {
  filters.value = {
    brand: null,
    processor_brand: null,
    processor_family: null,
    price_min: '',
    price_max: '',
    ram: '',
    storage: '',
    name: ''
  }

  await fetchLaptops()
  await fetchStats()
}

async function onLaptopAdd() {
  loading.value = true
  errorMessage.value = ''

  try {
    const formData = new FormData()

    formData.set('name', laptopToAdd.value.name || '')
    formData.set('description', laptopToAdd.value.description || '')
    formData.set('brand', laptopToAdd.value.brand || '')
    formData.set(
      'processor_family',
      laptopToAdd.value.processor_family || ''
    )
    formData.set(
      'processor_model',
      laptopToAdd.value.processor_model || ''
    )
    formData.set('price', laptopToAdd.value.price || 0)
    formData.set('ram', laptopToAdd.value.ram || '')
    formData.set('storage', laptopToAdd.value.storage || '')

    if (laptopsPictureRef.value?.files?.[0]) {
      formData.append(
        'picture',
        laptopsPictureRef.value.files[0]
      )
    }

    await axios.post('/api/laptops/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    resetLaptopToAdd()

    await fetchLaptops()
    await fetchStats()

    const modalElement = document.getElementById('addLaptopModal')

    if (modalElement && window.bootstrap) {
      const modal = window.bootstrap.Modal.getInstance(modalElement)

      if (modal) {
        modal.hide()
      }
    }
  } catch {
    errorMessage.value = 'Не удалось добавить ноутбук.'
  } finally {
    loading.value = false
  }
}

async function onLaptopEditClick(laptop) {
  const family = processorFamilies.value.find(
    item => item.id === laptop.processor_family
  )

  laptopToEdit.value = {
    id: laptop.id,
    name: laptop.name || '',
    description: laptop.description || '',
    brand: laptop.brand || null,
    processor_brand: family ? family.brand : null,
    processor_family: laptop.processor_family || null,
    processor_model: laptop.processor_model || '',
    price: laptop.price || '',
    ram: laptop.ram || '',
    storage: laptop.storage || ''
  }

  laptopEditImageUrl.value = laptop.picture || null

  if (laptopEditPictureRef.value) {
    laptopEditPictureRef.value.value = null
  }
}

async function onUpdateLaptop() {
  loading.value = true
  errorMessage.value = ''

  try {
    const formData = new FormData()

    formData.set('name', laptopToEdit.value.name || '')
    formData.set(
      'description',
      laptopToEdit.value.description || ''
    )
    formData.set('brand', laptopToEdit.value.brand || '')
    formData.set(
      'processor_family',
      laptopToEdit.value.processor_family || ''
    )
    formData.set(
      'processor_model',
      laptopToEdit.value.processor_model || ''
    )
    formData.set('price', laptopToEdit.value.price || 0)
    formData.set('ram', laptopToEdit.value.ram || '')
    formData.set('storage', laptopToEdit.value.storage || '')

    if (laptopEditPictureRef.value?.files?.[0]) {
      formData.append(
        'picture',
        laptopEditPictureRef.value.files[0]
      )
    }

    await axios.patch(
      `/api/laptops/${laptopToEdit.value.id}/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    resetLaptopToEdit()

    await fetchLaptops()
    await fetchStats()
  } catch {
    errorMessage.value = 'Не удалось обновить ноутбук.'
  } finally {
    loading.value = false
  }
}

async function onRemoveClick(laptop) {
  if (!confirm(`Удалить ноутбук «${laptop.name}»?`)) {
    return
  }

  try {
    await axios.delete(`/api/laptops/${laptop.id}/`)
    await fetchLaptops()
    await fetchStats()
  } catch {
    errorMessage.value = 'Не удалось удалить ноутбук.'
  }
}

async function onProcessorFamilyAdd() {
  try {
    await axios.post('/api/processor-families/', {
      brand: newFamily.value.brand,
      name: newFamily.value.name
    })

    await fetchProcessorFamilies()

    const added = processorFamilies.value.find(
      family =>
        family.brand === newFamily.value.brand &&
        family.name === newFamily.value.name
    )

    if (added) {
      laptopToAdd.value.processor_brand = newFamily.value.brand
      laptopToAdd.value.processor_family = added.id
    }

    newFamily.value = {
      brand: null,
      name: ''
    }

    errorMessage.value = ''

    const modalElement = document.getElementById(
      'addProcessorFamilyModal'
    )

    if (modalElement && window.bootstrap) {
      const modal = window.bootstrap.Modal.getInstance(modalElement)

      if (modal) {
        modal.hide()
      }
    }
  } catch {
    errorMessage.value =
      'Не удалось добавить линейку процессора'
  }
}

function laptopsAddPictureChange() {
  if (laptopsPictureRef.value?.files?.[0]) {
    laptopAddImageUrl.value = URL.createObjectURL(
      laptopsPictureRef.value.files[0]
    )
  }
}

function laptopsEditPictureChange() {
  if (laptopEditPictureRef.value?.files?.[0]) {
    laptopEditImageUrl.value = URL.createObjectURL(
      laptopEditPictureRef.value.files[0]
    )
  }
}
async function exportLaptopsToExcelLink() {
  const response = await axios.get(
    '/api/laptops/export-excel/'
  )
}

async function exportLaptopsToExcel() {
  try {
    const response = await axios.get(
      '/api/laptops/export-excel/',
      {
        responseType: 'blob'
      }
    )

    const blob = new Blob(
      [response.data],
      {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      }
    )

    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')

    link.href = url
    link.download = 'laptops.xlsx'

    document.body.appendChild(link)
    link.click()
    link.remove()

    window.URL.revokeObjectURL(url)
  } catch {
    errorMessage.value =
      'Не удалось скачать Excel-файл.'
  }
}

onBeforeMount(async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    await fetchBrands()
    await fetchProcessorBrands()
    await fetchProcessorFamilies()
    await fetchLaptops()
    await fetchStats()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div
    class="modal fade"
    id="addLaptopModal"
    tabindex="-1"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            Добавление ноутбука
          </h5>

          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
          ></button>
        </div>

        <form @submit.prevent="onLaptopAdd">
          <div class="modal-body">
            <div class="row">
              <div class="col-md-6">
                <div class="form-floating mb-3">
                  <input
                    type="text"
                    class="form-control"
                    v-model="laptopToAdd.name"
                    placeholder="Модель"
                    required
                  >
                  <label>Модель ноутбука</label>
                </div>
              </div>

              <div class="col-md-6">
                <div class="form-floating mb-3">
                  <select
                    class="form-select"
                    v-model="laptopToAdd.brand"
                    required
                  >
                    <option
                      :value="null"
                    >
                      Выберите бренд
                    </option>

                    <option
                      v-for="brand in brands"
                      :key="brand.id"
                      :value="brand.id"
                    >
                      {{ brand.name }}
                    </option>
                  </select>

                  <label>Бренд</label>
                </div>
              </div>

              <div class="col-md-6">
                <div class="form-floating mb-3">
                  <select
                    class="form-select"
                    v-model="laptopToAdd.processor_brand"
                    required
                  >
                    <option
                      :value="null"
                    >
                      Выберите производителя
                    </option>

                    <option
                      v-for="brand in processorBrands"
                      :key="brand.id"
                      :value="brand.id"
                    >
                      {{ brand.name }}
                    </option>
                  </select>

                  <label>
                    Производитель CPU
                  </label>
                </div>
              </div>

              <div class="col-md-6">
                <div class="form-floating mb-3">
                  <select
                    class="form-select"
                    v-model="laptopToAdd.processor_family"
                    required
                  >
                    <option
                      :value="null"
                    >
                      Выберите линейку
                    </option>

                    <option
                      v-for="family in filteredFamiliesForAdd"
                      :key="family.id"
                      :value="family.id"
                    >
                      {{ family.name }}
                    </option>
                  </select>

                  <label>
                    Линейка CPU
                  </label>
                </div>

                <button
                  type="button"
                  class="btn btn-outline-secondary btn-sm mb-3"
                  data-bs-toggle="modal"
                  data-bs-target="#addProcessorFamilyModal"
                >
                  + Новая линейка
                </button>
              </div>

              <div class="col-md-4">
                <div class="form-floating mb-3">
                  <input
                    type="text"
                    class="form-control"
                    v-model="laptopToAdd.processor_model"
                    placeholder="Модель CPU"
                  >

                  <label>
                    Модель CPU
                  </label>
                </div>
              </div>

              <div class="col-md-4">
                <div class="form-floating mb-3">
                  <input
                    type="number"
                    step="0.01"
                    class="form-control"
                    v-model="laptopToAdd.price"
                    placeholder="Цена"
                    required
                  >

                  <label>
                    Цена (руб.)
                  </label>
                </div>
              </div>

              <div class="col-md-4">
                <div class="form-floating mb-3">
                  <input
                    type="text"
                    class="form-control"
                    v-model="laptopToAdd.ram"
                    placeholder="ОЗУ"
                  >

                  <label>
                    ОЗУ
                  </label>
                </div>
              </div>

              <div class="col-md-4">
                <div class="form-floating mb-3">
                  <input
                    type="text"
                    class="form-control"
                    v-model="laptopToAdd.storage"
                    placeholder="SSD"
                  >

                  <label>
                    SSD
                  </label>
                </div>
              </div>

              <div class="col-12">
                <div class="form-floating mb-3">
                  <textarea
                    class="form-control"
                    v-model="laptopToAdd.description"
                    placeholder="Описание"
                    style="height: 100px"
                    required
                  ></textarea>

                  <label>
                    Описание
                  </label>
                </div>
              </div>

              <div class="col-md-8">
                <input
                  class="form-control"
                  type="file"
                  ref="laptopsPictureRef"
                  @change="laptopsAddPictureChange"
                  accept="image/*"
                >
              </div>

              <div
                class="col-md-4"
                v-if="laptopAddImageUrl"
              >
                <img
                  :src="laptopAddImageUrl"
                  class="preview-image"
                  @click="openImage(laptopAddImageUrl)"
                >
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              data-bs-dismiss="modal"
              @click="resetLaptopToAdd"
            >
              Отмена
            </button>

            <button
              type="submit"
              class="btn btn-primary"
              :disabled="loading"
            >
              {{ loading ? 'Добавление...' : 'Добавить' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <div
    class="modal fade"
    id="addProcessorFamilyModal"
    tabindex="-1"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            Новая линейка процессора
          </h5>

          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
          ></button>
        </div>

        <div class="modal-body">
          <form @submit.prevent="onProcessorFamilyAdd">
            <div class="form-floating mb-3">
              <select
                class="form-select"
                v-model="newFamily.brand"
                required
              >
                <option
                  :value="null"
                >
                  Выберите производителя
                </option>

                <option
                  v-for="brand in processorBrands"
                  :key="brand.id"
                  :value="brand.id"
                >
                  {{ brand.name }}
                </option>
              </select>

              <label>
                Производитель
              </label>
            </div>

            <div class="form-floating mb-3">
              <input
                type="text"
                class="form-control"
                v-model="newFamily.name"
                placeholder="Название линейки"
                required
              >

              <label>
                Название линейки
              </label>
            </div>

            <button
              type="submit"
              class="btn btn-primary"
            >
              Добавить
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>

  <div
    class="modal fade"
    id="editLaptopModal"
    tabindex="-1"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            Редактирование ноутбука
          </h5>

          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
          ></button>
        </div>

        <div class="modal-body">
          <div class="row">
            <div class="col-md-6">
              <div class="form-floating mb-3">
                <input
                  type="text"
                  class="form-control"
                  v-model="laptopToEdit.name"
                  placeholder="Модель"
                >

                <label>
                  Модель ноутбука
                </label>
              </div>
            </div>

            <div class="col-md-6">
              <div class="form-floating mb-3">
                <select
                  class="form-select"
                  v-model="laptopToEdit.brand"
                >
                  <option
                    v-for="brand in brands"
                    :key="brand.id"
                    :value="brand.id"
                  >
                    {{ brand.name }}
                  </option>
                </select>

                <label>
                  Бренд
                </label>
              </div>
            </div>

            <div class="col-md-4">
              <div class="form-floating mb-3">
                <select
                  class="form-select"
                  v-model="laptopToEdit.processor_brand"
                >
                  <option
                    :value="null"
                  >
                    Выберите производителя
                  </option>

                  <option
                    v-for="brand in processorBrands"
                    :key="brand.id"
                    :value="brand.id"
                  >
                    {{ brand.name }}
                  </option>
                </select>

                <label>
                  Производитель CPU
                </label>
              </div>
            </div>

            <div class="col-md-4">
              <div class="form-floating mb-3">
                <select
                  class="form-select"
                  v-model="laptopToEdit.processor_family"
                >
                  <option
                    :value="null"
                  >
                    Выберите линейку
                  </option>

                  <option
                    v-for="family in filteredFamiliesForEdit"
                    :key="family.id"
                    :value="family.id"
                  >
                    {{ family.name }}
                  </option>
                </select>

                <label>
                  Линейка CPU
                </label>
              </div>
            </div>

            <div class="col-md-4">
              <div class="form-floating mb-3">
                <input
                  type="text"
                  class="form-control"
                  v-model="laptopToEdit.processor_model"
                  placeholder="Модель CPU"
                >

                <label>
                  Модель CPU
                </label>
              </div>
            </div>

            <div class="col-md-4">
              <div class="form-floating mb-3">
                <input
                  type="number"
                  step="0.01"
                  class="form-control"
                  v-model="laptopToEdit.price"
                  placeholder="Цена"
                >

                <label>
                  Цена (руб.)
                </label>
              </div>
            </div>

            <div class="col-md-4">
              <div class="form-floating mb-3">
                <input
                  type="text"
                  class="form-control"
                  v-model="laptopToEdit.ram"
                  placeholder="ОЗУ"
                >

                <label>
                  ОЗУ
                </label>
              </div>
            </div>

            <div class="col-md-4">
              <div class="form-floating mb-3">
                <input
                  type="text"
                  class="form-control"
                  v-model="laptopToEdit.storage"
                  placeholder="SSD"
                >

                <label>
                  SSD
                </label>
              </div>
            </div>

            <div class="col-12">
              <div class="form-floating mb-3">
                <textarea
                  class="form-control"
                  v-model="laptopToEdit.description"
                  style="height: 100px"
                ></textarea>

                <label>
                  Описание
                </label>
              </div>
            </div>

            <div class="col-md-8">
              <input
                class="form-control"
                type="file"
                ref="laptopEditPictureRef"
                @change="laptopsEditPictureChange"
                accept="image/*"
              >
            </div>

            <div
              class="col-md-4"
              v-if="laptopEditImageUrl"
            >
              <img
                :src="laptopEditImageUrl"
                class="preview-image"
                @click="openImage(laptopEditImageUrl)"
              >
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            data-bs-dismiss="modal"
          >
            Закрыть
          </button>

          <button
            type="button"
            class="btn btn-primary"
            @click="onUpdateLaptop"
            :disabled="loading"
            data-bs-dismiss="modal"
          >
            Сохранить
          </button>
        </div>
      </div>
    </div>
  </div>

  <div class="container-fluid">
    <div class="card mb-4 p-3">
      <h5>Фильтры</h5>

      <div class="row g-2">
        <div class="col-md-2">
          <select
            class="form-select"
            v-model="filters.brand"
          >
            <option :value="null">
              Все бренды
            </option>

            <option
              v-for="brand in brands"
              :key="brand.id"
              :value="brand.id"
            >
              {{ brand.name }}
            </option>
          </select>
        </div>

        <div class="col-md-2">
          <select
            class="form-select"
            v-model="filters.processor_brand"
          >
            <option :value="null">
              Все производители CPU
            </option>

            <option
              v-for="brand in processorBrands"
              :key="brand.id"
              :value="brand.id"
            >
              {{ brand.name }}
            </option>
          </select>
        </div>

        <div class="col-md-2">
          <select
            class="form-select"
            v-model="filters.processor_family"
          >
            <option :value="null">
              Все линейки CPU
            </option>

            <option
              v-for="family in filteredProcessorFamilies"
              :key="family.id"
              :value="family.id"
            >
              {{ family.name }}
            </option>
          </select>
        </div>

        <div class="col-md-2">
          <input
            type="text"
            class="form-control"
            v-model="filters.name"
            placeholder="Поиск по названию"
          >
        </div>

        <div class="col-md-2">
          <input
            type="number"
            class="form-control"
            v-model="filters.price_min"
            placeholder="Цена от"
          >
        </div>

        <div class="col-md-2">
          <input
            type="number"
            class="form-control"
            v-model="filters.price_max"
            placeholder="Цена до"
          >
        </div>

        <div class="col-md-2">
          <input
            type="text"
            class="form-control"
            v-model="filters.ram"
            placeholder="ОЗУ"
          >
        </div>

        <div class="col-md-2">
          <input
            type="text"
            class="form-control"
            v-model="filters.storage"
            placeholder="SSD"
          >
        </div>

        <div class="col-md-auto">
          <button
            class="btn btn-primary"
            @click="applyFilters"
          >
            Применить
          </button>

          <button
            class="btn btn-secondary ms-2"
            @click="resetFilters"
          >
            Сбросить
          </button>
        </div>
      </div>
    </div>

    <div class="d-flex gap-2 mb-3">
      <button
        v-if="isAuthenticated"
        class="btn btn-primary"
        data-bs-toggle="modal"
        data-bs-target="#addLaptopModal"
      >
        + Добавить ноутбук
      </button>

      <button
        class="btn btn-success"
        @click="exportLaptopsToExcel"
      >
        Скачать Excel
      </button>

      <a href="/api/laptops/export-excel/" class="btn btn-danger">  
      Скачать Excel
      </a>
      
      
    </div>

    <div
      v-if="loading"
      class="mb-3"
    >
      Загрузка...
    </div>

    <div
      v-if="errorMessage"
      class="alert alert-warning"
    >
      {{ errorMessage }}
    </div>

    <div
      v-if="stats"
      class="alert alert-info"
    >
      <b>Статистика по ноутбукам</b><br>
      Количество: {{ stats.count }}<br>
      Средняя цена:
      {{ stats.avg ? Number(stats.avg).toFixed(2) : '-' }}<br>
      Максимальная цена:
      {{ stats.max ?? '-' }}<br>
      Минимальная цена:
      {{ stats.min ?? '-' }}
    </div>

    <div
      v-for="item in laptops"
      :key="item.id"
      class="laptops-item"
    >
      <div class="laptop-main">
        <b>{{ item.name }}</b>

        <div>
          {{ item.description }}
        </div>

        <small>
          ОЗУ:
          {{ item.ram || '-' }}
          |
          SSD:
          {{ item.storage || '-' }}
          <br>

          Процессор:
          {{
            processorBrandsById[
              item.processor_family
                ? processorFamiliesById[item.processor_family]?.brand
                : null
            ]?.name || '-'
          }}

          {{
            processorFamiliesById[item.processor_family]?.name || '-'
          }}

          {{ item.processor_model || '' }}
        </small>
      </div>

      <div class="laptop-meta">
        <span>
          {{ brandsById[item.brand]?.name || '-' }}
        </span>

        <span>
          {{ item.price }} руб.
        </span>
      </div>

      <div v-if="item.picture">
        <img
          :src="item.picture"
          class="laptop-image"
          @click="openImage(item.picture)"
        >
      </div>

      <button
        v-if="isAuthenticated"
        class="btn btn-success btn-sm"
        @click="onLaptopEditClick(item)"
        data-bs-toggle="modal"
        data-bs-target="#editLaptopModal"
      >
        ✎
      </button>

      <button
        v-if="isAuthenticated"
        class="btn btn-danger btn-sm"
        @click="onRemoveClick(item)"
      >
        ✖
      </button>
    </div>

    <div
      v-if="!loading && laptops.length === 0"
      class="text-muted"
    >
      Ноутбуки не найдены.
    </div>
  </div>

  <div
    v-if="selectedImage"
    class="image-modal"
    @click="closeImage"
  >
    <img
      :src="selectedImage"
      class="image-modal-content"
    >
  </div>
</template>

<style scoped>
.laptops-item {
  display: grid;
  grid-template-columns: 2fr 1.5fr auto auto auto;
  align-items: center;
  gap: 16px;
  padding: 0.75rem;
  margin: 0.5rem 0;
  border: 1px solid silver;
  border-radius: 8px;
}

.laptop-main {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.laptop-meta {
  display: grid;
  gap: 4px;
}

.laptop-image {
  max-height: 60px;
  max-width: 100px;
  cursor: pointer;
  object-fit: contain;
}

.preview-image {
  max-height: 60px;
  max-width: 100px;
  cursor: pointer;
  object-fit: contain;
}

.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.image-modal-content {
  max-height: 90%;
  max-width: 90%;
}
</style>