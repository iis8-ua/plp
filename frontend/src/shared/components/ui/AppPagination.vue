<script setup lang="ts">
import { computed } from 'vue'
import AppButton from '@/shared/components/ui/AppButton.vue'

const props = withDefaults(
  defineProps<{
    page: number
    totalPages: number
    rangeStart?: number
    rangeEnd?: number
    total: number
    label?: string
  }>(),
  { rangeStart: 0, rangeEnd: 0, label: 'resultados' },
)

const emit = defineEmits<{ 'update:page': [page: number] }>()

const pages = computed<Array<number | 'ellipsis'>>(() => {
  const total = props.totalPages
  if (total <= 5) return Array.from({ length: total }, (_, index) => index + 1)
  const current = props.page
  const result: Array<number | 'ellipsis'> = [1]
  if (current > 3) result.push('ellipsis')
  const start = Math.max(2, current - 1)
  const end = Math.min(total - 1, current + 1)
  for (let page = start; page <= end; page += 1) result.push(page)
  if (current < total - 2) result.push('ellipsis')
  result.push(total)
  return result
})

function go(page: number): void {
  if (page < 1 || page > props.totalPages || page === props.page) return
  emit('update:page', page)
}
</script>

<template>
  <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
    <p class="text-[12px] leading-[1.5] text-muted">
      Mostrando {{ rangeStart }}–{{ rangeEnd }} de {{ total }} {{ label }}
    </p>
    <div class="flex items-center gap-2">
      <AppButton
        variant="neutral"
        size="sm"
        class="min-w-[96px]"
        :disabled="page <= 1"
        @click="go(page - 1)"
      >
        Anterior
      </AppButton>
      <div class="hidden items-center gap-2 sm:flex">
        <template v-for="(item, index) in pages" :key="`${item}-${index}`">
          <span v-if="item === 'ellipsis'" class="px-1 text-muted">…</span>
          <button
            v-else
            type="button"
            class="grid size-10 place-items-center rounded-md border text-[14px] font-semibold transition-colors"
            :class="
              item === page
                ? 'border-brand-700 bg-brand-700 text-white'
                : 'border-line bg-white text-ink hover:bg-app'
            "
            :aria-current="item === page ? 'page' : undefined"
            @click="go(item)"
          >
            {{ item }}
          </button>
        </template>
      </div>
      <AppButton
        variant="neutral"
        size="sm"
        class="min-w-[96px]"
        :disabled="page >= totalPages"
        @click="go(page + 1)"
      >
        Siguiente
      </AppButton>
    </div>
  </div>
</template>
