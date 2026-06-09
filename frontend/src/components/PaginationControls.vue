<template>
  <div class="d-flex justify-content-between align-items-center mt-3">
    <span class="text-muted">共 {{ pagination.total }} {{ unit }}，第 {{ pagination.page }} / {{ pagination.total_pages }} 页</span>
    <div class="d-flex gap-2">
      <button class="btn btn-sm btn-outline-primary" :disabled="pagination.page <= 1" @click="$emit('change', pagination.page - 1)">上一页</button>
      <button class="btn btn-sm btn-outline-primary" :disabled="pagination.page >= pagination.total_pages" @click="$emit('change', pagination.page + 1)">下一页</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  pagination: {
    type: Object,
    default: () => ({ page: 1, page_size: 10, total: 0, total_pages: 1 })
  },
  unit: { type: String, default: '条' }
})
defineEmits(['change'])
</script>
