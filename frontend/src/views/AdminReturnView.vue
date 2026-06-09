<template>
  <section class="card"><div class="card-body">
    <h1 class="card-title">办理还书</h1>
    <form class="d-flex gap-2 mb-3" @submit.prevent="search">
      <input v-model="keyword" class="form-control" placeholder="查询借阅编码、学号、姓名、书名或条码">
      <button class="btn btn-outline-primary">查询记录</button>
      <button type="button" class="btn btn-outline-secondary" @click="resetSearch">重置</button>
    </form>
    <SortableTable :columns="columns" :rows="rows" id-key="borrow_no">
      <template #actions="{ row }">
        <button class="btn btn-sm btn-primary" @click="submit(row)">确认归还</button>
      </template>
    </SortableTable>
    <PaginationControls :pagination="pagination" @change="changePage" />
  </div></section>
</template>
<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api'
import SortableTable from '../components/SortableTable.vue'
import PaginationControls from '../components/PaginationControls.vue'
const emit = defineEmits(['notice'])
const rows = ref([])
const keyword = ref('')
const pagination = reactive({ page: 1, page_size: 10, total: 0, total_pages: 1 })
const columns = [['borrow_code', '借阅编码'], ['student_id', '学号'], ['name', '姓名'], ['title', '书名'], ['barcode', '条码'], ['borrow_time', '借出时间'], ['due_time', '应还时间'], ['status', '状态']]
async function load() {
  const params = new URLSearchParams({ page: pagination.page, page_size: pagination.page_size })
  if (keyword.value.trim()) params.set('q', keyword.value.trim())
  const data = await api(`/api/admin/return?${params}`)
  rows.value = data.rows
  Object.assign(pagination, data.pagination)
}
async function search() { pagination.page = 1; await load() }
async function resetSearch() { keyword.value = ''; pagination.page = 1; await load() }
async function changePage(page) { pagination.page = page; await load() }
async function submit(row) {
  if (!window.confirm(`确认归还《${row.title}》（借阅编码 ${row.borrow_code}）？`)) return
  const data = await api('/api/admin/return', { method: 'POST', body: { borrow_no: row.borrow_no } })
  emit('notice', data.message)
  await load()
}
onMounted(load)
</script>
