<template>
  <section class="card"><div class="card-body">
    <h1 class="card-title">预约处理</h1>
    <SortableTable :columns="columns" :rows="rows" id-key="reservation_no">
      <template #actions="{ row }">
        <form class="d-flex gap-2" @submit.prevent="update(row)">
          <select v-model="row.nextStatus" class="form-select form-select-sm">
            <option value="notified">已通知</option>
            <option value="fulfilled">已完成</option>
            <option value="cancelled">已取消</option>
            <option value="expired">已过期</option>
          </select>
          <button class="btn btn-sm btn-primary">更新</button>
        </form>
      </template>
    </SortableTable>
  </div></section>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api'
import SortableTable from '../components/SortableTable.vue'
const emit = defineEmits(['notice'])
const rows = ref([])
const columns = [['reservation_no', '编号'], ['student_id', '学号'], ['name', '姓名'], ['title', '书名'], ['reserved_at', '预约时间'], ['borrow_date', '计划借出日期'], ['expire_at', '过期时间'], ['status', '状态']]
async function load() { rows.value = (await api('/api/admin/reservations')).rows.map(row => ({ ...row, nextStatus: row.status === 'waiting' ? 'notified' : row.status })) }
async function update(row) { const data = await api('/api/admin/reservations', { method: 'POST', body: { reservation_no: row.reservation_no, status: row.nextStatus } }); emit('notice', data.message); await load() }
onMounted(load)
</script>
