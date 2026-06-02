<template>
  <section class="card">
    <div class="card-body">
      <h1 class="card-title">管理员管理</h1>
      <form class="form-grid wide mb-3" @submit.prevent="load">
        <label class="form-label">搜索工号<input v-model="filters.employee_id" class="form-control" placeholder="输入工号关键字"></label>
        <label class="form-label">搜索姓名<input v-model="filters.name" class="form-control" placeholder="输入姓名关键字"></label>
        <button class="btn btn-outline-primary">搜索</button>
        <button type="button" class="btn btn-outline-secondary" @click="resetFilters">重置</button>
      </form>
      <form class="form-grid wide mb-3" @submit.prevent="addLibrarian">
        <label class="form-label">工号<input v-model="form.employee_id" class="form-control" required></label>
        <label class="form-label">姓名<input v-model="form.name" class="form-control" required></label>
        <label class="form-label">初始密码<input v-model="form.password" type="password" class="form-control" minlength="6" pattern="[A-Za-z0-9]{6,}" title="密码至少 6 位，且只能包含数字或字母"></label>
        <label class="form-label">职位<input v-model="form.position" class="form-control"></label>
        <label class="form-label">电话<input v-model="form.phone" class="form-control" pattern="(1[3-9]\d{9}|0\d{2,3}-?\d{7,8})" title="请填写 11 位手机号或座机号"></label>
        <label class="form-label">邮箱<input v-model="form.email" type="email" class="form-control" pattern="[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}" title="请填写有效邮箱地址"></label>
        <div class="text-muted align-self-end">初始密码为空时默认为 123456；自定义密码至少 6 位，且只能包含数字或字母。</div>
        <button class="btn btn-primary">新增管理员</button>
        <button type="button" class="btn btn-danger" @click="deleteLibrarian">删除管理员</button>
      </form>
      <SortableTable :columns="columns" :rows="rows" id-key="librarian_no" />
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api'
import SortableTable from '../components/SortableTable.vue'

const emit = defineEmits(['notice'])
const rows = ref([])
const filters = reactive({ employee_id: '', name: '' })
const form = reactive({ employee_id: '', name: '', password: '123456', position: '', phone: '', email: '' })
const columns = [
  ['librarian_no', '编号'],
  ['employee_id', '工号'],
  ['name', '姓名'],
  ['phone', '电话'],
  ['email', '邮箱'],
  ['position', '职位'],
  ['status', '状态'],
  ['created_at', '创建时间']
]

function librarianUrl() {
  const params = new URLSearchParams()
  if (filters.employee_id.trim()) params.set('employee_id', filters.employee_id.trim())
  if (filters.name.trim()) params.set('name', filters.name.trim())
  const query = params.toString()
  return query ? `/api/admin/librarians?${query}` : '/api/admin/librarians'
}

async function load() {
  rows.value = (await api(librarianUrl())).rows
}

async function resetFilters() {
  Object.assign(filters, { employee_id: '', name: '' })
  await load()
}

async function addLibrarian() {
  try {
    const data = await api('/api/admin/librarians', { method: 'POST', body: form })
    emit('notice', data.message)
    Object.assign(form, { employee_id: '', name: '', password: '123456', position: '', phone: '', email: '' })
    await load()
  } catch (err) {
    emit('notice', err.message)
  }
}

async function deleteLibrarian() {
  const employeeId = form.employee_id.trim()
  if (!employeeId) {
    emit('notice', '请先输入要删除的管理员工号')
    return
  }
  if (!window.confirm(`确认删除管理员 ${employeeId}？`)) return
  try {
    const data = await api('/api/admin/librarians', { method: 'DELETE', body: { employee_id: employeeId } })
    emit('notice', data.message)
    Object.assign(form, { employee_id: '', name: '', password: '123456', position: '', phone: '', email: '' })
    await load()
  } catch (err) {
    emit('notice', err.message)
  }
}

onMounted(load)
</script>
