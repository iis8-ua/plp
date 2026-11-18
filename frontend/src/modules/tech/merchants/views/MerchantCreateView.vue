<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMerchantsStore } from '@/stores/merchants.store'
import { useUiStore } from '@/stores/ui.store'
import AppBreadcrumbs from '@/shared/components/layout/AppBreadcrumbs.vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppInput from '@/shared/components/ui/AppInput.vue'
import AppSelect from '@/shared/components/ui/AppSelect.vue'
import AccountCreatedDialog from '@/shared/components/ui/AccountCreatedDialog.vue'
import { createCompany } from '@/services/companies.service'
import { COMPANY_ACTIVITIES, COMPANY_TYPES, COUNTRIES, PROVINCES } from '@/shared/utils/company'
import type { CompanyForm, CreatedCompany } from '@/types'

const router = useRouter()
const store = useMerchantsStore()
const ui = useUiStore()

const created = ref<CreatedCompany | null>(null)
const createdOpen = ref(false)

const defaultForm = (): CompanyForm => ({
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
  username: '',
  password: '',
  forceChange: true,
})

const form = reactive<CompanyForm>(defaultForm())

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
  ['username', 'El usuario de acceso es obligatorio'],
]

function validate(): boolean {
  Object.keys(errors).forEach((key) => delete errors[key])
  REQUIRED.forEach(([field, message]) => {
    if (!String(form[field]).trim()) errors[field] = message
  })
  if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Introduce un correo válido'
  }
  if (form.password.length < 8) {
    errors.password = 'La contraseña debe tener al menos 8 caracteres'
  }
  return Object.keys(errors).length === 0
}

function generatePassword(): void {
  const firstName = form.nombre.trim().split(/\s+/)[0] || 'Comercio'
  form.password = `PLP!${firstName}${new Date().getFullYear()}#`
  errors.password = ''
}

function resetForm(): void {
  Object.assign(form, defaultForm())
  Object.keys(errors).forEach((key) => delete errors[key])
}

async function submit(): Promise<void> {
  if (!validate()) return
  try {
    created.value = await createCompany({ ...form })
    await store.load(true)
    createdOpen.value = true
  } catch (cause) {
    ui.pushToast('error', cause instanceof Error ? cause.message : 'No se pudo crear el comercio.')
  }
}

function closeCreated(): void {
  createdOpen.value = false
  created.value = null
  ui.pushToast('success', `Comercio ${form.nombre} creado correctamente`)
  void router.push('/tecnico/comercios')
}

function createAnother(): void {
  createdOpen.value = false
  created.value = null
  resetForm()
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

    <section class="rounded-lg border border-line bg-white p-6">
      <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Acceso al portal</h2>
      <p class="mt-1 text-[13px] leading-[1.5] text-muted">
        Crea la cuenta con la que el comercio entrará en PLP.
      </p>
      <div class="mt-5 grid grid-cols-1 gap-x-6 gap-y-4 lg:grid-cols-2">
        <AppInput
          v-model="form.username"
          label="Usuario *"
          placeholder="Ej. libreriahorizonte"
          :error="errors.username"
        />
        <div>
          <AppInput
            v-model="form.password"
            label="Contraseña inicial *"
            placeholder="Mínimo 8 caracteres"
            revealable
            :error="errors.password"
          />
          <AppButton variant="secondary" size="sm" class="mt-2" @click="generatePassword">
            Generar contraseña
          </AppButton>
        </div>
      </div>
      <label class="mt-4 flex items-center gap-3 text-[13px] leading-[1.5] text-ink">
        <input
          v-model="form.forceChange"
          type="checkbox"
          class="size-4 rounded border-line text-brand-700 focus:ring-brand-700"
        />
        Obligar a cambiar la contraseña en el primer acceso
      </label>
    </section>

    <div class="flex justify-end gap-3">
      <AppButton variant="secondary" to="/tecnico/comercios">Cancelar</AppButton>
      <AppButton :loading="store.saving" @click="submit">Crear comercio</AppButton>
    </div>

    <AccountCreatedDialog
      :open="createdOpen"
      title="Comercio creado"
      :name="created?.company.name ?? form.nombre"
      :username="created?.username ?? ''"
      :password="created?.password ?? ''"
      @close="closeCreated"
      @create-another="createAnother"
    />
  </div>
</template>
