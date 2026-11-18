<script setup lang="ts">
import AppToastHost from '@/shared/components/ui/AppToastHost.vue'
</script>

<template>
  <RouterView v-slot="{ Component }">
    <Transition name="fade" mode="out-in">
      <component :is="Component" />
    </Transition>
  </RouterView>
  <AppToastHost />
</template>
