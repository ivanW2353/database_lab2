<template>
  <section class="card">
    <div class="card-body">
      <h1 class="card-title">我的预约</h1>
      <SortableTable :columns="columns" :rows="displayRows" id-key="reservation_no">
        <template #actions="{ row }">
          <button
            v-if="canCancel(row)"
            class="btn btn-sm btn-outline-danger"
            @click="cancelReservation(row)"
          >
            取消预约
          </button>
        </template>
      </SortableTable>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api'
import SortableTable from '../components/SortableTable.vue'

const emit = defineEmits(['notice'])
const rows = ref([])
const displayRows = computed(() => rows.value.map((row, index) => ({ ...row, display_no: index + 1 })))
const columns = [
  ['display_no', '编号'],
  ['title', '书名'],
  ['reserved_at', '预约时间'],
  ['borrow_date', '计划借出日期'],
  ['expire_at', '过期时间'],
  ['status', '状态']
]

function canCancel(row) {
  return ['waiting', 'notified'].includes(row.status)
}

async function load() {
  rows.value = (await api('/api/student/reservations')).rows
}

async function cancelReservation(row) {
  if (!window.confirm(`确认取消《${row.title}》的预约？`)) return
  try {
    const data = await api('/api/student/reservations', {
      method: 'DELETE',
      body: { reservation_no: row.reservation_no }
    })
    emit('notice', data.message)
    await load()
  } catch (err) {
    emit('notice', err.message)
  }
}

onMounted(load)
</script>
