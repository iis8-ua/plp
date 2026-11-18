<script setup lang="ts">
import { useUiStore } from '@/stores/ui.store'
import AppIcon from '@/shared/components/ui/AppIcon.vue'

const ui = useUiStore()
</script>

<template>
  <Teleport to="body">
    <div
      class="pointer-events-none fixed right-4 top-20 z-[70] flex w-[calc(100%-2rem)] max-w-[584px] flex-col gap-3 sm:right-6 lg:top-24"
      aria-live="polite"
      aria-atomic="false"
    >
      <TransitionGroup
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="translate-y-[-8px] opacity-0"
        leave-active-class="transition duration-150 ease-in"
        leave-to-class="translate-y-[-8px] opacity-0"
      >
        <div
          v-for="toast in ui.toasts"
          :key="toast.id"
          class="pointer-events-auto flex min-h-14 items-center gap-3 rounded-lg border px-4 py-3 text-[14px] font-medium leading-[1.5]"
          :class="
            toast.type === 'success'
              ? 'border-success-border bg-success-bg text-success-text'
              : 'border-danger-border bg-danger-soft text-danger'
          "
          role="status"
        >
          <span
            class="grid size-6 shrink-0 place-items-center rounded-full"
            :class="toast.type === 'success' ? 'bg-white/60' : 'bg-white/60'"
          >
            <AppIcon :name="toast.type === 'success' ? 'check' : 'alert-circle'" :size="16" :stroke-width="2" />
          </span>
          <span class="min-w-0 flex-1">{{ toast.message }}</span>
          <button
            type="button"
            class="grid size-8 shrink-0 place-items-center rounded-md transition-colors hover:bg-white/50"
            aria-label="Cerrar notificación"
            @click="ui.dismissToast(toast.id)"
          >
            <AppIcon name="x" :size="16" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>
