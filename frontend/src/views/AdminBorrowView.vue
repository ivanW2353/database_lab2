<template>
  <section class="card"><div class="card-body">
    <h1 class="card-title">办理借书</h1>
    <form class="form-grid mb-3" @submit.prevent="submit">
      <label class="form-label">学生学号<input v-model="form.student_id" class="form-control" required></label>
      <label class="form-label">图书条码<input v-model="form.barcode" class="form-control" required></label>
      <button class="btn btn-primary">确认借出</button>
    </form>
    <SortableTable :columns="columns" :rows="rows" id-key="barcode" />
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
const form = reactive({ student_id: '', barcode: '' })
const pagination = reactive({ page: 1, page_size: 10, total: 0, total_pages: 1 })
const columns = [['barcode', '条码'], ['title', '书名'], ['location', '位置'], ['status', '状态']]
async function load() { const data = await api(`/api/admin/borrow?page=${pagination.page}&page_size=${pagination.page_size}`); rows.value = data.rows; Object.assign(pagination, data.pagination) }
async function changePage(page) { pagination.page = page; await load() }
async function submit() { try { const data = await api('/api/admin/borrow', { method: 'POST', body: form }); emit('notice', data.message); await load() } catch (e) { emit('notice', e.message) } }
onMounted(load)
</script>
