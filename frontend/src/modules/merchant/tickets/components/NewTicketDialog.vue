<script setup lang="ts">
import { reactive, watch } from 'vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppInput from '@/shared/components/ui/AppInput.vue'
import AppModal from '@/shared/components/ui/AppModal.vue'
import AppTextarea from '@/shared/components/ui/AppTextarea.vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    loading?: boolean
  }>(),
  { loading: false },
)

const emit = defineEmits<{
  submit: [payload: { subject: string; description: string }]
  cancel: []
}>()

const form = reactive({ subject: '', description: '' })
const errors = reactive({ subject: '', description: '' })

watch(
  () => props.open,
  (open) => {
    if (!open) return
    form.subject = ''
    form.description = ''
    errors.subject = ''
    errors.description = ''
  },
)

function validate(): boolean {
  errors.subject = form.subject.trim() ? '' : 'El asunto es obligatorio'
  errors.description = form.description.trim() ? '' : 'La descripción es obligatoria'
  return !errors.subject && !errors.description
}

function submit(): void {
  if (!validate()) return
  emit('submit', { subject: form.subject.trim(), description: form.description.trim() })
}
</script>

<template>
  <AppModal
    :open="open"
    size="lg"
    hide-header
    :close-on-overlay="!loading"
    @close="emit('cancel')"
  >
    <h2 class="text-[24px] font-semibold leading-[1.5] text-ink">Nuevo ticket de soporte</h2>
    <p class="mt-1 text-[14px] leading-[1.5] text-muted">Cuéntanos cómo podemos ayudarte.</p>

    <div class="mt-6 space-y-5">
      <AppInput
        v-model="form.subject"
        label="Asunto *"
        placeholder="Resumen de la consulta"
        :error="errors.subject"
        @update:model-value="errors.subject = ''"
      />
      <AppTextarea
        v-model="form.description"
        label="Descripción *"
        placeholder="Detalla lo que necesitas y el contexto de la incidencia"
        :rows="5"
        :error="errors.description"
      />
    </div>

    <p class="mt-4 text-[12px] leading-[1.5] text-muted">* Campos obligatorios</p>

    <div class="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-[200px_minmax(0,1fr)]">
      <AppButton variant="secondary" :disabled="loading" @click="emit('cancel')">
        Cancelar
      </AppButton>
      <AppButton :loading="loading" @click="submit">Enviar ticket</AppButton>
    </div>
  </AppModal>
</template>
