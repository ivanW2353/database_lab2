<template>
  <div class="page page-shell">
    <header v-if="user" class="navbar navbar-expand-md d-print-none">
      <div class="container-xl">
        <a class="navbar-brand d-flex align-items-center gap-2" href="#" @click.prevent="go(homePath)">
          <span class="brand-mark">L</span><span>图书管理系统</span>
        </a>
        <div class="navbar-nav flex-row order-md-last">
          <div v-if="route !== '/student/setup'" class="badge bg-blue-lt">{{ user.name }}</div>
          <button class="btn btn-outline-danger ms-2" @click="logout">退出</button>
        </div>
        <nav class="navbar-nav flex-wrap">
          <button v-for="item in navItems" :key="item.path" class="nav-link btn btn-link" @click="go(item.path)">{{ item.label }}</button>
        </nav>
      </div>
    </header>

    <main class="page-wrapper">
      <div class="page-body">
        <div class="container-xl">
          <div v-if="notice" class="alert alert-info">{{ notice }}</div>
          <LoginView v-if="!user" @logged-in="onLoggedIn" />
          <ProfileSetupView v-else-if="route === '/student/setup'" @notice="setNotice" @profile-saved="onProfileSetupSaved" />
          <DashboardView v-else-if="route === homePath" :role="user.role" @notice="setNotice" @book-search="onBookSearch" />
          <BooksView v-else-if="routePath === '/student/books'" :route="route" @notice="setNotice" />
          <StudentBorrowsView v-else-if="route === '/student/borrows'" @notice="setNotice" />
          <StudentReservationsView v-else-if="route === '/student/reservations'" @notice="setNotice" />
          <RowsView v-else-if="route === '/student/overdue'" title="违期记录" url="/api/student/overdue" :columns="studentOverdueColumns" />
          <ProfileView v-else-if="route === '/student/profile'" @notice="setNotice" @profile-saved="onProfileSaved" />
          <AdminBooksView v-else-if="route === '/admin/books'" @notice="setNotice" />
          <AdminStudentsView v-else-if="route === '/admin/students'" @notice="setNotice" />
          <AdminLibrariansView v-else-if="route === '/admin/librarians'" @notice="setNotice" />
          <AdminBorrowView v-else-if="route === '/admin/borrow'" @notice="setNotice" />
          <AdminReturnView v-else-if="route === '/admin/return'" @notice="setNotice" />
          <AdminReservationsView v-else-if="route === '/admin/reservations'" @notice="setNotice" />
          <AdminOverdueView v-else-if="route === '/admin/overdue'" @notice="setNotice" />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import LoginView from './views/LoginView.vue'
import ProfileSetupView from './views/ProfileSetupView.vue'
import DashboardView from './views/DashboardView.vue'
import BooksView from './views/BooksView.vue'
import RowsView from './views/RowsView.vue'
import StudentBorrowsView from './views/StudentBorrowsView.vue'
import StudentReservationsView from './views/StudentReservationsView.vue'
import ProfileView from './views/ProfileView.vue'
import AdminBooksView from './views/AdminBooksView.vue'
import AdminStudentsView from './views/AdminStudentsView.vue'
import AdminLibrariansView from './views/AdminLibrariansView.vue'
import AdminBorrowView from './views/AdminBorrowView.vue'
import AdminReturnView from './views/AdminReturnView.vue'
import AdminReservationsView from './views/AdminReservationsView.vue'
import AdminOverdueView from './views/AdminOverdueView.vue'
import { api } from './api'

const user = ref(null)
const notice = ref('')
const route = ref(location.hash.slice(1) || '/student')

const homePath = computed(() => user.value?.role === 'librarian' ? '/admin' : '/student')
const routePath = computed(() => route.value.split('?')[0])
const navItems = computed(() => user.value?.role === 'librarian'
  ? [
      { path: '/admin', label: '首页' },
      { path: '/admin/books', label: '图书管理' },
      { path: '/admin/students', label: '学生管理' },
      { path: '/admin/librarians', label: '管理员管理' },
      { path: '/admin/borrow', label: '借书' },
      { path: '/admin/return', label: '还书' },
      { path: '/admin/reservations', label: '预约' },
      { path: '/admin/overdue', label: '违期' }
    ]
  : [
      { path: '/student', label: '首页' },
      { path: '/student/books', label: '图书检索' },
      { path: '/student/borrows', label: '我的借阅' },
      { path: '/student/reservations', label: '我的预约' },
      { path: '/student/overdue', label: '违期记录' },
      { path: '/student/profile', label: '个人信息' }
    ])

const studentOverdueColumns = [['overdue_code', '违期编码'], ['title', '书名'], ['overdue_start_date', '违期开始日期'], ['overdue_days', '逾期天数'], ['fine_amount', '罚金'], ['paid_amount', '已缴'], ['status', '状态']]

function go(path) {
  if (user.value?.role === 'student' && needsProfileCompletion(user.value) && path !== '/student/setup') {
    path = '/student/setup'
    notice.value = '首次登录请先补全个人信息：姓名必填，电话和邮箱至少填写一项。'
  } else {
    notice.value = ''
  }
  route.value = path
  location.hash = path
}

function setNotice(message) {
  notice.value = message
}

function onBookSearch(keyword) {
  go('/student/books?q=' + encodeURIComponent(keyword || ''))
}

function onLoggedIn(nextUser) {
  user.value = nextUser
  go(nextUser.role === 'librarian' ? '/admin' : '/student')
}

function onProfileSaved(nextUser) {
  if (nextUser) user.value = nextUser
}

function onProfileSetupSaved(nextUser, message) {
  if (nextUser) user.value = nextUser
  go('/student')
  if (message) notice.value = message
}

function needsProfileCompletion(nextUser) {
  return nextUser?.name === '待完善'
}

async function logout() {
  await api('/api/logout', { method: 'POST' })
  user.value = null
  notice.value = ''
}

onMounted(async () => {
  window.addEventListener('hashchange', () => {
    const nextRoute = location.hash.slice(1) || homePath.value
    if (user.value?.role === 'student' && needsProfileCompletion(user.value) && nextRoute !== '/student/setup') {
      go('/student/setup')
      return
    }
    route.value = nextRoute
  })
  const data = await api('/api/me')
  user.value = data.user
  if (user.value && !location.hash) go(homePath.value)
})
</script>
