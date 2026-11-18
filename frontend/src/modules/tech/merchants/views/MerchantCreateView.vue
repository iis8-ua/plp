<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMerchantsStore } from '@/stores/merchants.store'
import { useUiStore } from '@/stores/ui.store'
import AppBreadcrumbs from '@/shared/components/layout/AppBreadcrumbs.vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppInput from '@/shared/components/ui/AppInput.vue'
import AppSelect from '@/shared/components/ui/AppSelect.vue'
import { createCompany } from '@/services/companies.service'
import { COMPANY_ACTIVITIES, COMPANY_TYPES, COUNTRIES, PROVINCES } from '@/shared/utils/company'
import type { CompanyForm } from '@/types'

const router = useRouter()
const store = useMerchantsStore()
const ui = useUiStore()

const form = reactive<CompanyForm>({
  nombre: '',
  razon_social: '',
  cif: '',
  tipo_empresa: '',
  actividad_economica: '',
  direccion: '',
  codigo_postal: '',
  ciudad: '',
  provincia: '',
  pais: 'España',
  telefono: '',
  email: '',
  web: '',
})

const errors = reactive<Record<string, string>>({})

const REQUIRED: Array<[keyof CompanyForm, string]> = [
  ['nombre', 'El nombre comercial es obligatorio'],
  ['razon_social', 'La razón social es obligatoria'],
  ['cif', 'El CIF/NIF es obligatorio'],
  ['tipo_empresa', 'Selecciona un tipo de empresa'],
  ['actividad_economica', 'Selecciona una actividad'],
  ['direccion', 'La dirección fiscal es obligatoria'],
  ['codigo_postal', 'El código postal es obligatorio'],
  ['ciudad', 'La ciudad es obligatoria'],
  ['provincia', 'Selecciona una provincia'],
  ['pais', 'Selecciona un país'],
  ['telefono', 'El teléfono es obligatorio'],
  ['email', 'El correo electrónico es obligatorio'],
]

function validate(): boolean {
  Object.keys(errors).forEach((key) => delete errors[key])
  REQUIRED.forEach(([field, message]) => {
    if (!String(form[field]).trim()) errors[field] = message
  })
  if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Introduce un correo válido'
  }
  return Object.keys(errors).length === 0
}

async function submit(): Promise<void> {
  if (!validate()) return
  try {
    await createCompany({ ...form })
    await store.load(true)
    ui.pushToast('success', `Comercio ${form.nombre} creado correctamente`)
    void router.push('/tecnico/comercios')
  } catch (cause) {
    ui.pushToast('error', cause instanceof Error ? cause.message : 'No se pudo crear el comercio.')
  }
}
</script>

<template>
  <div class="space-y-6">
    <AppBreadcrumbs
      :items="[
        { label: 'Comercios', to: '/tecnico/comercios' },
        { label: 'Nuevo comercio' },
      ]"
      separator=">"
    />

    <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <h1 class="text-[28px] font-semibold leading-[1.5] text-ink lg:text-[32px]">Nuevo comercio</h1>
        <p class="mt-1 text-[14px] leading-[1.5] text-muted">
          Completa los datos para dar de alta un nuevo comercio.
        </p>
      </div>
      <p class="text-[12px] leading-[1.5] text-muted">* Campos obligatorios</p>
    </div>

    <section class="rounded-lg border border-line bg-white p-6">
      <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Datos del comercio</h2>
      <div class="mt-5 grid grid-cols-1 gap-x-6 gap-y-4 lg:grid-cols-2">
        <AppInput v-model="form.nombre" label="Nombre comercial *" placeholder="Ej. Librería Horizonte" :error="errors.nombre" />
        <AppInput v-model="form.razon_social" label="Razón social *" placeholder="Ej. Librería Horizonte, S.L." :error="errors.razon_social" />
        <AppInput v-model="form.cif" label="CIF/NIF *" placeholder="Ej. B12345678" :error="errors.cif" />
        <AppSelect v-model="form.tipo_empresa" label="Tipo de empresa *" :options="COMPANY_TYPES" placeholder="Selecciona un tipo de empresa" :error="errors.tipo_empresa" />
        <AppSelect v-model="form.actividad_economica" label="Actividad económica *" :options="COMPANY_ACTIVITIES" placeholder="Busca y selecciona una actividad" :error="errors.actividad_economica" class="lg:col-span-2" />
      </div>
    </section>

    <section class="rounded-lg border border-line bg-white p-6">
      <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Dirección fiscal</h2>
      <div class="mt-5 grid grid-cols-1 gap-x-6 gap-y-4 lg:grid-cols-2">
        <AppInput v-model="form.direccion" label="Dirección fiscal *" placeholder="Calle, número, piso y puerta" :error="errors.direccion" />
        <AppInput v-model="form.codigo_postal" label="Código postal *" placeholder="Ej. 28001" :error="errors.codigo_postal" />
        <AppInput v-model="form.ciudad" label="Ciudad *" placeholder="Ej. Madrid" :error="errors.ciudad" />
        <AppSelect v-model="form.provincia" label="Provincia *" :options="PROVINCES" placeholder="Selecciona una provincia" :error="errors.provincia" />
        <AppSelect v-model="form.pais" label="País *" :options="COUNTRIES" placeholder="Selecciona un país" :error="errors.pais" />
      </div>
    </section>

    <section class="rounded-lg border border-line bg-white p-6">
      <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Contacto</h2>
      <div class="mt-5 grid grid-cols-1 gap-x-6 gap-y-4 lg:grid-cols-2">
        <AppInput v-model="form.telefono" label="Teléfono *" placeholder="Ej. +34 612 345 678" :error="errors.telefono" />
        <AppInput v-model="form.email" label="Correo electrónico *" placeholder="Ej. contacto@comercio.es" :error="errors.email" />
        <AppInput v-model="form.web" label="Página web" placeholder="https://www.comercio.es" hint="Opcional" class="lg:col-span-2" />
      </div>
    </section>

    <div class="flex justify-end gap-3">
      <AppButton variant="secondary" to="/tecnico/comercios">Cancelar</AppButton>
      <AppButton :loading="store.saving" @click="submit">Crear comercio</AppButton>
    </div>
  </div>
</template>
