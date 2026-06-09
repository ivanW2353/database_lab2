<template>
  <section class="card">
    <div class="card-body">
      <h1 class="card-title">图书管理</h1>
      <details open class="mb-3"><summary>新增图书</summary>
        <form class="form-grid wide mt-3" @submit.prevent="save('book', book)">
          <label class="form-label">ISBN<input v-model="book.isbn" class="form-control" required></label>
          <label class="form-label">书名<input v-model="book.title" class="form-control" required></label>
          <label class="form-label">分类<select v-model="book.category_no" class="form-select"><option v-for="c in categories" :key="c.category_no" :value="c.category_no">{{ c.category_name }}</option></select></label>
          <label class="form-label">出版社
            <input list="publisherOptionsList" v-model="publisherTitle" class="form-control" placeholder="输入出版社名称或从下拉选择" />
            <datalist id="publisherOptionsList">
              <option v-for="p in publishers" :key="p.publisher_no" :value="p.publisher_name"></option>
            </datalist>
          </label>
          <label class="form-label">出版日期<input v-model="book.publish_date" type="date" class="form-control"></label>
          <label class="form-label">版次<input v-model="book.edition" class="form-control"></label>
          <label class="form-label">价格<input v-model="book.price" type="number" step="0.01" class="form-control"></label>
          <label class="form-label">语言<input v-model="book.language" class="form-control"></label>
          <label class="form-label span-2">简介<input v-model="book.summary" class="form-control"></label>
          <button class="btn btn-primary">保存图书</button>
        </form>
      </details>
      <details class="mb-3"><summary>新增馆藏副本</summary>
        <form class="form-grid mt-3" @submit.prevent="save('copy', copy)">
          <label class="form-label">图书
            <input list="bookOptionsList" v-model="copyTitle" class="form-control" placeholder="输入书名或从下拉选择" />
            <datalist id="bookOptionsList">
              <option v-for="b in bookOptions" :key="b.book_no" :value="b.title"></option>
            </datalist>
          </label>
          <label class="form-label">条码<input v-model="copy.barcode" class="form-control" required></label>
          <label class="form-label">位置<input v-model="copy.location" class="form-control" required></label>
          <label class="form-label">入库日期<input v-model="copy.purchase_date" type="date" class="form-control"></label>
          <button class="btn btn-primary">保存副本</button>
        </form>
      </details>
      <!-- 上传入口已移至图书详情模态 -->
      <div class="mb-3 d-flex" style="gap:8px;align-items:center;">
        <input v-model="searchKeyword" class="form-control" placeholder="按书名、ISBN 或作者搜索" @keyup.enter="doSearch" />
        <button class="btn btn-primary" @click="doSearch">搜索</button>
        <button class="btn btn-outline-secondary" @click="clearSearch">清除</button>
      </div>
      <SortableTable :columns="columns" :rows="books.map(b => ({...b, stock: `${b.available_count}/${b.copy_count}`}))" id-key="book_no">
        <template #actions="{ row }">
          <button class="btn btn-sm btn-outline-primary" @click="showDetail(row.book_no)">详情</button>
        </template>
      </SortableTable>
      <PaginationControls :pagination="pagination" unit="本" @change="changePage" />
      <BookDetailModal :book="selectedBook" editable-summary :allowUpload="true" @save-summary="saveSummary" @close="selectedBook = null" @uploaded="onMediaUploaded" @notice="(m) => emit('notice', m)" />
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { api } from '../api'
import SortableTable from '../components/SortableTable.vue'
import BookDetailModal from '../components/BookDetailModal.vue'
import PaginationControls from '../components/PaginationControls.vue'

const emit = defineEmits(['notice'])
const books = ref([])
const bookOptions = ref([])
const pagination = reactive({ page: 1, page_size: 10, total: 0, total_pages: 1 })
const selectedBook = ref(null)
const categories = ref([])
const publishers = ref([])
const columns = [['isbn', 'ISBN'], ['title', '书名'], ['category_name', '分类'], ['authors', '作者'], ['publisher_name', '出版社'], ['stock', '可借/馆藏']]
const book = reactive({ isbn: '', title: '', category_no: '', publisher_no: '', publish_date: '', edition: '', price: '', language: 'Chinese', summary: '' })
const copy = reactive({ book_no: '', barcode: '', location: '', purchase_date: localDate() })
const copyTitle = ref('')
const publisherTitle = ref('')
const media = reactive({ book_no: '' })
const mediaFile = ref(null)
const mediaFileInput = ref(null)
const searchKeyword = ref('')

