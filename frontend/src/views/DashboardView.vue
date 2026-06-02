<template>
  <section class="card mb-3">
    <div class="card-body">
      <h1 class="card-title">{{ role === 'librarian' ? '管理员工作台' : '学生首页' }}</h1>
      <div class="stats">
        <div v-for="item in statItems" :key="item.label" class="stat-card"><b>{{ item.value }}</b><span>{{ item.label }}</span></div>
      </div>
    </div>
  </section>
  <section class="card mb-3">
    <div class="card-body">
      <h2 class="card-title">图书搜索</h2>
      <form class="d-flex gap-2" @submit.prevent="searchBooks">
        <input v-model="keyword" class="form-control" placeholder="输入书名、ISBN 或作者">
        <button class="btn btn-primary">搜索</button>
      </form>
    </div>
  </section>
  <section class="card">
    <div class="card-body">
      <h2 class="card-title">借阅排行前十</h2>
      <SortableTable :columns="columns" :rows="topBooks" id-key="book_no" />
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api'
import SortableTable from '../components/SortableTable.vue'

const props = defineProps({ role: { type: String, required: true } })
const emit = defineEmits(['notice', 'book-search'])
const stats = ref({})
const topBooks = ref([])
const keyword = ref('')
const columns = [['rank', '排名'], ['title', '书名'], ['isbn', 'ISBN'], ['authors', '作者'], ['borrow_count', '借阅次数']]

const statItems = computed(() => props.role === 'librarian'
  ? [
      { label: '图书种类', value: stats.value.books || 0 },
      { label: '馆藏副本', value: stats.value.copies || 0 },
      { label: '当前借出', value: stats.value.borrowed || 0 },
      { label: '待处理预约', value: stats.value.reservations || 0 }
    ]
  : [
      { label: '当前借阅', value: stats.value.borrow || 0 },
      { label: '有效预约', value: stats.value.reserve || 0 },
      { label: '未缴罚金', value: stats.value.fine || '0.00' }
    ])

onMounted(async () => {
  const data = await api(props.role === 'librarian' ? '/api/admin/dashboard' : '/api/student/dashboard')
  stats.value = data.stats
  topBooks.value = data.top_books.map((book, index) => ({ ...book, rank: index + 1 }))
})

function searchBooks() {
  emit('book-search', keyword.value.trim())
}
</script>
