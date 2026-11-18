<script setup lang="ts">
import AppButton from '@/shared/components/ui/AppButton.vue'

withDefaults(
  defineProps<{
    code?: string
    title: string
    description?: string
    actionLabel?: string
  }>(),
  { code: '404' },
)

const emit = defineEmits<{ action: [] }>()
</script>

<template>
  <div class="flex min-h-[520px] flex-col items-center justify-center px-6 py-16 text-center">
    <p class="text-[72px] font-semibold leading-none tracking-[-0.04em] text-brand-700">{{ code }}</p>
    <h2 class="mt-4 text-[28px] font-semibold leading-[1.5] text-ink">{{ title }}</h2>
    <p v-if="description" class="mt-2 max-w-[440px] text-[14px] leading-[1.5] text-muted">
      {{ description }}
    </p>
    <AppButton v-if="actionLabel" class="mt-6 min-w-[232px]" @click="emit('action')">
      {{ actionLabel }}
    </AppButton>
  </div>
</template>
