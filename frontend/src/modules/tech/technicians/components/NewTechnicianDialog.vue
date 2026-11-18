<script setup lang="ts">
import { reactive, watch } from 'vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppInput from '@/shared/components/ui/AppInput.vue'
import AppModal from '@/shared/components/ui/AppModal.vue'
import type { TechnicianCreatePayload } from '@/types'

const props = withDefaults(
  defineProps<{
    open: boolean
    loading?: boolean
  }>(),
  { loading: false },
)

const emit = defineEmits<{
  create: [payload: TechnicianCreatePayload]
  cancel: []
}>()

const form = reactive({
  name: '',
  email: '',
  username: '',
  password: '',
  forceChange: true,
})

const errors = reactive({
  name: '',
  email: '',
  username: '',
  password: '',
})

watch(
  () => props.open,
  (open) => {
    if (!open) return
    form.name = ''
    form.email = ''
    form.username = ''
    form.password = ''
    form.forceChange = true
    errors.name = ''
    errors.email = ''
    errors.username = ''
    errors.password = ''
  },
)

function generatePassword(): void {
  const firstName = form.name.trim().split(/\s+/)[0] || 'Tecnico'
  form.password = `PLP!${firstName}${new Date().getFullYear()}#`
  errors.password = ''
}

function validate(): boolean {
  errors.name = form.name.trim() ? '' : 'El nombre es obligatorio'
  errors.email = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email) ? '' : 'Introduce un correo válido'
  errors.username = form.username.trim() ? '' : 'El usuario es obligatorio'
  errors.password = form.password.length >= 8 ? '' : 'Mínimo 8 caracteres'
  return !errors.name && !errors.email && !errors.username && !errors.password
}

function submit(): void {
  if (!validate()) return
  emit('create', {
    name: form.name.trim(),
    email: form.email.trim(),
    username: form.username.trim(),
    password: form.password,
    force_change: form.forceChange,
  })
}
</script>

<template>
  <AppModal
    :open="open"
    size="md"
    title="Nuevo técnico"
    :close-on-overlay="!loading"
    @close="emit('cancel')"
  >
    <p class="-mt-3 text-[14px] leading-[1.5] text-muted">Crea un acceso para el equipo de soporte.</p>
    <p class="mt-3 text-[12px] leading-[1.5] text-muted">* Campos obligatorios</p>

    <div class="mt-5 space-y-4">
      <AppInput
        v-model="form.name"
        label="Nombre completo *"
        placeholder="Ana López"
        :error="errors.name"
        @update:model-value="errors.name = ''"
      />
      <AppInput
        v-model="form.email"
        label="Correo *"
        placeholder="ana.lopez@plp.es"
        :error="errors.email"
        @update:model-value="errors.email = ''"
      />
      <AppInput
        v-model="form.username"
        label="Usuario *"
        placeholder="alopez"
        :error="errors.username"
        @update:model-value="errors.username = ''"
      />
      <div>
        <AppInput
          v-model="form.password"
          label="Contraseña inicial *"
          placeholder="Mínimo 8 caracteres"
          revealable
          :error="errors.password"
          @update:model-value="errors.password = ''"
        />
        <AppButton variant="secondary" size="sm" class="mt-2" @click="generatePassword">
          Generar contraseña
        </AppButton>
      </div>

      <div>
        <p class="plp-label mb-2">Rol</p>
        <div class="flex h-11 items-center rounded-md border border-line bg-app px-3 text-[14px] text-muted">
          Técnico
        </div>
      </div>

      <label class="flex items-center gap-3 text-[13px] leading-[1.5] text-ink">
        <input
          v-model="form.forceChange"
          type="checkbox"
          class="size-4 rounded border-line text-brand-700 focus:ring-brand-700"
        />
        Obligar a cambiar la contraseña en el primer acceso
      </label>
    </div>

    <div class="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
      <AppButton variant="secondary" :disabled="loading" @click="emit('cancel')">Cancelar</AppButton>
      <AppButton :loading="loading" @click="submit">Crear técnico</AppButton>
    </div>
  </AppModal>
</template>
