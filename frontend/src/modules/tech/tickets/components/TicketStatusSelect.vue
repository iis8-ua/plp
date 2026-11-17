<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import AppIcon from '@/shared/components/ui/AppIcon.vue'
import StatusBadge from '@/shared/components/ui/StatusBadge.vue'
import { TICKET_STATUS_LABELS, TICKET_STATUS_OPTIONS } from '@/shared/utils/status'
import type { TicketStatus } from '@/types'

const props = defineProps<{ modelValue: TicketStatus }>()
const emit = defineEmits<{ 'update:modelValue': [value: TicketStatus] }>()

const open = ref(false)
const root = ref<HTMLElement | null>(null)

function toggle(): void {
  open.value = !open.value
}

function choose(status: TicketStatus): void {
  emit('update:modelValue', status)
  open.value = false
}

function handleClickOutside(event: MouseEvent): void {
  if (!root.value?.contains(event.target as Node)) open.value = false
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside))
</script>

<template>
  <div ref="root" class="relative">
    <button
      type="button"
      class="flex h-11 w-full items-center justify-between gap-3 rounded-md border border-line bg-white px-3 text-left transition-colors hover:border-brand-300"
      :aria-expanded="open"
      aria-haspopup="listbox"
      aria-label="Estado del ticket"
      @click.stop="toggle"
    >
      <StatusBadge kind="ticket" :status="props.modelValue" />
      <AppIcon :name="open ? 'chevron-up' : 'chevron-down'" :size="20" class="text-muted" />
    </button>

    <ul
      v-if="open"
      role="listbox"
      class="absolute left-0 top-[calc(100%+6px)] z-30 w-full rounded-lg border border-line bg-white p-2"
    >
      <li v-for="option in TICKET_STATUS_OPTIONS" :key="option.value">
        <button
          type="button"
          role="option"
          :aria-selected="option.value === props.modelValue"
          class="flex h-11 w-full items-center justify-between gap-3 rounded-md px-3 text-left transition-colors hover:bg-app"
          @click="choose(option.value)"
        >
          <StatusBadge kind="ticket" :status="option.value" />
          <AppIcon
            v-if="option.value === props.modelValue"
            name="check"
            :size="18"
            class="text-brand-700"
          />
          <span v-else class="sr-only">{{ TICKET_STATUS_LABELS[option.value] }}</span>
        </button>
      </li>
    </ul>
  </div>
</template>
