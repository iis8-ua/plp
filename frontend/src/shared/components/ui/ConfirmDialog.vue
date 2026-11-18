<script setup lang="ts">
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppIcon from '@/shared/components/ui/AppIcon.vue'
import AppModal from '@/shared/components/ui/AppModal.vue'
import type { IconName } from '@/types/icons'

withDefaults(
  defineProps<{
    open: boolean
    title: string
    description?: string
    confirmLabel?: string
    cancelLabel?: string
    tone?: 'danger' | 'primary'
    icon?: IconName
    loading?: boolean
    size?: 'sm' | 'md' | 'lg'
  }>(),
  {
    confirmLabel: 'Confirmar',
    cancelLabel: 'Cancelar',
    tone: 'danger',
    icon: 'alert-triangle',
    loading: false,
    size: 'sm',
  },
)

const emit = defineEmits<{ confirm: []; cancel: [] }>()
</script>

<template>
  <AppModal
    :open="open"
    :size="size"
    hide-header
    :close-on-overlay="!loading"
    @close="emit('cancel')"
  >
    <div class="pt-2">
      <div
        class="grid size-12 place-items-center rounded-full"
        :class="tone === 'danger' ? 'bg-danger-soft text-danger' : 'bg-brand-100 text-brand-700'"
      >
        <AppIcon :name="icon" :size="24" :stroke-width="2" />
      </div>
      <h2 class="mt-4 text-[24px] font-semibold leading-[1.5] text-ink">{{ title }}</h2>
      <p v-if="description" class="mt-1 text-[14px] leading-[1.5] text-muted">{{ description }}</p>

      <slot />

      <div class="mt-6 grid grid-cols-2 gap-3">
        <AppButton variant="secondary" :disabled="loading" @click="emit('cancel')">
          {{ cancelLabel }}
        </AppButton>
        <AppButton
          :variant="tone === 'danger' ? 'danger' : 'primary'"
          :loading="loading"
          @click="emit('confirm')"
        >
          {{ confirmLabel }}
        </AppButton>
      </div>
    </div>
  </AppModal>
</template>
