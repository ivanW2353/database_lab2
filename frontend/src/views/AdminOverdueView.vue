<template>
  <section class="card"><div class="card-body">
    <h1 class="card-title">违期管理</h1>
    <SortableTable :columns="columns" :rows="rows" id-key="overdue_no">
      <template #actions="{ row }">
        <button v-if="row.status !== 'paid'" class="btn btn-sm btn-primary" @click="pay(row.overdue_no)">登记缴清</button>
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
const columns = [['overdue_no', '编号'], ['student_id', '学号'], ['name', '姓名'], ['title', '书名'], ['overdue_days', '逾期天数'], ['fine_amount', '罚金'], ['paid_amount', '已缴'], ['status', '状态']]
async function load() { rows.value = (await api('/api/admin/overdue')).rows }
async function pay(overdue_no) { const data = await api('/api/admin/overdue', { method: 'POST', body: { overdue_no } }); emit('notice', data.message); await load() }
onMounted(load)
</script>
