<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{ variant?: 'sidebar' | 'auth' | 'card' }>(),
  { variant: 'sidebar' },
)

const sizes = {
  sidebar: '128px',
  auth: '112px',
  card: '96px',
}

// El SVG original es negro: en el sidebar (fondo morado) se invierte a blanco.
const tone = computed(() => (props.variant === 'sidebar' ? 'brightness-0 invert' : ''))
</script>

<template>
  <img
    src="/images/logo-plp.svg"
    alt="PLP · Pasa La Pasta"
    class="block select-none"
    :class="tone"
    :style="{ width: sizes[variant], height: sizes[variant] }"
    draggable="false"
  />
</template>