function localDate() {
  const value = new Date()
  const year = value.getFullYear()
  const month = String(value.getMonth() + 1).padStart(2, '0')
  const day = String(value.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

async function load() {
  const keywordPart = searchKeyword.value ? `&keyword=${encodeURIComponent(searchKeyword.value)}` : ''
  const data = await api(`/api/admin/books?page=${pagination.page}&page_size=${pagination.page_size}${keywordPart}`)
  books.value = data.books
  bookOptions.value = data.book_options
  Object.assign(pagination, data.pagination)
  categories.value = data.categories
  publishers.value = data.publishers
  if (!book.category_no && categories.value[0]) book.category_no = categories.value[0].category_no
  if (!book.publisher_no && publishers.value[0]) book.publisher_no = publishers.value[0].publisher_no
  if (!copy.book_no && bookOptions.value[0]) copy.book_no = bookOptions.value[0].book_no
  if (!media.book_no && bookOptions.value[0]) media.book_no = bookOptions.value[0].book_no
  // initialize publisherTitle from current publisher_no when loading
  if (book.publisher_no) {
    const p = publishers.value.find(x => x.publisher_no === book.publisher_no)
    publisherTitle.value = p ? p.publisher_name : ''
  } else if (publishers.value[0]) {
    publisherTitle.value = publishers.value[0].publisher_name
  }
}

async function doSearch() {
  pagination.page = 1
  await load()
}

function clearSearch() {
  searchKeyword.value = ''
  doSearch()
}

async function changePage(page) {
  pagination.page = page
  await load()
}

async function save(action, form) {
  // ensure copy.book_no is resolved from copyTitle when saving a copy
  if (action === 'copy' && !form.book_no && copyTitle.value) {
    const found = bookOptions.value.find(b => b.title === copyTitle.value)
    if (found) form.book_no = found.book_no
  }
  if (action === 'copy' && !form.book_no) {
    emit('notice', '请选择有效的图书')
    return
  }
  // resolve publisher_no from input title when saving a book
  if (action === 'book') {
    if (publisherTitle.value) {
      const foundPub = publishers.value.find(p => p.publisher_name === publisherTitle.value)
      if (foundPub) form.publisher_no = foundPub.publisher_no
      else {
        emit('notice', '请选择有效的出版社')
        return
      }
    } else {
      form.publisher_no = ''
    }
  }
  const data = await api('/api/admin/books', { method: 'POST', body: { ...form, action } })
  emit('notice', data.message)
  if (action === 'copy') copy.purchase_date = localDate()
  await load()
}

function selectMediaFile(event) {
  mediaFile.value = event.target.files?.[0] || null
}

async function saveMedia() {
  const form = new FormData()
  form.append('action', 'media')
  form.append('book_no', media.book_no)
  if (mediaFile.value) form.append('file', mediaFile.value)
  const data = await api('/api/admin/books', { method: 'POST', body: form })
  emit('notice', data.message)
  mediaFile.value = null
  if (mediaFileInput.value) mediaFileInput.value.value = ''
  await load()
}

async function saveSummary(summary) {
  const data = await api('/api/admin/books', {
    method: 'POST',
    body: { action: 'summary', book_no: selectedBook.value.book_no, summary }
  })
  emit('notice', data.message)
  selectedBook.value.summary = summary
  await load()
}

async function showDetail(bookNo) {
  try {
    selectedBook.value = (await api('/api/admin/books/' + bookNo)).book
  } catch (err) {
    emit('notice', err.message)
  }
}

async function onMediaUploaded(message) {
  emit('notice', message)
  if (selectedBook.value?.book_no) {
    await showDetail(selectedBook.value.book_no)
  }
  await load()
}

onMounted(load)

// keep copyTitle and copy.book_no in sync
watch(() => copyTitle.value, (val) => {
  if (!val) {
    copy.book_no = ''
    return
  }
  const found = bookOptions.value.find(b => b.title === val)
  if (found) copy.book_no = found.book_no
})
watch(() => copy.book_no, (val) => {
  const found = bookOptions.value.find(b => b.book_no === val)
  copyTitle.value = found ? found.title : ''
})
// keep publisherTitle and book.publisher_no in sync
watch(() => publisherTitle.value, (val) => {
  if (!val) {
    book.publisher_no = ''
    return
  }
  const found = publishers.value.find(p => p.publisher_name === val)
  if (found) book.publisher_no = found.publisher_no
})
watch(() => book.publisher_no, (val) => {
  const found = publishers.value.find(p => p.publisher_no === val)
  publisherTitle.value = found ? found.publisher_name : ''
})
</script>
