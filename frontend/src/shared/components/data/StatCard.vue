<script setup lang="ts">
import { computed } from 'vue'

type Tone = 'brand' | 'warning' | 'info' | 'success' | 'neutral' | 'danger'

const props = withDefaults(
  defineProps<{
    label: string
    value: string | number
    context?: string
    tone?: Tone
    compact?: boolean
  }>(),
  { tone: 'brand', compact: false },
)

const toneClass: Record<Tone, string> = {
  brand: 'text-brand-700',
  warning: 'text-warning-text',
  info: 'text-info-text',
  success: 'text-success-text',
  neutral: 'text-neutral-text',
  danger: 'text-danger',
}

const dotClass: Record<Tone, string> = {
  brand: 'bg-brand-700',
  warning: 'bg-warning-text',
  info: 'bg-info-text',
  success: 'bg-success-text',
  neutral: 'bg-neutral-text',
  danger: 'bg-danger',
}

const height = computed(() => (props.compact ? 'min-h-[104px]' : 'min-h-[140px]'))
</script>

<template>
  <div class="relative rounded-lg border border-line bg-white p-5" :class="height">
    <div class="flex items-start justify-between gap-3">
      <p class="text-[14px] font-medium leading-[1.5] text-muted">{{ label }}</p>
      <span class="mt-[7px] size-2 shrink-0 rounded-full" :class="dotClass[tone]" aria-hidden="true" />
    </div>
    <p class="mt-1 text-[36px] font-semibold leading-[1.5] tracking-[-0.01em]" :class="toneClass[tone]">
      {{ value }}
    </p>
    <p v-if="context" class="mt-1 text-[12px] leading-[1.5] text-muted">{{ context }}</p>
  </div>
</template>
