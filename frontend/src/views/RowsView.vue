<template>
  <section class="card">
    <div class="card-body">
      <h1 class="card-title">{{ title }}</h1>
      <SortableTable :columns="columns" :rows="displayRows" />
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api'
import SortableTable from '../components/SortableTable.vue'

const props = defineProps({ title: String, url: String, columns: Array, numbered: Boolean })
const rows = ref([])
const displayRows = computed(() => props.numbered
  ? rows.value.map((row, index) => ({ ...row, display_no: index + 1 }))
  : rows.value
)

onMounted(async () => {
  rows.value = (await api(props.url)).rows
})
</script>
