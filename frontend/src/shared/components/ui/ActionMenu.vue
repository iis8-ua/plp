<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue'
import AppIcon from '@/shared/components/ui/AppIcon.vue'
import type { IconName } from '@/types/icons'

export interface ActionItem {
  key: string
  label: string
  tone?: 'default' | 'danger' | 'primary'
  icon?: IconName
  disabled?: boolean
}

const props = withDefaults(
  defineProps<{
    items: ActionItem[]
    ariaLabel: string
    header?: string
    bordered?: boolean
    width?: number
    align?: 'left' | 'right'
  }>(),
  { bordered: false, width: 208, align: 'right', header: '' },
)

const emit = defineEmits<{ select: [key: string] }>()

const open = ref(false)
const trigger = ref<HTMLElement | null>(null)
const position = ref({ top: 0, left: 0 })

function updatePosition(): void {
  const rect = trigger.value?.getBoundingClientRect()
  if (!rect) return
  const menuWidth = props.width
  const left = props.align === 'right' ? Math.max(8, rect.right - menuWidth) : Math.min(window.innerWidth - menuWidth - 8, rect.left)
  const estimatedHeight = 16 + (props.header ? 32 : 0) + props.items.length * 48
  const top = rect.bottom + estimatedHeight > window.innerHeight ? rect.top - estimatedHeight - 4 : rect.bottom + 4
  position.value = { top: Math.max(8, top), left }
}

function toggle(): void {
  open.value = !open.value
  if (open.value) {
    updatePosition()
    window.addEventListener('scroll', close, true)
    window.addEventListener('resize', close)
  } else {
    cleanup()
  }
}

function close(): void {
  open.value = false
  cleanup()
}

function cleanup(): void {
  window.removeEventListener('scroll', close, true)
  window.removeEventListener('resize', close)
}

function choose(item: ActionItem): void {
  if (item.disabled) return
  emit('select', item.key)
  close()
}

onBeforeUnmount(cleanup)
</script>

<template>
  <div>
    <button
      ref="trigger"
      type="button"
      class="grid size-10 place-items-center rounded-md text-ink transition-colors hover:bg-app"
      :aria-label="ariaLabel"
      :aria-expanded="open"
      aria-haspopup="menu"
      @click.stop="toggle"
    >
      <AppIcon name="dots" :size="20" />
    </button>

    <Teleport to="body">
      <div v-if="open" class="fixed inset-0 z-40" @click="close" />
      <div
        v-if="open"
        class="fixed z-50 rounded-lg border border-line bg-white p-2"
        :style="{ top: `${position.top}px`, left: `${position.left}px`, width: `${width}px` }"
        role="menu"
      >
        <p v-if="header" class="truncate px-3 pb-2 pt-1 text-[12px] font-medium text-muted">
          {{ header }}
        </p>
        <button
          v-for="item in items"
          :key="item.key"
          type="button"
          role="menuitem"
          class="flex h-11 w-full items-center gap-2 rounded-md px-3 text-left text-[14px] font-semibold transition-colors"
          :class="[
            bordered ? 'border' : '',
            item.tone === 'danger'
              ? 'border-danger text-danger hover:bg-danger-soft'
              : item.tone === 'primary'
                ? 'border-brand-700 text-brand-700 hover:bg-brand-100'
                : 'border-line text-ink hover:bg-app',
            item.disabled ? 'cursor-not-allowed opacity-50' : '',
            items.length > 1 && bordered ? 'mb-1 last:mb-0' : '',
          ]"
          :disabled="item.disabled"
          @click="choose(item)"
        >
          <AppIcon v-if="item.icon" :name="item.icon" :size="18" />
          {{ item.label }}
        </button>
      </div>
    </Teleport>
  </div>
</template>
