<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import AppAvatar from '@/shared/components/ui/AppAvatar.vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppInput from '@/shared/components/ui/AppInput.vue'
import AppSelect from '@/shared/components/ui/AppSelect.vue'
import PageErrorState from '@/shared/components/ui/PageErrorState.vue'
import ChangePasswordDialog from '@/modules/profile/components/ChangePasswordDialog.vue'
import { useAuthStore } from '@/stores/auth.store'
import { useProfileStore } from '@/stores/profile.store'
import { useUiStore } from '@/stores/ui.store'
import { COMPANY_ACTIVITIES, COUNTRIES, PROVINCES } from '@/shared/utils/company'

const auth = useAuthStore()
const store = useProfileStore()
const ui = useUiStore()

const passwordOpen = ref(false)
const passwordError = ref('')

const userForm = reactive({ name: '', email: '' })
const companyForm = reactive({
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

const profile = computed(() => store.profile)
const isCommerce = computed(() => profile.value?.role === 'comercio')

const roleLabel = computed(() => {
  if (profile.value?.role === 'admin') return 'Administrador'
  if (profile.value?.role === 'tecnico') return 'Técnico'
  return 'Comercio'
})

const heading = computed(() =>
  isCommerce.value ? 'La información de tu comercio' : 'Tu información, actualizada',
)

const description = computed(() =>
  isCommerce.value
    ? 'Mantén actualizados tus datos fiscales y de contacto.'
    : 'Gestiona tus datos personales y tu cuenta de PLP.',
)

const subtitle = computed(() => {
  if (!profile.value) return ''
  if (isCommerce.value && profile.value.company) {
    return `Comercio · ${profile.value.company.id.slice(0, 8)}`
  }
  return `${roleLabel.value} · ${profile.value.username}`
})

function fillForms(): void {
  if (!profile.value) return
  userForm.name = profile.value.name
  userForm.email = profile.value.email
  if (profile.value.company) {
    companyForm.nombre = profile.value.company.nombre
    companyForm.razon_social = profile.value.company.razonSocial
    companyForm.cif = profile.value.company.cif
    companyForm.tipo_empresa = profile.value.company.tipoEmpresa
    companyForm.actividad_economica = profile.value.company.actividadEconomica
    companyForm.direccion = profile.value.company.direccion
    companyForm.codigo_postal = profile.value.company.codigoPostal
    companyForm.ciudad = profile.value.company.ciudad
    companyForm.provincia = profile.value.company.provincia
    companyForm.pais = profile.value.company.pais
    companyForm.telefono = profile.value.company.telefono
    companyForm.email = profile.value.company.email
    companyForm.web = profile.value.company.web
  }
}

async function save(): Promise<void> {
  try {
    if (isCommerce.value) {
      await store.save({ ...companyForm })
      auth.updateUser({ name: companyForm.nombre, companyName: companyForm.nombre })
    } else {
      await store.save({ name: userForm.name, email: userForm.email })
      auth.updateUser({ name: userForm.name })
    }
    fillForms()
    ui.pushToast('success', 'Perfil actualizado correctamente')
  } catch (cause) {
    ui.pushToast('error', cause instanceof Error ? cause.message : 'No se pudo actualizar el perfil.')
  }
}

function cancel(): void {
  fillForms()
}

async function changePassword(payload: { current: string; next: string }): Promise<void> {
  passwordError.value = ''
  try {
    await store.updatePassword(payload.current, payload.next)
    auth.updateUser({ forcePasswordChange: false })
    passwordOpen.value = false
    ui.pushToast('success', 'Contraseña actualizada correctamente')
  } catch (cause) {
    passwordError.value =
      cause instanceof Error ? cause.message : 'No se pudo actualizar la contraseña.'
  }
}

onMounted(async () => {
  await store.load()
  fillForms()
  if (auth.user?.forcePasswordChange) passwordOpen.value = true
})
</script>

<template>
  <div class="space-y-6">
    <div v-if="store.loading && !profile" class="space-y-4">
      <div class="h-8 w-72 animate-pulse rounded bg-line-soft" />
      <div class="h-28 animate-pulse rounded-lg bg-line-soft" />
      <div class="h-72 animate-pulse rounded-lg bg-line-soft" />
    </div>

    <PageErrorState
      v-else-if="!profile"
      title="No se pudo cargar el perfil"
      description="Inténtalo de nuevo en unos segundos."
      action-label="Recargar"
      @action="store.load(true)"
    />

    <template v-else>
      <div>
        <h1 class="text-[28px] font-semibold leading-[1.5] text-ink lg:text-[32px]">{{ heading }}</h1>
        <p class="mt-1 text-[14px] leading-[1.5] text-muted">{{ description }}</p>
      </div>

      <section class="rounded-lg border border-line bg-white p-6">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex items-center gap-4">
            <AppAvatar :name="profile.name" :size="48" shape="circle" tone="brand" />
            <div>
              <p class="text-[22px] font-semibold leading-[1.5] text-ink">{{ profile.name }}</p>
              <p class="text-[13px] leading-[1.5] text-muted">{{ subtitle }}</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <span class="rounded-pill bg-success-bg px-3 py-1 text-[12px] font-semibold text-success-text">
              Cuenta {{ profile.status === 'Activo' ? 'activa' : 'inactiva' }}
            </span>
          </div>
        </div>
      </section>

      <template v-if="isCommerce">
        <section class="rounded-lg border border-line bg-white p-6">
          <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Datos del comercio</h2>
          <div class="mt-5 grid grid-cols-1 gap-x-6 gap-y-4 lg:grid-cols-3">
            <AppInput v-model="companyForm.nombre" label="Nombre comercial" />
            <AppInput :model-value="companyForm.razon_social" label="Razón social · Solo lectura" disabled />
            <AppInput :model-value="companyForm.cif" label="CIF/NIF · Solo lectura" disabled />
            <AppInput :model-value="companyForm.tipo_empresa" label="Tipo de empresa · Solo lectura" disabled />
            <AppSelect v-model="companyForm.actividad_economica" label="Actividad económica" :options="COMPANY_ACTIVITIES" class="lg:col-span-2" />
          </div>
        </section>

        <div class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_380px]">
          <section class="rounded-lg border border-line bg-white p-6">
            <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Dirección fiscal</h2>
            <div class="mt-5 grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-2">
              <AppInput v-model="companyForm.direccion" label="Dirección" class="sm:col-span-2" />
              <AppInput v-model="companyForm.codigo_postal" label="CP" />
              <AppInput v-model="companyForm.ciudad" label="Ciudad" />
              <AppSelect v-model="companyForm.provincia" label="Provincia" :options="PROVINCES" />
              <AppSelect v-model="companyForm.pais" label="País" :options="COUNTRIES" />
            </div>
          </section>

          <section class="rounded-lg border border-line bg-white p-6">
            <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Contacto</h2>
            <div class="mt-5 space-y-4">
              <AppInput v-model="companyForm.telefono" label="Teléfono" />
              <AppInput v-model="companyForm.email" label="Correo" />
              <AppInput v-model="companyForm.web" label="Web" placeholder="https://" />
            </div>
          </section>
        </div>

        <section class="flex flex-col gap-4 rounded-lg border border-line bg-white p-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Acceso</h2>
            <p class="mt-1 text-[14px] leading-[1.5] text-muted">Gestiona la seguridad de tu cuenta.</p>
          </div>
          <AppButton variant="secondary" @click="passwordOpen = true">Cambiar contraseña</AppButton>
        </section>
      </template>

      <template v-else>
        <section class="rounded-lg border border-line bg-white p-6">
          <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Datos personales</h2>
          <div class="mt-5 grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-2">
            <AppInput v-model="userForm.name" label="Nombre" />
            <AppInput v-model="userForm.email" label="Correo" />
            <AppInput :model-value="profile.username" label="Usuario · Solo lectura" disabled />
            <AppInput :model-value="roleLabel" label="Rol · Solo lectura" disabled />
          </div>
        </section>

        <section v-if="profile.role === 'tecnico' && profile.activity" class="rounded-lg border border-line bg-white p-6">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Mi actividad</h2>
            <p class="text-[12px] leading-[1.5] text-muted">Resumen de tus tickets de soporte</p>
          </div>
          <div class="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div class="rounded-lg bg-app p-4">
              <p class="text-[12px] leading-[1.5] text-muted">Tickets asignados</p>
              <p class="mt-1 text-[28px] font-semibold leading-[1.2] text-brand-700">{{ profile.activity.assigned }}</p>
            </div>
            <div class="rounded-lg bg-app p-4">
              <p class="text-[12px] leading-[1.5] text-muted">En proceso</p>
              <p class="mt-1 text-[28px] font-semibold leading-[1.2] text-info-text">{{ profile.activity.in_progress }}</p>
            </div>
            <div class="rounded-lg bg-app p-4">
              <p class="text-[12px] leading-[1.5] text-muted">Cerrados</p>
              <p class="mt-1 text-[28px] font-semibold leading-[1.2] text-success-text">{{ profile.activity.closed }}</p>
            </div>
          </div>
        </section>

        <section class="flex flex-col gap-4 rounded-lg border border-line bg-white p-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Acceso</h2>
            <p class="mt-1 text-[14px] leading-[1.5] text-muted">Actualiza tu contraseña para mantener tu cuenta segura.</p>
          </div>
          <AppButton variant="secondary" @click="passwordOpen = true">Cambiar contraseña</AppButton>
        </section>
      </template>

      <div class="flex justify-end gap-3">
        <AppButton variant="secondary" @click="cancel">Cancelar</AppButton>
        <AppButton :loading="store.saving" @click="save">Guardar cambios</AppButton>
      </div>
    </template>

    <ChangePasswordDialog
      :open="passwordOpen"
      :loading="store.saving"
      :error="passwordError"
      @submit="changePassword"
      @cancel="passwordOpen = false"
    />
  </div>
</template>
