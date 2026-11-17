<script setup lang="ts">
defineProps<{
  accepted: number
  rejected: number
  total: number
}>()
</script>

<template>
  <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
    <div class="flex min-h-[104px] flex-col justify-between rounded-lg border border-line bg-white p-5">
      <p class="text-[14px] font-medium leading-[1.5] text-muted">Pagos aceptados</p>
      <div class="mt-1 flex items-end justify-between gap-3">
        <p class="text-[36px] font-semibold leading-[1.2] text-success-text">{{ accepted }}</p>
        <p class="pb-1 text-[12px] leading-[1.5] text-muted">Registrados</p>
      </div>
    </div>
    <div class="flex min-h-[104px] flex-col justify-between rounded-lg border border-line bg-white p-5">
      <p class="text-[14px] font-medium leading-[1.5] text-muted">Pagos rechazados</p>
      <div class="mt-1 flex items-end justify-between gap-3">
        <p class="text-[36px] font-semibold leading-[1.2] text-danger">{{ rejected }}</p>
        <p class="pb-1 text-[12px] leading-[1.5] text-muted">Registrados</p>
      </div>
    </div>
    <div class="flex min-h-[104px] flex-col justify-between rounded-lg border border-line bg-white p-5">
      <p class="text-[14px] font-medium leading-[1.5] text-muted">Total de pagos</p>
      <div class="mt-1 flex items-end justify-between gap-3">
        <p class="text-[36px] font-semibold leading-[1.2] text-ink">{{ total }}</p>
        <p class="pb-1 text-[12px] leading-[1.5] text-muted">Registrados</p>
      </div>
    </div>
  </div>
</template>
