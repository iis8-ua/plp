<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/shared/components/layout/AppHeader.vue'
import AppSidebar from '@/shared/components/layout/AppSidebar.vue'

const route = useRoute()
const title = computed(() => (route.meta.title as string | undefined) ?? 'Panel')
</script>

<template>
  <div class="flex min-h-screen bg-app">
    <AppSidebar variant="tecnico" />
    <div class="flex min-w-0 flex-1 flex-col">
      <AppHeader :title="title" variant="tecnico" />
      <main class="flex-1 p-4 sm:p-6 lg:p-8">
        <div class="mx-auto w-full max-w-[1152px]">
          <RouterView />
        </div>
      </main>
    </div>
  </div>
</template>
