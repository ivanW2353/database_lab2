<template>
  <section class="card">
    <div class="card-body">
      <h1 class="card-title">学生管理</h1>
      <form class="form-grid wide mb-3" @submit.prevent="search">
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
      <SortableTable :columns="columns" :rows="rows" id-key="student_id">
        <template #actions="{ row }">
          <button class="btn btn-sm btn-outline-primary" @click="showDetail(row.student_id)">详情</button>
        </template>
      </SortableTable>
      <PaginationControls :pagination="pagination" @change="changePage" />
      <div v-if="selectedStudent" class="modal-backdrop" @click.self="selectedStudent = null">
        <section class="detail-modal card">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start gap-3 mb-3">
              <div>
                <h2 class="card-title mb-1">{{ selectedStudent.name }}</h2>
                <div class="text-muted">{{ selectedStudent.student_id }}</div>
              </div>
              <button class="btn btn-outline-secondary btn-sm" @click="selectedStudent = null">关闭</button>
            </div>
            <div class="detail-grid mb-3">
              <div><b>性别</b><span>{{ selectedStudent.gender || '未登记' }}</span></div>
              <div><b>学院</b><span>{{ selectedStudent.college || '未登记' }}</span></div>
              <div><b>专业</b><span>{{ selectedStudent.major || '未登记' }}</span></div>
              <div><b>电话</b><span>{{ selectedStudent.phone || '未登记' }}</span></div>
              <div><b>邮箱</b><span>{{ selectedStudent.email || '未登记' }}</span></div>
              <div><b>类型</b><span>{{ studentTypeText(selectedStudent.student_type) }}</span></div>
              <div><b>状态</b><span>{{ statusText(selectedStudent.status) }}</span></div>
              <div><b>注册时间</b><span>{{ selectedStudent.created_at || '' }}</span></div>
            </div>
            <h3 class="detail-title">借阅记录</h3>
            <div class="table-responsive">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>借阅编码</th><th>书名</th><th>条码</th><th>借出时间</th>
                    <th>应还时间</th><th>归还时间</th><th>延期次数</th><th>状态</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="record in selectedStudent.borrow_records" :key="record.borrow_no">
                    <td>{{ record.borrow_code }}</td>
                    <td>{{ record.title }}</td>
                    <td>{{ record.barcode }}</td>
                    <td>{{ record.borrow_time || '' }}</td>
                    <td>{{ record.due_time || '' }}</td>
                    <td>{{ record.return_time || '' }}</td>
                    <td>{{ record.renew_count }}</td>
                    <td>{{ statusText(record.status) }}</td>
                  </tr>
                  <tr v-if="!selectedStudent.borrow_records.length"><td colspan="8" class="text-muted">暂无借阅记录</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </div>
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
const selectedStudent = ref(null)
const filters = reactive({ student_id: '', name: '' })
const form = reactive({ student_id: '' })
const pagination = reactive({ page: 1, page_size: 10, total: 0, total_pages: 1 })
const columns = [['student_id', '学号'], ['name', '姓名'], ['college', '学院'], ['major', '专业'], ['student_type', '类型'], ['status', '状态']]

function studentUrl() {
  const params = new URLSearchParams()
  if (filters.student_id.trim()) params.set('student_id', filters.student_id.trim())
  if (filters.name.trim()) params.set('name', filters.name.trim())
  params.set('page', pagination.page)
  params.set('page_size', pagination.page_size)
  const query = params.toString()
  return query ? `/api/admin/students?${query}` : '/api/admin/students'
}

async function load() {
  const data = await api(studentUrl())
  rows.value = data.rows
  Object.assign(pagination, data.pagination)
}
async function search() { pagination.page = 1; await load() }
async function changePage(page) { pagination.page = page; await load() }
async function resetFilters() {
  Object.assign(filters, { student_id: '', name: '' })
  pagination.page = 1
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
async function showDetail(studentId) {
  try {
    selectedStudent.value = (await api(`/api/admin/students/${encodeURIComponent(studentId)}`)).student
  } catch (err) {
    emit('notice', err.message)
  }
}
function statusText(status) {
  const labels = {
    normal: '正常',
    suspended: '暂停借阅',
    graduated: '毕业',
    borrowed: '借出',
    returned: '已归还',
    overdue: '已超期'
  }
  return labels[status] || status || ''
}
function studentTypeText(type) {
  const labels = { undergraduate: '本科生' }
  return labels[type] || type || '未登记'
}
onMounted(load)
</script>
