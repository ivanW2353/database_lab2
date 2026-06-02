<template>
  <section class="login-page">
    <div class="login-header">
      <div class="login-logo">L</div>
      <h1>图书管理系统</h1>
      <p>{{ mode === 'login' ? '登录到系统' : '创建学生账号' }}</p>
    </div>

    <div class="login-panel">
      <form v-if="mode === 'login'" class="login-form" @submit.prevent="submit">
        <label class="form-label">身份</label>
        <div class="mb-3">
          <select v-model="form.role" class="form-select">
            <option value="student">学生</option>
            <option value="librarian">图书管理员</option>
          </select>
        </div>
        <label class="form-label">学号/工号</label>
        <input v-model="form.login" class="form-control mb-3" required autofocus>
        <label class="form-label">密码</label>
        <input v-model="form.password" type="password" class="form-control mb-3" required>
        <button class="btn btn-primary w-100">登录</button>
      </form>

      <form v-else class="login-form" @submit.prevent="registerStudent">
        <label class="form-label">学号</label>
        <input v-model="registerForm.student_id" class="form-control mb-3" required autofocus placeholder="如 pb22000001">
        <label class="form-label">密码</label>
        <input v-model="registerForm.password" type="password" class="form-control mb-3" required minlength="6" pattern="[A-Za-z0-9]{6,}" title="密码至少 6 位，且只能包含数字或字母">
        <label class="form-label">确认密码</label>
        <input v-model="registerForm.confirm_password" type="password" class="form-control mb-3" required minlength="6" pattern="[A-Za-z0-9]{6,}" title="密码至少 6 位，且只能包含数字或字母">
        <button class="btn btn-primary w-100">注册</button>
      </form>

      <p v-if="error" class="text-danger mt-3">{{ error }}</p>
      <p v-if="success" class="text-success mt-3">{{ success }}</p>
      <p class="text-muted mt-3 mb-0 text-center">演示学生：pb22000001 / 123456<br>管理员：admin / 123456</p>
    </div>

    <div class="login-switch">
      <template v-if="mode === 'login'">
        没有学生账号？
        <button class="btn btn-link p-0 align-baseline" @click="switchMode('register')">学生注册</button>
      </template>
      <template v-else>
        已有账号？
        <button class="btn btn-link p-0 align-baseline" @click="switchMode('login')">返回登录</button>
      </template>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { api } from '../api'

const emit = defineEmits(['logged-in'])
const error = ref('')
const success = ref('')
const mode = ref('login')
const form = reactive({ role: 'student', login: '', password: '' })
const registerForm = reactive({ student_id: '', password: '', confirm_password: '' })

function switchMode(nextMode) {
  mode.value = nextMode
  error.value = ''
  success.value = ''
}

async function submit() {
  try {
    error.value = ''
    success.value = ''
    const data = await api('/api/login', { method: 'POST', body: form })
    emit('logged-in', data.user)
  } catch (err) {
    error.value = err.message
  }
}

async function registerStudent() {
  try {
    error.value = ''
    success.value = ''
    const data = await api('/api/register/student', { method: 'POST', body: registerForm })
    Object.assign(registerForm, { student_id: '', password: '', confirm_password: '' })
    emit('logged-in', data.user)
  } catch (err) {
    error.value = err.message
  }
}
</script>
