<script setup lang="ts">
import { computed, ref, useId } from 'vue'
import AppIcon from '@/shared/components/ui/AppIcon.vue'
import type { IconName } from '@/types/icons'

const props = withDefaults(
  defineProps<{
    modelValue: string
    label?: string
    type?: string
    placeholder?: string
    hint?: string
    error?: string
    invalid?: boolean
    icon?: IconName
    suffix?: string
    autocomplete?: string
    name?: string
    id?: string
    disabled?: boolean
    maxlength?: number
    inputmode?: 'text' | 'numeric' | 'decimal' | 'search' | 'email'
    size?: 'md' | 'lg'
    revealable?: boolean
  }>(),
  {
    type: 'text',
    size: 'md',
    disabled: false,
    revealable: false,
    invalid: false,
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
  blur: []
}>()

const generatedId = useId()
const inputId = computed(() => props.id ?? `field-${generatedId}`)
const revealed = ref(false)
const actualType = computed(() => {
  if (props.type === 'password' && props.revealable) return revealed.value ? 'text' : 'password'
  return props.type
})

const height = computed(() => (props.size === 'lg' ? 'h-12' : 'h-11'))
</script>

<template>
  <div>
    <label v-if="label" :for="inputId" class="plp-label mb-2 block">{{ label }}</label>
    <div class="relative">
      <span v-if="icon" class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted">
        <AppIcon :name="icon" :size="20" />
      </span>
      <input
        :id="inputId"
        :name="name"
        :type="actualType"
        :value="modelValue"
        :placeholder="placeholder"
        :autocomplete="autocomplete"
        :disabled="disabled"
        :maxlength="maxlength"
        :inputmode="inputmode"
        class="w-full rounded-md border bg-white px-3 text-[14px] leading-[1.5] text-ink transition-colors placeholder:text-muted focus:border-brand-700 focus:outline-none focus:ring-1 focus:ring-brand-700 disabled:cursor-not-allowed disabled:bg-line-soft disabled:text-muted"
        :class="[
          height,
          icon ? 'pl-10' : '',
          revealable || suffix ? 'pr-12' : '',
          error || invalid ? 'border-danger-strong' : 'border-line',
        ]"
        @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        @blur="emit('blur')"
      />
      <span
        v-if="suffix"
        class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-[13px] font-medium text-muted"
      >
        {{ suffix }}
      </span>
      <button
        v-if="type === 'password' && revealable"
        type="button"
        class="absolute right-1 top-1/2 grid size-10 -translate-y-1/2 place-items-center rounded-md text-muted transition-colors hover:bg-app hover:text-ink"
        :aria-label="revealed ? 'Ocultar contraseña' : 'Mostrar contraseña'"
        @click="revealed = !revealed"
      >
        <AppIcon :name="revealed ? 'eye-off' : 'eye'" :size="20" />
      </button>
    </div>
    <p v-if="error" class="mt-1.5 text-[12px] leading-[1.5] text-danger">{{ error }}</p>
    <p v-else-if="hint" class="mt-1.5 text-[12px] leading-[1.5] text-muted">{{ hint }}</p>
  </div>
</template>
