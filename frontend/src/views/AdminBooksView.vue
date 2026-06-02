<template>
  <section class="card">
    <div class="card-body">
      <h1 class="card-title">图书管理</h1>
      <details open class="mb-3"><summary>新增图书</summary>
        <form class="form-grid wide mt-3" @submit.prevent="save('book', book)">
          <label class="form-label">ISBN<input v-model="book.isbn" class="form-control" required></label>
          <label class="form-label">书名<input v-model="book.title" class="form-control" required></label>
          <label class="form-label">分类<select v-model="book.category_no" class="form-select"><option v-for="c in categories" :key="c.category_no" :value="c.category_no">{{ c.category_name }}</option></select></label>
          <label class="form-label">出版社<select v-model="book.publisher_no" class="form-select"><option v-for="p in publishers" :key="p.publisher_no" :value="p.publisher_no">{{ p.publisher_name }}</option></select></label>
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
          <label class="form-label">图书<select v-model="copy.book_no" class="form-select"><option v-for="b in books" :key="b.book_no" :value="b.book_no">{{ b.title }}</option></select></label>
          <label class="form-label">条码<input v-model="copy.barcode" class="form-control" required></label>
          <label class="form-label">位置<input v-model="copy.location" class="form-control" required></label>
          <label class="form-label">入库日期<input v-model="copy.purchase_date" type="date" class="form-control"></label>
          <button class="btn btn-primary">保存副本</button>
        </form>
      </details>
      <details class="mb-3"><summary>新增图片/视频/文件</summary>
        <form class="form-grid mt-3" @submit.prevent="save('media', media)">
          <label class="form-label">图书<select v-model="media.book_no" class="form-select"><option v-for="b in books" :key="b.book_no" :value="b.book_no">{{ b.title }}</option></select></label>
          <label class="form-label">类型<select v-model="media.media_type" class="form-select"><option value="image">图片</option><option value="video">视频</option><option value="file">文件</option></select></label>
          <label class="form-label">标题<input v-model="media.title" class="form-control" required></label>
          <label class="form-label">文件路径<input v-model="media.file_path" class="form-control" required></label>
          <label class="form-label">MIME<input v-model="media.mime_type" class="form-control"></label>
          <button class="btn btn-primary">保存资料</button>
        </form>
      </details>
      <SortableTable :columns="columns" :rows="books.map(b => ({...b, stock: `${b.available_count}/${b.copy_count}`}))" id-key="book_no">
        <template #actions="{ row }">
          <button class="btn btn-sm btn-outline-primary" @click="showDetail(row.book_no)">详情</button>
        </template>
      </SortableTable>
      <BookDetailModal :book="selectedBook" @close="selectedBook = null" />
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api'
import SortableTable from '../components/SortableTable.vue'
import BookDetailModal from '../components/BookDetailModal.vue'

const emit = defineEmits(['notice'])
const books = ref([])
const selectedBook = ref(null)
const categories = ref([])
const publishers = ref([])
const columns = [['isbn', 'ISBN'], ['title', '书名'], ['category_name', '分类'], ['authors', '作者'], ['publisher_name', '出版社'], ['stock', '可借/馆藏']]
const book = reactive({ isbn: '', title: '', category_no: '', publisher_no: '', publish_date: '', edition: '', price: '', language: 'Chinese', summary: '' })
const copy = reactive({ book_no: '', barcode: '', location: '', purchase_date: '' })
const media = reactive({ book_no: '', media_type: 'file', title: '', file_path: '', mime_type: '' })

async function load() {
  const data = await api('/api/admin/books')
  books.value = data.books
  categories.value = data.categories
  publishers.value = data.publishers
  if (!book.category_no && categories.value[0]) book.category_no = categories.value[0].category_no
  if (!book.publisher_no && publishers.value[0]) book.publisher_no = publishers.value[0].publisher_no
  if (!copy.book_no && books.value[0]) copy.book_no = books.value[0].book_no
  if (!media.book_no && books.value[0]) media.book_no = books.value[0].book_no
}

async function save(action, form) {
  const data = await api('/api/admin/books', { method: 'POST', body: { ...form, action } })
  emit('notice', data.message)
  await load()
}

async function showDetail(bookNo) {
  try {
    selectedBook.value = (await api('/api/books/' + bookNo)).book
  } catch (err) {
    emit('notice', err.message)
  }
}

onMounted(load)
</script>
