<template>
  <section class="card mb-3">
    <div class="card-body">
      <h1 class="card-title">个人信息</h1>
      <div v-if="canEditName" class="alert alert-warning">首次登录请补全个人信息：姓名必填，电话和邮箱至少填写一项。</div>
      <form class="form-grid wide" @submit.prevent="saveProfile">
        <label class="form-label">学号<input class="form-control" :value="student.student_id" disabled></label>
        <label class="form-label">学生类型<input class="form-control" value="本科生" disabled></label>
        <label class="form-label">状态<input class="form-control" :value="student.status" disabled></label>
        <label class="form-label">姓名<input v-if="canEditName" v-model="student.name" class="form-control" required @focus="clearPlaceholderName"><input v-else class="form-control" :value="student.name" disabled></label>
        <label class="form-label">性别<select v-model="student.gender" class="form-select"><option value="other">其他</option><option value="male">男</option><option value="female">女</option></select></label>
        <label class="form-label">电话<input v-model="student.phone" class="form-control" :required="!student.email" pattern="(1[3-9]\d{9}|0\d{2,3}-?\d{7,8})" title="请填写 11 位手机号或座机号"></label>
        <label class="form-label">邮箱<input v-model="student.email" type="email" class="form-control" :required="!student.phone" pattern="[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}" title="请填写有效邮箱地址"></label>
        <label class="form-label">学院<input v-model="student.college" class="form-control"></label>
        <label class="form-label">专业<input v-model="student.major" class="form-control"></label>
        <button class="btn btn-primary">保存个人信息</button>
      </form>
    </div>
  </section>
  <section class="card">
    <div class="card-body">
      <h2 class="card-title">修改密码</h2>
      <form class="form-grid" @submit.prevent="changePassword">
        <label class="form-label span-2">原密码<input v-model="password.old_password" type="password" class="form-control" required></label>
        <label class="form-label">新密码<input v-model="password.new_password" type="password" class="form-control" required minlength="6" pattern="[A-Za-z0-9]{6,}" title="密码至少 6 位，且只能包含数字或字母"></label>
        <label class="form-label">确认新密码<input v-model="password.confirm_password" type="password" class="form-control" required minlength="6" pattern="[A-Za-z0-9]{6,}" title="密码至少 6 位，且只能包含数字或字母"></label>
        <button class="btn btn-primary span-2">保存新密码</button>
      </form>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api'

const emit = defineEmits(['notice', 'profile-saved'])
const student = reactive({})
const password = reactive({ old_password: '', new_password: '', confirm_password: '' })
const canEditName = ref(false)

function clearPlaceholderName() {
  if (student.name === '待完善') student.name = ''
}

onMounted(async () => {
  Object.assign(student, (await api('/api/student/profile')).student)
  canEditName.value = student.name === '待完善'
})

async function saveProfile() {
  try {
    if (!String(student.phone || '').trim() && !String(student.email || '').trim()) {
      emit('notice', '电话和邮箱至少填写一项')
      return
    }
    const data = await api('/api/student/profile', { method: 'POST', body: student })
    emit('notice', data.message)
    emit('profile-saved', data.user)
  } catch (err) {
    emit('notice', err.message)
  }
}

async function changePassword() {
  try {
    const data = await api('/api/student/password', { method: 'POST', body: password })
    emit('notice', data.message)
    Object.assign(password, { old_password: '', new_password: '', confirm_password: '' })
  } catch (err) {
    emit('notice', err.message)
  }
}
</script>
