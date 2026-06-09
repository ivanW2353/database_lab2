<template>
  <section class="card">
    <div class="card-body">
      <h1 class="card-title">图书检索</h1>
      <form class="d-flex gap-2 mb-3" @submit.prevent="searchBooks">
        <input v-model="keyword" class="form-control" placeholder="输入书名、ISBN 或作者">
        <button class="btn btn-primary">搜索</button>
      </form>
      <div class="section-label">图书分类</div>
      <div class="category-grid mb-3">
        <button type="button" class="category-btn" :class="{ active: allCategoriesSelected }" @click="selectAllCategories">
          <b>全部</b>
          <span>全部分类</span>
        </button>
        <button v-for="category in categories" :key="category.code" type="button" class="category-btn" :class="{ active: selectedCategoryCode === category.code }" @click="selectCategory(category.code)">
          <b>{{ category.code }}</b>
          <span>{{ category.name }}</span>
        </button>
      </div>
      <div v-if="fallbackMessage" class="alert alert-warning py-2">{{ fallbackMessage }}</div>
      <div class="text-muted mb-2">{{ resultSummary }}</div>
      <SortableTable :key="tableKey" :columns="columns" :rows="books" id-key="book_no">
        <template #actions="{ row }">
          <div class="d-flex flex-wrap gap-2">
            <button class="btn btn-sm btn-outline-primary" @click="showDetail(row.book_no)">详情</button>
            <button class="btn btn-sm btn-primary" @click="borrow(row.book_no)">借出</button>
            <button class="btn btn-sm btn-outline-primary" @click="reserve(row.book_no)">预约</button>
          </div>
        </template>
      </SortableTable>
      <PaginationControls :pagination="pagination" unit="本" @change="changePage" />
      <BookDetailModal :book="selectedBook" show-actions @borrow="borrow" @reserve="reserve" @close="selectedBook = null" />
    </div>
  </section>
  <div v-if="reservationBookNo" class="modal-backdrop" @click.self="cancelReservation">
    <section class="reservation-modal card">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-start gap-3 mb-3">
          <div>
            <h2 class="card-title mb-1">选择预约借出日期</h2>
            <div class="text-muted">预约用于指定未来借出日期；当前无可借馆藏时请点击“借出”加入队列。</div>
          </div>
          <button class="btn btn-outline-secondary btn-sm" @click="cancelReservation">关闭</button>
        </div>
        <label class="form-label">计划借出日期</label>
        <input v-model="reservationDate" class="form-control" type="date" :min="minReservationDate">
        <div class="detail-actions">
          <button class="btn btn-outline-secondary" @click="cancelReservation">取消</button>
          <button class="btn btn-primary" @click="submitReservation">确认预约</button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { api } from '../api'
import SortableTable from '../components/SortableTable.vue'
import BookDetailModal from '../components/BookDetailModal.vue'
import PaginationControls from '../components/PaginationControls.vue'

