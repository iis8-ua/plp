<script setup lang="ts">
import { computed } from 'vue'
import AppIcon from '@/shared/components/ui/AppIcon.vue'
import type { IconName } from '@/types/icons'

const props = withDefaults(
  defineProps<{
    tone?: 'error' | 'success' | 'info'
    icon?: IconName
    compact?: boolean
  }>(),
  { tone: 'error', compact: false },
)

const styles = computed(() => {
  if (props.tone === 'success') return 'border-success-border bg-success-bg text-success-text'
  if (props.tone === 'info') return 'border-info-bg bg-info-bg text-info-text'
  return 'border-danger-border bg-danger-soft text-danger'
})

const icon = computed<IconName>(() => {
  if (props.icon) return props.icon
  return props.tone === 'success' ? 'check' : props.tone === 'info' ? 'info' : 'alert-circle'
})

defineEmits<{ dismiss: [] }>()
</script>

<template>
  <div
    class="flex items-start gap-3 rounded-lg border px-4 text-[14px] leading-[1.5]"
    :class="[styles, compact ? 'py-2.5' : 'py-3']"
    role="alert"
  >
    <AppIcon :name="icon" :size="20" class="mt-0.5 shrink-0" />
    <div class="min-w-0 flex-1"><slot /></div>
    <button
      v-if="$slots.dismiss"
      type="button"
      class="grid size-8 shrink-0 place-items-center rounded-md transition-colors hover:bg-white/50"
      aria-label="Cerrar aviso"
      @click="$emit('dismiss')"
    >
      <AppIcon name="x" :size="16" />
    </button>
  </div>
</template>
