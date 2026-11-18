<script setup lang="ts">
import AppIcon from '@/shared/components/ui/AppIcon.vue'
import { useUiStore } from '@/stores/ui.store'

defineProps<{ title: string }>()

const ui = useUiStore()
</script>

<template>
  <header
    class="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-line bg-white px-4 sm:px-6 lg:h-24 lg:px-8"
  >
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
  </header>
</template>
