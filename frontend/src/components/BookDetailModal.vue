<template>
  <div v-if="book" class="modal-backdrop" @click.self="$emit('close')">
    <section class="detail-modal card">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-start gap-3 mb-3">
          <div>
            <h2 class="card-title mb-1">{{ book.title }}</h2>
            <div class="text-muted">{{ book.isbn }} · {{ book.category_code }} {{ book.category_name }}</div>
          </div>
          <button class="btn btn-outline-secondary btn-sm" @click="$emit('close')">关闭</button>
        </div>

        <div class="detail-grid mb-3">
          <div><b>作者</b><span>{{ book.authors || '未登记' }}</span></div>
          <div><b>出版社</b><span>{{ book.publisher_name || '未登记' }}</span></div>
          <div><b>出版日期</b><span>{{ book.publish_date || '未登记' }}</span></div>
          <div><b>版次</b><span>{{ book.edition || '未登记' }}</span></div>
          <div><b>价格</b><span>{{ book.price || '未登记' }}</span></div>
          <div><b>语种</b><span>{{ book.language || '未登记' }}</span></div>
        </div>

        <section class="mb-3">
          <h3 class="detail-title">内容简介</h3>
          <p class="mb-0">{{ book.summary || '暂无简介' }}</p>
        </section>

        <section class="mb-3">
          <h3 class="detail-title">馆藏副本</h3>
          <table class="table table-sm">
            <thead><tr><th>条码</th><th>位置</th><th>状态</th><th>入库日期</th></tr></thead>
            <tbody>
              <tr v-for="copy in book.copies" :key="copy.copy_no">
                <td>{{ copy.barcode }}</td>
                <td>{{ copy.location }}</td>
                <td>{{ statusText(copy.status) }}</td>
                <td>{{ copy.purchase_date || '' }}</td>
              </tr>
              <tr v-if="!book.copies?.length"><td colspan="4" class="text-muted">暂无副本</td></tr>
            </tbody>
          </table>
        </section>

        <section>
          <h3 class="detail-title">图片 / 视频 / 文件</h3>
          <div v-if="book.media?.length" class="media-list">
            <div v-for="item in book.media" :key="item.media_no" class="media-item">
              <b>{{ mediaTypeText(item.media_type) }}</b>
              <span>{{ item.title }}</span>
              <code>{{ item.file_path }}</code>
            </div>
          </div>
          <p v-else class="text-muted mb-0">暂无附件资料</p>
        </section>

        <div v-if="showActions" class="detail-actions">
          <button class="btn btn-primary" @click="$emit('borrow', book.book_no)">{{ canBorrow ? '立即借出' : '加入队列' }}</button>
          <button class="btn btn-outline-primary" @click="$emit('reserve', book.book_no)">预约</button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  book: { type: Object, default: null },
  showActions: { type: Boolean, default: false }
})
defineEmits(['close', 'borrow', 'reserve'])

const canBorrow = computed(() => props.book?.copies?.some(copy => copy.status === 'available'))

function statusText(status) {
  const labels = { available: '可借', borrowed: '借出', maintenance: '维修', lost: '丢失', removed: '下架' }
  return labels[status] || status || ''
}

function mediaTypeText(type) {
  const labels = { image: '图片', video: '视频', file: '文件' }
  return labels[type] || type
}
</script>
