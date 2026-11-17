<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import AppIcon from '@/shared/components/ui/AppIcon.vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    title?: string
    size?: 'sm' | 'md' | 'lg'
    closeOnOverlay?: boolean
    hideHeader?: boolean
  }>(),
  { size: 'sm', closeOnOverlay: true, hideHeader: false },
)

const emit = defineEmits<{ close: [] }>()

const panel = ref<HTMLElement | null>(null)
const widths = { sm: 'max-w-[480px]', md: 'max-w-[528px]', lg: 'max-w-[560px]' }

let previousOverflow = ''

function close(): void {
  emit('close')
}

function onKeydown(event: KeyboardEvent): void {
  if (!props.open) return
  if (event.key === 'Escape') {
    close()
    return
  }
  if (event.key !== 'Tab' || !panel.value) return
  const focusable = panel.value.querySelectorAll<HTMLElement>(
    'button:not([disabled]), [href], input:not([disabled]), textarea:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])',
  )
  if (focusable.length === 0) return
  const first = focusable[0]
  const last = focusable[focusable.length - 1]
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}

watch(
  () => props.open,
  async (open) => {
    if (open) {
      previousOverflow = document.body.style.overflow
      document.body.style.overflow = 'hidden'
      window.addEventListener('keydown', onKeydown)
      await nextTick()
      panel.value?.querySelector<HTMLElement>('button, input, textarea, select, [href]')?.focus()
    } else {
      document.body.style.overflow = previousOverflow
      window.removeEventListener('keydown', onKeydown)
    }
  },
)

onBeforeUnmount(() => {
  document.body.style.overflow = previousOverflow
  window.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="opacity-0"
      leave-active-class="transition duration-100 ease-in"
      leave-to-class="opacity-0"
    >
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-end justify-center bg-[rgba(15,23,42,0.45)] p-0 sm:items-center sm:p-4"
        role="presentation"
        @click.self="closeOnOverlay && close()"
      >
        <div
          ref="panel"
          role="dialog"
          aria-modal="true"
          :aria-label="title"
          class="relative max-h-[92vh] w-full overflow-y-auto rounded-t-xl border border-line bg-white p-6 sm:rounded-xl sm:p-8"
          :class="widths[size]"
        >
          <div v-if="!hideHeader" class="mb-5 flex items-start justify-between gap-4">
            <h2 class="text-[24px] font-semibold leading-[1.5] text-ink">{{ title }}</h2>
            <button
              type="button"
              class="-mr-2 grid size-10 shrink-0 place-items-center rounded-md text-muted transition-colors hover:bg-app hover:text-ink"
              aria-label="Cerrar"
              @click="close"
            >
              <AppIcon name="x" :size="20" />
            </button>
          </div>
          <slot />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
