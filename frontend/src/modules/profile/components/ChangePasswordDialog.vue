<script setup lang="ts">
import { ref, watch } from 'vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppInput from '@/shared/components/ui/AppInput.vue'
import AppModal from '@/shared/components/ui/AppModal.vue'
import InlineAlert from '@/shared/components/ui/InlineAlert.vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    loading?: boolean
    error?: string
  }>(),
  { loading: false, error: '' },
)

const emit = defineEmits<{
  submit: [payload: { current: string; next: string }]
  cancel: []
}>()

const current = ref('')
const next = ref('')
const repeat = ref('')
const localError = ref('')

watch(
  () => props.open,
  (open) => {
    if (!open) return
    current.value = ''
    next.value = ''
    repeat.value = ''
    localError.value = ''
  },
)

function submit(): void {
  if (!current.value) {
    localError.value = 'Introduce tu contraseña actual'
    return
  }
  if (next.value.length < 8) {
    localError.value = 'La nueva contraseña debe tener al menos 8 caracteres'
    return
  }
  if (next.value !== repeat.value) {
    localError.value = 'Las contraseñas no coinciden'
    return
  }
  localError.value = ''
  emit('submit', { current: current.value, next: next.value })
}
</script>

<template>
  <AppModal
    :open="open"
    size="sm"
    title="Cambiar contraseña"
    :close-on-overlay="!loading"
    @close="emit('cancel')"
  >
    <p class="-mt-3 text-[14px] leading-[1.5] text-muted">
      Introduce tu contraseña actual y elige una nueva.
    </p>

    <div class="mt-6 space-y-4">
      <AppInput
        v-model="current"
        label="Contraseña actual"
        revealable
        placeholder="Tu contraseña actual"
      />
      <AppInput
        v-model="next"
        label="Nueva contraseña"
        revealable
        placeholder="Mínimo 8 caracteres"
        hint="Mínimo 8 caracteres"
      />
      <AppInput
        v-model="repeat"
        label="Repetir nueva contraseña"
        revealable
        placeholder="Repite la nueva contraseña"
      />
      <InlineAlert v-if="localError || error" tone="error">
        {{ localError || error }}
      </InlineAlert>
    </div>

    <div class="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
      <AppButton variant="secondary" :disabled="loading" @click="emit('cancel')">Cancelar</AppButton>
      <AppButton :loading="loading" @click="submit">Actualizar</AppButton>
    </div>
  </AppModal>
</template>
