<script setup lang="ts">
import BrandLogo from '@/shared/components/layout/BrandLogo.vue'

withDefaults(defineProps<{ title?: string; compact?: boolean }>(), { compact: false })
</script>

<template>
  <section
    class="rounded-xl border border-line bg-white px-6 pb-6 pt-6 sm:px-10 sm:pb-10"
    :class="compact ? 'sm:min-h-[378px]' : 'sm:min-h-[624px]'"
  >
    <div class="flex justify-center sm:justify-start">
      <BrandLogo variant="card" />
    </div>
    <div class="mt-4">
      <slot />
    </div>
  </section>
</template>
