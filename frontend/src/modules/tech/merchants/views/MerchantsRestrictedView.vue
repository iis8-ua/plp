<script setup lang="ts">
import PageHeader from '@/shared/components/layout/PageHeader.vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppIcon from '@/shared/components/ui/AppIcon.vue'
</script>

<template>
  <div class="space-y-6">
    <PageHeader
      title="Comercios"
      description="Da de alta comercios y gestiona su acceso a PLP."
    />

    <section class="rounded-lg border border-line bg-white px-6 py-16 text-center">
      <div class="mx-auto grid size-12 place-items-center rounded-full bg-brand-100 text-brand-700">
        <AppIcon name="lock" :size="24" />
      </div>
      <h2 class="mt-4 text-[24px] font-semibold leading-[1.5] text-ink">Acceso restringido</h2>
      <p class="mx-auto mt-2 max-w-[460px] text-[14px] leading-[1.5] text-muted">
        La gestión de comercios está reservada al administrador. Si necesitas realizar un cambio,
        contacta con el equipo responsable.
      </p>
      <AppButton to="/tecnico/tickets" variant="secondary" class="mt-6">Volver a la bandeja</AppButton>
    </section>
  </div>
</template>
