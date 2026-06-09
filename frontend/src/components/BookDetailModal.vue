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
          <form v-if="editingSummary" @submit.prevent="saveSummary">
            <textarea v-model="summaryDraft" class="form-control mb-2" rows="5" placeholder="请输入图书简介"></textarea>
            <div class="d-flex gap-2">
              <button class="btn btn-primary btn-sm">保存简介</button>
              <button type="button" class="btn btn-outline-secondary btn-sm" @click="cancelSummaryEdit">取消</button>
            </div>
          </form>
          <div v-else>
            <p class="mb-2">{{ book.summary || '暂无简介' }}</p>
            <button v-if="editableSummary" class="btn btn-sm btn-outline-primary" @click="startSummaryEdit">修改简介</button>
          </div>
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

        <section v-if="book.borrow_records" class="mb-3">
          <h3 class="detail-title">借阅记录</h3>
          <div class="table-responsive">
            <table class="table table-sm">
              <thead>
                <tr>
                  <th>借阅编码</th><th>学号</th><th>姓名</th><th>条码</th>
                  <th>借出时间</th><th>应还时间</th><th>归还时间</th><th>延期次数</th><th>状态</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="record in book.borrow_records" :key="record.borrow_no">
                  <td>{{ record.borrow_code }}</td>
                  <td>{{ record.student_id }}</td>
                  <td>{{ record.name }}</td>
                  <td>{{ record.barcode }}</td>
                  <td>{{ record.borrow_time || '' }}</td>
                  <td>{{ record.due_time || '' }}</td>
                  <td>{{ record.return_time || '' }}</td>
                  <td>{{ record.renew_count }}</td>
                  <td>{{ statusText(record.status) }}</td>
                </tr>
                <tr v-if="!book.borrow_records.length"><td colspan="9" class="text-muted">暂无借阅记录</td></tr>
              </tbody>
            </table>
          </div>
        </section>

        <section>
          <h3 class="detail-title">图片</h3>
            <div v-if="book.media?.length" class="media-list">
            <div v-for="item in book.media" :key="item.media_no" class="media-item">
              <div class="d-flex align-items-center gap-2">
                <div>
                  <b>{{ mediaTypeText(item.media_type) }}</b>
                </div>
                <div v-if="item.media_type === 'image'">
                  <img :src="fileUrl(item.file_path)" class="media-thumb" :alt="item.title || ''" />
                </div>
                <div v-else>
                  <a :href="fileUrl(item.file_path)" target="_blank" rel="noopener noreferrer">打开</a>
                </div>
                <div class="ms-auto">
                  <button v-if="allowUpload" class="btn btn-sm btn-outline-danger" @click="deleteMedia(item)">删除</button>
                </div>
              </div>
            </div>
          </div>
          <p v-else class="text-muted mb-0">暂无附件资料</p>
        
          <div v-if="allowUpload" class="mt-3">
            <label class="form-label">上传资料<input ref="uploadFileRef" type="file" accept="image/*" class="form-control" @change="selectUploadFile"></label>
            <div class="d-flex gap-2 mt-2">
              <button class="btn btn-primary btn-sm" @click="doUpload" :disabled="uploading">{{ uploading ? '上传中...' : '上传' }}</button>
            </div>
          </div>
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
import { computed, ref, watch } from 'vue'

const props = defineProps({
  book: { type: Object, default: null },
  showActions: { type: Boolean, default: false },
  editableSummary: { type: Boolean, default: false },
  allowUpload: { type: Boolean, default: false }
})
const emit = defineEmits(['close', 'borrow', 'reserve', 'save-summary', 'uploaded', 'notice'])
import { api } from '../api'

const canBorrow = computed(() => props.book?.copies?.some(copy => copy.status === 'available'))
const editingSummary = ref(false)
const summaryDraft = ref('')
const uploadFileRef = ref(null)
const uploadFileObj = ref(null)
const uploading = ref(false)
const deleting = ref(false)

watch(() => props.book?.book_no, () => {
  editingSummary.value = false
  summaryDraft.value = props.book?.summary || ''
  uploadFileObj.value = null
})

function startSummaryEdit() {
  summaryDraft.value = props.book?.summary || ''
  editingSummary.value = true
}

function cancelSummaryEdit() {
  editingSummary.value = false
  summaryDraft.value = props.book?.summary || ''
}

function saveSummary() {
  emit('save-summary', summaryDraft.value)
  editingSummary.value = false
}

function selectUploadFile(event) {
  const f = event.target.files?.[0] || null
  if (f && f.type && !f.type.startsWith('image/')) {
    emit('notice', '仅允许上传图片')
    // clear the input
    if (uploadFileRef.value) uploadFileRef.value.value = ''
    uploadFileObj.value = null
    return
  }
  uploadFileObj.value = f
}

async function doUpload() {
  if (!uploadFileObj.value) {
    emit('notice', '请选择文件')
    return
  }
  if (!props.book || !props.book.book_no) {
    emit('notice', '图书未选择')
    return
  }
  uploading.value = true
  try {
    const form = new FormData()
    form.append('action', 'media')
    form.append('book_no', props.book.book_no)
    form.append('file', uploadFileObj.value)
    const data = await api('/api/admin/books', { method: 'POST', body: form })
    emit('uploaded', data.message)
    emit('notice', data.message)
    // if server returned created media, insert it immediately for instant display
    if (data.media) {
      if (!props.book.media) props.book.media = []
      // normalize keys: ensure media_no is present
      props.book.media.unshift(data.media)
    }
    uploadFileObj.value = null
    if (uploadFileRef.value) uploadFileRef.value.value = ''
  } catch (err) {
    emit('notice', err.message)
  } finally {
    uploading.value = false
  }
}

async function deleteMedia(item) {
  console.log('deleteMedia called', item)
  if (!item || !item.media_no) return
  if (!confirm(`确认删除“${item.title}”？此操作不可撤销。`)) {
    console.log('deleteMedia cancelled by user', item && item.media_no)
    return
  }
  deleting.value = true
  try {
    console.log('deleteMedia: sending request', { action: 'delete_media', media_no: item.media_no })
    const data = await api('/api/admin/books', { method: 'POST', body: { action: 'delete_media', media_no: item.media_no } })
    console.log('deleteMedia: response', data)
    emit('uploaded', data.message || 'deleted')
    emit('notice', data.message || '删除成功')
  } catch (err) {
    console.error('deleteMedia error', err)
    emit('notice', err.message)
  } finally {
    deleting.value = false
  }
}

function statusText(status) {
  const labels = {
    available: '可借',
    borrowed: '借出',
    returned: '已归还',
    overdue: '已超期',
    maintenance: '维修',
    lost: '丢失',
    removed: '下架'
  }
  return labels[status] || status || ''
}

function mediaTypeText(type) {
  const labels = { image: '图片', video: '视频', file: '文件' }
  return labels[type] || type
}

function fileUrl(path) {
  if (!path) return ''
  if (/^https?:\/\//i.test(path)) return path
  const p = String(path).replace(/^\/+/, '')
  try {
    const currentPort = window.location.port
    // If the page is served from a different dev server port, point to backend on port 8000
    const backendPort = '8000'
    const origin = (currentPort && currentPort !== backendPort) ? `${window.location.protocol}//${window.location.hostname}:${backendPort}` : window.location.origin
    return origin + '/' + encodeURI(p)
  } catch (e) {
    return '/' + p
  }
}
</script>
