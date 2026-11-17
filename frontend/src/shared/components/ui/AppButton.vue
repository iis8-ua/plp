<script setup lang="ts">
import { computed } from 'vue'

type Variant = 'primary' | 'secondary' | 'neutral' | 'ghost' | 'danger' | 'danger-outline'
type Size = 'sm' | 'md' | 'lg'

const props = withDefaults(
  defineProps<{
    variant?: Variant
    size?: Size
    type?: 'button' | 'submit' | 'reset'
    block?: boolean
    loading?: boolean
    disabled?: boolean
    to?: string
  }>(),
  {
    variant: 'primary',
    size: 'md',
    type: 'button',
    block: false,
    loading: false,
    disabled: false,
  },
)

const base =
  'inline-flex items-center justify-center gap-2 rounded-md font-semibold leading-none transition-colors disabled:cursor-not-allowed disabled:opacity-70'

const variants: Record<Variant, string> = {
  primary: 'bg-brand-700 text-white hover:bg-brand-800 active:bg-brand-900 disabled:bg-line-soft disabled:text-muted',
  secondary:
    'border border-brand-700 bg-white text-brand-700 hover:bg-brand-100 active:bg-brand-200 disabled:border-line disabled:text-muted',
  neutral:
    'border border-line bg-white text-ink hover:bg-app active:bg-line-soft disabled:border-line disabled:text-muted',
  ghost: 'bg-transparent text-brand-700 hover:bg-brand-100 active:bg-brand-200',
  danger: 'bg-danger text-white hover:bg-[#991b1b] active:bg-[#7f1d1d]',
  'danger-outline':
    'border border-danger bg-white text-danger hover:bg-danger-soft active:bg-danger-bg disabled:border-line disabled:text-muted',
}

const sizes: Record<Size, string> = {
  sm: 'h-10 px-3 text-[14px]',
  md: 'h-11 px-4 text-[14px]',
  lg: 'h-12 px-5 text-[14px]',
}

const classes = computed(() => [
  base,
  variants[props.variant],
  sizes[props.size],
  props.block ? 'w-full' : '',
])
</script>

<template>
  <RouterLink v-if="to" :to="to" :class="classes">
    <slot />
  </RouterLink>
  <button v-else :type="type" :class="classes" :disabled="disabled || loading">
    <span
      v-if="loading"
      class="size-4 animate-spin rounded-full border-2 border-current border-t-transparent"
      aria-hidden="true"
    />
    <slot />
  </button>
</template>
