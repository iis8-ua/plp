<script setup lang="ts">
import { computed, useId } from 'vue'

const props = withDefaults(
  defineProps<{
    modelValue: string
    label?: string
    placeholder?: string
    hint?: string
    error?: string
    rows?: number
    disabled?: boolean
    id?: string
  }>(),
  { rows: 4, disabled: false },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const generatedId = useId()
const inputId = computed(() => props.id ?? `textarea-${generatedId}`)
</script>

<template>
  <div>
    <label v-if="label" :for="inputId" class="plp-label mb-2 block">{{ label }}</label>
    <textarea
      :id="inputId"
      :value="modelValue"
      :rows="rows"
      :placeholder="placeholder"
      :disabled="disabled"
      class="w-full resize-y rounded-md border bg-white px-3 py-3 text-[14px] leading-[1.5] text-ink placeholder:text-muted focus:border-brand-700 focus:outline-none focus:ring-1 focus:ring-brand-700 disabled:cursor-not-allowed disabled:bg-line-soft"
      :class="error ? 'border-danger-strong' : 'border-line'"
      @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
    />
    <p v-if="error" class="mt-1.5 text-[12px] leading-[1.5] text-danger">{{ error }}</p>
    <p v-else-if="hint" class="mt-1.5 text-[12px] leading-[1.5] text-muted">{{ hint }}</p>
  </div>
</template>
