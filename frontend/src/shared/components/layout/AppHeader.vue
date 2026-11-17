<script setup lang="ts">
import { computed } from 'vue'
import AppAvatar from '@/shared/components/ui/AppAvatar.vue'
import AppIcon from '@/shared/components/ui/AppIcon.vue'
import { useAuthStore } from '@/stores/auth.store'
import { useUiStore } from '@/stores/ui.store'

const props = defineProps<{
  title: string
  variant: 'tecnico' | 'comercio'
}>()

const auth = useAuthStore()
const ui = useUiStore()

const subtitle = computed(() =>
  props.variant === 'comercio' ? 'Comercio' : auth.user?.subtitle ?? '',
)
const avatarSrc = computed(() => (props.variant === 'tecnico' ? '/images/avatar-laura.jpg' : undefined))
</script>

<template>
  <header
    class="sticky top-0 z-30 flex h-16 items-center justify-between gap-4 border-b border-line bg-white px-4 sm:px-6 lg:h-24 lg:px-8"
  >
    <div class="flex min-w-0 items-center gap-3">
      <button
        type="button"
        class="grid size-10 shrink-0 place-items-center rounded-md text-ink transition-colors hover:bg-app lg:hidden"
        aria-label="Abrir navegación"
        @click="ui.openSidebar()"
      >
        <AppIcon name="menu" :size="22" />
      </button>
      <h1 class="truncate text-[20px] font-semibold leading-[1.5] text-ink lg:text-[24px]">
        {{ title }}
      </h1>
    </div>

    <div class="flex shrink-0 items-center gap-3">
      <div class="hidden text-right sm:block">
        <p class="text-[14px] font-semibold leading-[1.5] text-ink">{{ auth.user?.name }}</p>
        <p class="text-[12px] leading-[1.5] text-muted">{{ subtitle }}</p>
      </div>
      <AppAvatar
        :name="auth.user?.name ?? 'Usuario'"
        :src="avatarSrc"
        :size="40"
        shape="circle"
      />
    </div>
  </header>
</template>
