<template>
  <section class="card">
    <div class="card-body">
      <h1 class="card-title">学生管理</h1>
      <form class="form-grid wide mb-3" @submit.prevent="load">
        <label class="form-label">搜索学号<input v-model="filters.student_id" class="form-control" placeholder="输入学号关键字"></label>
        <label class="form-label">搜索姓名<input v-model="filters.name" class="form-control" placeholder="输入姓名关键字"></label>
        <button class="btn btn-outline-primary">搜索</button>
        <button type="button" class="btn btn-outline-secondary" @click="resetFilters">重置</button>
      </form>
      <form class="form-grid wide mb-3" @submit.prevent="addStudent">
        <label class="form-label">学号<input v-model="form.student_id" class="form-control" required></label>
        <div class="text-muted align-self-end">新增后初始密码为 123456，其余信息由学生登录后填写。</div>
        <button class="btn btn-primary">新增学生</button>
        <button type="button" class="btn btn-danger" @click="deleteStudent">删除学生</button>
      </form>
      <SortableTable :columns="columns" :rows="rows" id-key="student_no" />
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api'
import SortableTable from '../components/SortableTable.vue'

const emit = defineEmits(['notice'])
const rows = ref([])
const filters = reactive({ student_id: '', name: '' })
const form = reactive({ student_id: '' })
const columns = [['student_no', '编号'], ['student_id', '学号'], ['name', '姓名'], ['college', '学院'], ['major', '专业'], ['student_type', '类型'], ['status', '状态']]

function studentUrl() {
  const params = new URLSearchParams()
  if (filters.student_id.trim()) params.set('student_id', filters.student_id.trim())
  if (filters.name.trim()) params.set('name', filters.name.trim())
  const query = params.toString()
  return query ? `/api/admin/students?${query}` : '/api/admin/students'
}

async function load() { rows.value = (await api(studentUrl())).rows }
async function resetFilters() {
  Object.assign(filters, { student_id: '', name: '' })
  await load()
}
async function addStudent() {
  const data = await api('/api/admin/students', { method: 'POST', body: form })
  emit('notice', data.message)
  Object.assign(form, { student_id: '' })
  await load()
}
async function deleteStudent() {
  const studentId = form.student_id.trim()
  if (!studentId) {
    emit('notice', '请先输入要删除的学生学号')
    return
  }
  if (!window.confirm(`确认删除学生 ${studentId}？`)) return
  try {
    const data = await api('/api/admin/students', { method: 'DELETE', body: { student_id: studentId } })
    emit('notice', data.message)
    Object.assign(form, { student_id: '' })
    await load()
  } catch (err) {
    emit('notice', err.message)
  }
}
onMounted(load)
</script>
