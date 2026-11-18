<script setup lang="ts">
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppIcon from '@/shared/components/ui/AppIcon.vue'
import type { IconName } from '@/types/icons'

withDefaults(
  defineProps<{
    title: string
    description?: string
    actionLabel?: string
    icon?: IconName
    compact?: boolean
  }>(),
  { icon: 'inbox', compact: false },
)

const emit = defineEmits<{ action: [] }>()
</script>

<template>
  <div
    class="flex flex-col items-center justify-center px-6 text-center"
    :class="compact ? 'py-10' : 'py-16'"
  >
    <div
      v-if="icon"
      class="mb-4 grid size-12 place-items-center rounded-full bg-brand-100 text-brand-700"
    >
      <AppIcon :name="icon" :size="24" />
    </div>
    <h3 class="text-[20px] font-semibold leading-[1.5] text-ink">{{ title }}</h3>
    <p v-if="description" class="mt-2 max-w-[520px] text-[14px] leading-[1.5] text-muted">
      {{ description }}
    </p>
    <AppButton v-if="actionLabel" class="mt-5" @click="emit('action')">{{ actionLabel }}</AppButton>
  </div>
</template>
