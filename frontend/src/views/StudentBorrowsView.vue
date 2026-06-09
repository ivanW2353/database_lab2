<template>
  <section class="card">
    <div class="card-body">
      <h1 class="card-title">我的借阅</h1>
      <SortableTable :columns="columns" :rows="rows" id-key="borrow_no">
        <template #actions="{ row }">
          <div v-if="isActive(row)" class="d-flex gap-2">
            <button v-if="row.status === 'borrowed'" class="btn btn-sm btn-outline-primary" :disabled="busy" @click="operate('renew', row.borrow_no)">
              延期
            </button>
            <button class="btn btn-sm btn-outline-success" :disabled="busy" @click="operate('return', row.borrow_no)">
              还书
            </button>
          </div>
        </template>
      </SortableTable>
      <PaginationControls :pagination="pagination" @change="changePage" />
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api'
import SortableTable from '../components/SortableTable.vue'
import PaginationControls from '../components/PaginationControls.vue'

const emit = defineEmits(['notice'])
const rows = ref([])
const busy = ref(false)
const pagination = reactive({ page: 1, page_size: 10, total: 0, total_pages: 1 })
const columns = [
  ['borrow_code', '借阅编码'],
  ['title', '书名'],
  ['barcode', '条码'],
  ['borrow_time', '借出时间'],
  ['due_time', '应还时间'],
  ['return_time', '归还时间'],
  ['status', '状态']
]
function isActive(row) {
  return ['borrowed', 'overdue'].includes(row.status)
}

async function load() {
  const data = await api(`/api/student/borrows?page=${pagination.page}&page_size=${pagination.page_size}`)
  rows.value = data.rows
  Object.assign(pagination, data.pagination)
}
async function changePage(page) { pagination.page = page; await load() }

async function operate(action, borrowNo) {
  busy.value = true
  try {
    const data = await api(`/api/student/borrows/${action}`, {
      method: 'POST',
      body: { borrow_no: borrowNo }
    })
    emit('notice', data.message)
    await load()
  } catch (err) {
    emit('notice', err.message)
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>
