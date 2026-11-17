<script setup lang="ts">
import { formatFullDateTime, formatFullDateTimeSeconds } from '@/shared/utils/format'

interface TimelineEntry {
  id: string
  at: string
  title: string
  description?: string
  author?: string
  tone?: 'brand' | 'accent' | 'danger'
}

withDefaults(defineProps<{ entries: TimelineEntry[]; showSeconds?: boolean }>(), {
  showSeconds: false,
})

const dotClass: Record<string, string> = {
  brand: 'bg-brand-700',
  accent: 'bg-accent',
  danger: 'bg-danger',
}
</script>

<template>
  <ol class="relative ml-1 space-y-6">
    <span
      v-if="entries.length > 1"
      class="absolute bottom-2 left-[4px] top-2 w-0.5 bg-line"
      aria-hidden="true"
    />
    <li v-for="entry in entries" :key="entry.id" class="relative pl-6">
      <span
        class="absolute left-0 top-[5px] size-2.5 rounded-full ring-4 ring-white"
        :class="dotClass[entry.tone ?? 'brand']"
        aria-hidden="true"
      />
      <p class="text-[12px] leading-[1.5] text-muted">
        {{ showSeconds ? formatFullDateTimeSeconds(entry.at) : formatFullDateTime(entry.at) }}
      </p>
      <p class="mt-1 text-[14px] font-semibold leading-[1.5] text-ink">{{ entry.title }}</p>
      <p v-if="entry.description" class="mt-1 whitespace-pre-line text-[13px] leading-[1.5] text-secondary">
        {{ entry.description }}
      </p>
      <p v-if="entry.author" class="mt-2 text-[12px] leading-[1.5] text-muted">{{ entry.author }}</p>
    </li>
  </ol>
</template>