const props = defineProps({ route: { type: String, default: '/student/books' } })
const emit = defineEmits(['notice'])
const categoryNo = ref('')
const selectedCategoryCode = ref('')
const keyword = ref('')
const CLC_CATEGORIES = [
  { code: 'A', name: '马列主义、毛泽东思想、邓小平理论' },
  { code: 'B', name: '哲学、宗教' },
  { code: 'C', name: '社会科学总论' },
  { code: 'D', name: '政治、法律' },
  { code: 'E', name: '军事' },
  { code: 'F', name: '经济' },
  { code: 'G', name: '文化、科学、教育、体育' },
  { code: 'H', name: '语言、文字' },
  { code: 'I', name: '文学' },
  { code: 'J', name: '艺术' },
  { code: 'K', name: '历史、地理' },
  { code: 'N', name: '自然科学总论' },
  { code: 'O', name: '数理科学与化学' },
  { code: 'P', name: '天文学、地球科学' },
  { code: 'Q', name: '生物科学' },
  { code: 'R', name: '医药、卫生' },
  { code: 'S', name: '农业科学' },
  { code: 'T', name: '工业技术' },
  { code: 'U', name: '交通运输' },
  { code: 'V', name: '航空、航天' },
  { code: 'X', name: '环境科学,安全科学' },
  { code: 'Z', name: '综合性图书' }
]
const categories = ref(CLC_CATEGORIES)
const books = ref([])
const selectedBook = ref(null)
const reservationBookNo = ref('')
const reservationDate = ref('')
const tableKey = ref(0)
const fallbackMessage = ref('')
const pagination = ref({ page: 1, page_size: 10, total: 0, total_pages: 1 })
const columns = [['isbn', 'ISBN'], ['title', '书名'], ['category_name', '分类'], ['authors', '作者'], ['publisher_name', '出版社'], ['stock', '可借/馆藏']]
const allCategoriesSelected = computed(() => !selectedCategoryCode.value)
const minReservationDate = computed(() => {
  const next = new Date()
  next.setDate(next.getDate() + 1)
  const year = next.getFullYear()
  const month = String(next.getMonth() + 1).padStart(2, '0')
  const day = String(next.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
})
const resultSummary = computed(() => {
  const categoryText = allCategoriesSelected.value ? '全部分类' : selectedCategoryCode.value
  const keywordText = keyword.value.trim() ? `，关键词：${keyword.value.trim()}` : ''
  return `${categoryText}${keywordText}，共 ${pagination.value.total} 本图书`
})

function categoryNamesFor(code) {
  const names = {
    A: ['马列主义、毛泽东思想、邓小平理论', '马克思主义、列宁主义、毛泽东思想、邓小平理论'],
    B: ['哲学、宗教'],
    C: ['社会科学总论'],
    D: ['政治、法律'],
    E: ['军事'],
    F: ['经济'],
    G: ['文化、科学、教育、体育'],
    H: ['语言、文字'],
    I: ['文学'],
    J: ['艺术'],
    K: ['历史、地理'],
    N: ['自然科学总论'],
    O: ['数理科学与化学', '数理科学和化学', '数理科学'],
    P: ['天文学、地球科学'],
    Q: ['生物科学'],
    R: ['医药、卫生'],
    S: ['农业科学'],
    T: ['工业技术', '自动化技术、计算机技术'],
    U: ['交通运输'],
    V: ['航空、航天'],
    X: ['环境科学,安全科学', '环境科学、安全科学'],
    Z: ['综合性图书']
  }
  return names[code] || []
}

async function fetchBooks({ includeCategory = true } = {}) {
  const params = new URLSearchParams()
  if (keyword.value.trim()) params.set('q', keyword.value.trim())
  if (includeCategory && categoryNo.value) params.set('category_no', categoryNo.value)
  if (includeCategory && selectedCategoryCode.value) params.set('category_code', selectedCategoryCode.value)
  params.set('page', pagination.value.page)
  params.set('page_size', pagination.value.page_size)
  const data = await api('/api/books?' + params.toString())
  return {
    rows: data.books.map(book => ({ ...book, stock: `${book.available_count}/${book.copy_count}` })),
    pagination: data.pagination
  }
}

async function load() {
  fallbackMessage.value = ''
  const result = await fetchBooks()
  books.value = result.rows
  pagination.value = result.pagination
  tableKey.value += 1
}

async function searchBooks(resetPage = true) {
  if (resetPage) pagination.value.page = 1
  categoryNo.value = ''
  fallbackMessage.value = ''
  const categoryResult = await fetchBooks()
  if (keyword.value.trim() && selectedCategoryCode.value && categoryResult.pagination.total === 0) {
    const fallbackResult = await fetchBooks({ includeCategory: false })
    books.value = fallbackResult.rows
    pagination.value = fallbackResult.pagination
    fallbackMessage.value = `当前分类 ${selectedCategoryCode.value} 中没有找到“${keyword.value.trim()}”，已在全部分类中继续查找。`
  } else {
    books.value = categoryResult.rows
    pagination.value = categoryResult.pagination
  }
  tableKey.value += 1
}

async function selectAllCategories() {
  pagination.value.page = 1
  keyword.value = ''
  categoryNo.value = ''
  selectedCategoryCode.value = ''
  await load()
}

async function selectCategory(categoryCode) {
  pagination.value.page = 1
  keyword.value = ''
  categoryNo.value = ''
  selectedCategoryCode.value = categoryCode
  await load()
}

async function changePage(page) {
  pagination.value.page = page
  await searchBooks(false)
}

async function reserve(bookNo) {
  reservationBookNo.value = bookNo
  reservationDate.value = minReservationDate.value
}

function cancelReservation() {
  reservationBookNo.value = ''
  reservationDate.value = ''
}

async function submitReservation() {
  try {
    const data = await api('/api/student/reservations', {
      method: 'POST',
      body: { book_no: reservationBookNo.value, borrow_date: reservationDate.value }
    })
    emit('notice', data.message)
    selectedBook.value = null
    cancelReservation()
    await load()
  } catch (err) {
    emit('notice', err.message)
  }
}

async function borrow(bookNo) {
  try {
    const data = await api('/api/student/borrows', { method: 'POST', body: { book_no: bookNo } })
    emit('notice', data.message)
    selectedBook.value = null
    await load()
  } catch (err) {
    emit('notice', err.message)
  }
}

async function showDetail(bookNo) {
  try {
    selectedBook.value = (await api('/api/books/' + bookNo)).book
  } catch (err) {
    emit('notice', err.message)
  }
}

function applyRoute() {
  const query = props.route.split('?')[1] || ''
  const params = new URLSearchParams(query)
  keyword.value = params.get('q') || ''
  categoryNo.value = params.get('category_no') || ''
  selectedCategoryCode.value = (params.get('category_code') || '').split(',').filter(Boolean)[0] || ''
}

watch(() => props.route, async () => {
  applyRoute()
  await load()
})

onMounted(async () => {
  applyRoute()
  await load()
})
</script>
