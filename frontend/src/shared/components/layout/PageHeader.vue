<script setup lang="ts">
defineProps<{
  title: string
  description?: string
  timestamp?: string
}>()
</script>

<template>
  <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
    <div class="min-w-0">
      <h1 class="text-[24px] font-semibold leading-[1.5] text-ink">{{ title }}</h1>
      <p v-if="description" class="mt-0.5 text-[14px] leading-[1.5] text-muted">{{ description }}</p>
    </div>
    <div class="flex shrink-0 flex-col items-start gap-2 sm:items-end">
      <slot name="actions" />
      <p v-if="timestamp" class="text-[12px] leading-[1.5] text-muted">{{ timestamp }}</p>
    </div>
  </div>
</template>
