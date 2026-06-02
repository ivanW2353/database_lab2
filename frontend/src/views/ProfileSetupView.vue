<template>
  <section class="setup-page">
    <div class="card setup-card">
      <div class="card-body">
        <h1 class="card-title mb-2">完善个人信息</h1>
        <p class="text-muted mb-4">首次使用系统前需要补全基础资料。姓名必填，电话和邮箱至少填写一项。</p>
        <form class="form-grid" @submit.prevent="saveProfile">
          <label class="form-label span-2">学号<input class="form-control" :value="student.student_id" disabled></label>
          <label class="form-label">姓名<input v-model="student.name" class="form-control" required autofocus @focus="clearPlaceholderName"></label>
          <label class="form-label">性别<select v-model="student.gender" class="form-select"><option value="other">其他</option><option value="male">男</option><option value="female">女</option></select></label>
          <label class="form-label">电话<input v-model="student.phone" class="form-control" :required="!student.email" pattern="(1[3-9]\d{9}|0\d{2,3}-?\d{7,8})" title="请填写 11 位手机号或座机号"></label>
          <label class="form-label">邮箱<input v-model="student.email" type="email" class="form-control" :required="!student.phone" pattern="[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}" title="请填写有效邮箱地址"></label>
          <label class="form-label">学院<input v-model="student.college" class="form-control"></label>
          <label class="form-label">专业<input v-model="student.major" class="form-control"></label>
          <button class="btn btn-primary span-2">保存并进入系统</button>
        </form>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive } from 'vue'
import { api } from '../api'

const emit = defineEmits(['notice', 'profile-saved'])
const student = reactive({})

function clearPlaceholderName() {
  if (student.name === '待完善') student.name = ''
}

onMounted(async () => {
  Object.assign(student, (await api('/api/student/profile')).student)
})

async function saveProfile() {
  try {
    if (!String(student.name || '').trim() || student.name === '待完善') {
      emit('notice', '请填写姓名')
      return
    }
    if (!String(student.phone || '').trim() && !String(student.email || '').trim()) {
      emit('notice', '电话和邮箱至少填写一项')
      return
    }
    const data = await api('/api/student/profile', { method: 'POST', body: student })
    emit('profile-saved', data.user, data.message)
  } catch (err) {
    emit('notice', err.message)
  }
}
</script>
