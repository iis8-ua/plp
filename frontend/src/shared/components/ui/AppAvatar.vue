<script setup lang="ts">
import { computed, ref } from 'vue'
import { initials } from '@/shared/utils/format'

const props = withDefaults(
  defineProps<{
    name: string
    src?: string
    size?: 32 | 36 | 40 | 48
    shape?: 'circle' | 'square'
    tone?: 'brand' | 'neutral'
  }>(),
  { size: 40, shape: 'circle', tone: 'brand' },
)

const failed = ref(false)
const showImage = computed(() => Boolean(props.src) && !failed.value)
const dimension = computed(() => `${props.size}px`)
</script>

<template>
  <span
    class="inline-grid shrink-0 place-items-center overflow-hidden font-semibold"
    :class="[
      shape === 'circle' ? 'rounded-full' : 'rounded-md',
      tone === 'brand' ? 'bg-brand-100 text-brand-700' : 'bg-line-soft text-muted',
    ]"
    :style="{ width: dimension, height: dimension, fontSize: `${Math.max(11, size * 0.3)}px` }"
  >
    <img
      v-if="showImage"
      :src="src"
      :alt="name"
      class="size-full object-cover"
      @error="failed = true"
    />
    <span v-else>{{ initials(name) }}</span>
  </span>
</template>
