<template>
  <section class="card">
    <div class="card-body">
      <h1 class="card-title">我的预约</h1>
      <form v-if="editing" class="d-flex align-items-end gap-2 mb-3" @submit.prevent="updateReservation">
        <label class="form-label mb-0">
          修改《{{ editing.title }}》的计划借出日期
          <input v-model="editingDate" type="date" class="form-control" :min="minimumDate" required>
        </label>
        <button class="btn btn-primary" :disabled="busy">保存修改</button>
        <button type="button" class="btn btn-outline-secondary" :disabled="busy" @click="stopEditing">取消</button>
      </form>
      <SortableTable :columns="columns" :rows="rows" id-key="reservation_no">
        <template #actions="{ row }">
          <div v-if="canModify(row)" class="d-flex gap-2">
            <button class="btn btn-sm btn-outline-primary" :disabled="busy" @click="startEditing(row)">修改时间</button>
            <button class="btn btn-sm btn-outline-danger" :disabled="busy" @click="cancelReservation(row)">取消预约</button>
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
const editing = ref(null)
const editingDate = ref('')
const busy = ref(false)
const pagination = reactive({ page: 1, page_size: 10, total: 0, total_pages: 1 })
const minimumDate = localDateAfter(1)
const columns = [
  ['reservation_code', '预约编码'],
  ['title', '书名'],
  ['reserved_at', '预约时间'],
  ['borrow_date', '计划借出日期'],
  ['expire_at', '过期时间'],
  ['status', '状态']
]

function canModify(row) {
  return ['waiting', 'notified'].includes(row.status)
}

function localDateAfter(days) {
  const value = new Date()
  value.setDate(value.getDate() + days)
  const year = value.getFullYear()
  const month = String(value.getMonth() + 1).padStart(2, '0')
  const day = String(value.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

async function load() {
  const data = await api(`/api/student/reservations?page=${pagination.page}&page_size=${pagination.page_size}`)
  rows.value = data.rows
  Object.assign(pagination, data.pagination)
}
async function changePage(page) { pagination.page = page; stopEditing(); await load() }

async function cancelReservation(row) {
  if (!window.confirm(`确认取消《${row.title}》的预约？`)) return
  busy.value = true
  try {
    const data = await api('/api/student/reservations', {
      method: 'DELETE',
      body: { reservation_no: row.reservation_no }
    })
    emit('notice', data.message)
    stopEditing()
    await load()
  } catch (err) {
    emit('notice', err.message)
  } finally {
    busy.value = false
  }
}

function startEditing(row) {
  editing.value = row
  editingDate.value = row.borrow_date || minimumDate
}

function stopEditing() {
  editing.value = null
  editingDate.value = ''
}

async function updateReservation() {
  busy.value = true
  try {
    const data = await api('/api/student/reservations', {
      method: 'PUT',
      body: { reservation_no: editing.value.reservation_no, borrow_date: editingDate.value }
    })
    emit('notice', data.message)
    stopEditing()
    await load()
  } catch (err) {
    emit('notice', err.message)
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>
