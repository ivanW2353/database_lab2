<template>
  <div class="table-responsive card">
    <table class="table table-vcenter card-table">
      <thead>
        <tr>
          <th v-for="[key, label] in columns" :key="key" class="sortable" :class="sort.key === key ? sort.dir : ''" @click="toggle(key)">
            {{ label }}
          </th>
          <th v-if="$slots.actions">操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in sortedRows" :key="row[idKey] || JSON.stringify(row)">
          <td v-for="[key] in columns" :key="key">
            <span v-if="key === 'status'" class="badge" :class="badgeClass(row[key])">{{ statusText(row[key]) }}</span>
            <span v-else>{{ row[key] || '' }}</span>
          </td>
          <td v-if="$slots.actions"><slot name="actions" :row="row" /></td>
        </tr>
        <tr v-if="!sortedRows.length"><td :colspan="columns.length + ($slots.actions ? 1 : 0)" class="text-muted">暂无数据</td></tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, default: () => [] },
  idKey: { type: String, default: 'id' }
})

const sort = ref({ key: props.columns[0]?.[0] || '', dir: 'asc' })

function typed(value) {
  if (value === null || value === undefined || value === '') return { type: 'empty', value: '' }
  const text = String(value)
  const num = Number(text.replace(/,/g, ''))
  if (!Number.isNaN(num) && /^-?\d+(\.\d+)?$/.test(text.replace(/,/g, ''))) return { type: 'number', value: num }
  const date = Date.parse(text.replace(' ', 'T'))
  if (!Number.isNaN(date) && /\d{4}-\d{1,2}-\d{1,2}/.test(text)) return { type: 'date', value: date }
  return { type: 'text', value: text.toLocaleLowerCase('zh-CN') }
}

function toggle(key) {
  sort.value = sort.value.key === key
    ? { key, dir: sort.value.dir === 'asc' ? 'desc' : 'asc' }
    : { key, dir: 'asc' }
}

const sortedRows = computed(() => {
  const dir = sort.value.dir === 'asc' ? 1 : -1
  return [...props.rows].sort((a, b) => {
    const left = typed(a[sort.value.key])
    const right = typed(b[sort.value.key])
    if (left.type === 'empty' && right.type !== 'empty') return 1
    if (right.type === 'empty' && left.type !== 'empty') return -1
    if (left.value < right.value) return -1 * dir
    if (left.value > right.value) return 1 * dir
    return 0
  })
})

function badgeClass(status) {
  if (['normal', 'available', 'returned', 'fulfilled', 'paid'].includes(status)) return 'bg-green-lt'
  if (['waiting', 'notified', 'borrowed', 'overdue', 'partial_paid', 'unpaid'].includes(status)) return 'bg-yellow-lt'
  if (['suspended', 'cancelled', 'expired', 'lost', 'disabled'].includes(status)) return 'bg-red-lt'
  return 'bg-secondary-lt'
}

function statusText(status) {
  const labels = {
    waiting: '待处理',
    notified: '已通知',
    fulfilled: '已完成',
    cancelled: '已取消',
    expired: '已过期',
    normal: '正常',
    suspended: '暂停借阅',
    graduated: '毕业',
    available: '可借',
    borrowed: '借出',
    returned: '已归还',
    overdue: '已超期',
    paid: '已缴清',
    partial_paid: '部分缴清',
    unpaid: '未缴清',
    lost: '遗失',
    disabled: '停用'
  }
  return labels[status] || status || ''
}
</script>
