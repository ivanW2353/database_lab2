<template>
  <section class="card"><div class="card-body">
    <h1 class="card-title">办理还书</h1>
    <form class="form-grid mb-3" @submit.prevent="submit">
      <label class="form-label">借阅编号<input v-model="borrow_no" class="form-control" required></label>
      <button class="btn btn-primary">确认归还</button>
    </form>
    <SortableTable :columns="columns" :rows="rows" id-key="borrow_no" />
  </div></section>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api'
import SortableTable from '../components/SortableTable.vue'
const emit = defineEmits(['notice'])
const rows = ref([])
const borrow_no = ref('')
const columns = [['borrow_no', '借阅编号'], ['student_id', '学号'], ['name', '姓名'], ['title', '书名'], ['barcode', '条码'], ['borrow_time', '借出时间'], ['due_time', '应还时间'], ['status', '状态']]
async function load() { rows.value = (await api('/api/admin/return')).rows }
async function submit() { const data = await api('/api/admin/return', { method: 'POST', body: { borrow_no: borrow_no.value } }); emit('notice', data.message); borrow_no.value = ''; await load() }
onMounted(load)
</script>
