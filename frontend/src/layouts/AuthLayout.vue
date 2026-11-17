<script setup lang="ts">
import BrandLogo from '@/shared/components/layout/BrandLogo.vue'

withDefaults(
  defineProps<{
    portalLabel: string
    footerMessage?: string
    centered?: boolean
  }>(),
  { footerMessage: '', centered: false },
)
</script>

<template>
  <div
    class="flex min-h-screen flex-col"
    style="
      background-image: linear-gradient(
        136.52deg,
        #f2edfa 0%,
        #f8fafc 39.29%,
        #e9e1f7 71.43%
      );
    "
  >
    <header class="flex items-start justify-between gap-4 px-4 pt-4 sm:px-10 sm:pt-5 lg:px-16">
      <BrandLogo variant="auth" />
      <p class="pt-8 text-[10px] font-semibold tracking-[0.02em] text-brand-700 sm:text-[11px]">
        {{ portalLabel }}
      </p>
    </header>

    <main
      class="flex flex-1 justify-center px-4 pb-8 sm:px-6"
      :class="centered ? 'items-center py-8' : 'items-start pt-8 sm:pt-[59px]'"
    >
      <div class="w-full max-w-[464px]">
        <slot />
      </div>
    </main>

    <footer
      class="flex flex-col gap-2 px-4 pb-5 text-[13px] leading-[1.5] text-muted sm:flex-row sm:items-center sm:justify-between sm:px-10 sm:pb-10 lg:px-16"
    >
      <p>PLP · Pasa La Pasta</p>
      <p v-if="footerMessage">{{ footerMessage }}</p>
    </footer>
  </div>
</template>
