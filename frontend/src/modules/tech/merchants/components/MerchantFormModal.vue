<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppInput from '@/shared/components/ui/AppInput.vue'
import AppModal from '@/shared/components/ui/AppModal.vue'
import InlineAlert from '@/shared/components/ui/InlineAlert.vue'
import { useMerchantsStore } from '@/stores/merchants.store'
import type { Company } from '@/types'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ close: []; created: [company: Company] }>()

const store = useMerchantsStore()
const name = ref('')
const fieldError = ref('')
const actionError = ref('')

const counterVisible = computed(() => name.value.length > 0)

watch(
  () => props.open,
  (open) => {
    if (open) {
      name.value = ''
      fieldError.value = ''
      actionError.value = ''
    }
  },
)

function validate(): boolean {
  const value = name.value.trim()
  if (!value) {
    fieldError.value = 'El nombre es obligatorio'
    return false
  }
  if (value.length > 100) {
    fieldError.value = 'El nombre no puede superar los 100 caracteres'
    return false
  }
  fieldError.value = ''
  return true
}

async function submit(): Promise<void> {
  actionError.value = ''
  if (!validate()) return
  try {
    const company = await store.addCompany(name.value)
    emit('created', company)
    emit('close')
  } catch (cause) {
    actionError.value =
      cause instanceof Error ? cause.message : 'No se ha podido completar la acción. Inténtalo de nuevo'
  }
}
</script>

<template>
  <AppModal :open="open" title="Nuevo comercio" size="md" :close-on-overlay="!store.saving" @close="emit('close')">
    <form novalidate @submit.prevent="submit">
      <div>
        <AppInput
          v-model="name"
          label="Nombre del comercio"
          placeholder="Ej. Panadería Alameda"
          :invalid="Boolean(fieldError)"
          :maxlength="140"
          size="lg"
          @update:model-value="fieldError = ''; actionError = ''"
        />
        <div class="mt-1.5 flex items-center justify-between gap-3">
          <p class="text-[12px] leading-[1.5] text-muted">Máx. 100 caracteres</p>
          <p
            v-if="counterVisible"
            class="text-[12px] leading-[1.5]"
            :class="name.length > 100 ? 'text-danger' : 'text-muted'"
          >
            {{ name.length }} / 100
          </p>
        </div>
        <p v-if="fieldError" class="mt-2 text-[12px] leading-[1.5] text-danger">{{ fieldError }}</p>
      </div>

      <InlineAlert v-if="actionError" tone="error" class="mt-4">
        {{ actionError }}
        <p class="mt-1 text-[12px]">El nombre se ha conservado para que puedas reintentarlo.</p>
      </InlineAlert>

      <div class="mt-10 grid grid-cols-2 gap-4">
        <AppButton variant="secondary" :disabled="store.saving" @click="emit('close')">Cancelar</AppButton>
        <AppButton type="submit" :loading="store.saving">Crear comercio</AppButton>
      </div>
    </form>
  </AppModal>
</template>
