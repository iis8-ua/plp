<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthCard from '@/shared/components/layout/AuthCard.vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppInput from '@/shared/components/ui/AppInput.vue'
import InlineAlert from '@/shared/components/ui/InlineAlert.vue'
import { useAuthStore } from '@/stores/auth.store'

const props = defineProps<{ portal: 'tecnico' | 'comercio' }>()

const auth = useAuthStore()
const router = useRouter()

const form = reactive({ username: '', password: '' })
const fieldErrors = reactive({ username: '', password: '' })
const formError = ref('')

const copy = computed(() =>
  props.portal === 'tecnico'
    ? {
        title: 'Acceso técnicos',
        subtitle: 'Gestiona el soporte de nuestros comercios.',
        userPlaceholder: 'Tu usuario de técnico',
        note: 'Acceso exclusivo para personal autorizado',
      }
    : {
        title: 'Acceso comercios',
        subtitle: 'Gestiona los pagos y el saldo de tu comercio.',
        userPlaceholder: 'Tu usuario de comercio',
        note: 'Acceso exclusivo para comercios de PLP',
      },
)

function validate(): boolean {
  fieldErrors.username = form.username.trim() ? '' : 'Introduce tu usuario'
  fieldErrors.password = form.password ? '' : 'Introduce tu contraseña'
  return !fieldErrors.username && !fieldErrors.password
}

async function submit(): Promise<void> {
  formError.value = ''
  auth.clearError()
  if (!validate()) return

  try {
    await auth.login(form.username, form.password, props.portal)
    await router.push(auth.homeRoute)
  } catch (cause) {
    formError.value = cause instanceof Error ? cause.message : 'No se pudo iniciar sesión.'
  }
}
</script>

<template>
  <AuthCard>
    <h1 class="text-[28px] font-semibold leading-[1.5] text-ink">{{ copy.title }}</h1>
    <p class="mt-1 text-[14px] leading-[1.5] text-muted">{{ copy.subtitle }}</p>

    <form class="mt-8 space-y-6" novalidate @submit.prevent="submit">
      <AppInput
        v-model="form.username"
        label="Usuario"
        :placeholder="copy.userPlaceholder"
        autocomplete="username"
        size="lg"
        :error="fieldErrors.username"
        @update:model-value="fieldErrors.username = ''; formError = ''"
      />
      <AppInput
        v-model="form.password"
        label="Contraseña"
        type="password"
        placeholder="Introduce tu contraseña"
        autocomplete="current-password"
        size="lg"
        revealable
        :error="fieldErrors.password"
        @update:model-value="fieldErrors.password = ''; formError = ''"
      />

      <InlineAlert v-if="formError" tone="error">{{ formError }}</InlineAlert>

      <AppButton type="submit" size="lg" block :loading="auth.loading">Iniciar sesión</AppButton>
    </form>

    <p class="mt-8 text-[12px] leading-[1.5] text-muted">{{ copy.note }}</p>
  </AuthCard>
</template>
