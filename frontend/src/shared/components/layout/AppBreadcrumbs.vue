<script setup lang="ts">
withDefaults(
  defineProps<{
    items: Array<{ label: string; to?: string }>
    separator?: string
  }>(),
  { separator: '/' },
)
</script>

<template>
  <nav class="flex flex-wrap items-center gap-2 text-[12px] leading-[1.5] text-muted" aria-label="Migas de pan">
    <template v-for="(item, index) in items" :key="item.label">
      <RouterLink v-if="item.to" :to="item.to" class="transition-colors hover:text-brand-700">
        {{ item.label }}
      </RouterLink>
      <span v-else class="text-secondary">{{ item.label }}</span>
      <span v-if="index < items.length - 1" aria-hidden="true">{{ separator }}</span>
    </template>
  </nav>
</template>
