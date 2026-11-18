<script setup lang="ts">
import { computed } from 'vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppIcon from '@/shared/components/ui/AppIcon.vue'
import AppModal from '@/shared/components/ui/AppModal.vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    title?: string
    name: string
    username: string
    password: string
  }>(),
  { title: 'Cuenta creada' },
)

const emit = defineEmits<{ close: []; createAnother: [] }>()

const summary = computed(() =>
  props.name ? `El acceso de ${props.name} ya está disponible.` : 'El acceso ya está disponible.',
)

async function copy(value: string): Promise<void> {
  try {
    await navigator.clipboard.writeText(value)
  } catch {
    // Si el navegador bloquea el portapapeles, el texto sigue visible.
  }
}
</script>

<template>
  <AppModal :open="open" size="sm" hide-header @close="emit('close')">
    <div class="grid size-12 place-items-center rounded-full bg-success-bg text-success-text">
      <AppIcon name="check" :size="24" />
    </div>
    <h2 class="mt-4 text-[24px] font-semibold leading-[1.5] text-ink">{{ title }}</h2>
    <p class="mt-1 text-[14px] leading-[1.5] text-muted">{{ summary }}</p>

    <div class="mt-5 rounded-lg border border-line p-4">
      <div class="flex items-center justify-between gap-3 pb-3">
        <div>
          <p class="text-[12px] leading-[1.5] text-muted">Usuario</p>
          <p class="mt-0.5 text-[14px] font-semibold text-ink">{{ username }}</p>
        </div>
        <AppButton variant="secondary" size="sm" @click="copy(username)">Copiar</AppButton>
      </div>
      <div class="flex items-center justify-between gap-3 border-t border-line pt-3">
        <div>
          <p class="text-[12px] leading-[1.5] text-muted">Contraseña inicial</p>
          <p class="mt-0.5 text-[14px] font-semibold text-ink">{{ password }}</p>
        </div>
        <AppButton variant="secondary" size="sm" @click="copy(password)">Copiar</AppButton>
      </div>
    </div>

    <div class="mt-4 rounded-lg bg-warning-bg px-4 py-3 text-[12px] leading-[1.5] text-warning-text">
      La contraseña solo se muestra ahora. Cópiala y compártela de forma segura.
    </div>

    <div class="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
      <AppButton variant="secondary" @click="emit('createAnother')">Crear otro</AppButton>
      <AppButton @click="emit('close')">Ir al listado</AppButton>
    </div>
  </AppModal>
</template>
