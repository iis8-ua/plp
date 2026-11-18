<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, useId, watch } from 'vue'
import AppIcon from '@/shared/components/ui/AppIcon.vue'
import type { IconName } from '@/types/icons'

export interface SelectOption {
  value: string
  label: string
  disabled?: boolean
}

const props = withDefaults(
  defineProps<{
    modelValue: string
    options: SelectOption[]
    label?: string
    placeholder?: string
    error?: string
    hint?: string
    icon?: IconName
    size?: 'sm' | 'md'
    block?: boolean
    disabled?: boolean
    id?: string
    ariaLabel?: string
  }>(),
  { size: 'md', block: false, disabled: false, placeholder: 'Selecciona una opción' },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const generatedId = useId()
const selectId = computed(() => props.id ?? `select-${generatedId}`)
const open = ref(false)
const activeIndex = ref(-1)
const root = ref<HTMLElement | null>(null)
const listbox = ref<HTMLElement | null>(null)

const selected = computed(() => props.options.find((option) => option.value === props.modelValue))
const height = computed(() => (props.size === 'sm' ? 'h-10' : 'h-11'))

function toggle(): void {
  if (props.disabled) return
  open.value = !open.value
  if (open.value) {
    activeIndex.value = Math.max(
      0,
      props.options.findIndex((option) => option.value === props.modelValue),
    )
    void nextTick(() => listbox.value?.focus())
  }
}

function close(): void {
  open.value = false
}

function choose(option: SelectOption): void {
  if (option.disabled) return
  emit('update:modelValue', option.value)
  close()
}

function handleDocumentClick(event: MouseEvent): void {
  if (!root.value?.contains(event.target as Node)) close()
}

function handleKeydown(event: KeyboardEvent): void {
  if (!open.value) {
    if (event.key === 'ArrowDown' || event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      toggle()
    }
    return
  }

  if (event.key === 'Escape') {
    close()
    return
  }
  if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
    event.preventDefault()
    const direction = event.key === 'ArrowDown' ? 1 : -1
    let next = activeIndex.value
    for (let step = 0; step < props.options.length; step += 1) {
      next = (next + direction + props.options.length) % props.options.length
      if (!props.options[next]?.disabled) break
    }
    activeIndex.value = next
    return
  }
  if (event.key === 'Enter') {
    event.preventDefault()
    const option = props.options[activeIndex.value]
    if (option) choose(option)
  }
}

watch(
  () => props.disabled,
  (value) => {
    if (value) close()
  },
)

document.addEventListener('click', handleDocumentClick)
onBeforeUnmount(() => document.removeEventListener('click', handleDocumentClick))
</script>

<template>
  <div ref="root" class="relative" :class="block ? 'w-full' : ''">
    <label v-if="label" :id="`${selectId}-label`" class="plp-label mb-2 block">{{ label }}</label>
    <button
      :id="selectId"
      type="button"
      role="combobox"
      :aria-expanded="open"
      aria-haspopup="listbox"
      :aria-label="ariaLabel"
      :aria-labelledby="label ? `${selectId}-label` : undefined"
      :disabled="disabled"
      class="flex w-full items-center gap-2 rounded-md border bg-white px-3 text-left text-[13px] leading-[1.5] transition-colors disabled:cursor-not-allowed disabled:bg-line-soft disabled:text-muted"
      :class="[
        height,
        error ? 'border-danger-strong' : 'border-line hover:border-brand-300',
        open ? 'border-brand-700 ring-1 ring-brand-700' : '',
        icon ? 'pl-10' : '',
      ]"
      @click.stop="toggle"
      @keydown="handleKeydown"
    >
      <span v-if="icon" class="pointer-events-none absolute left-3 text-muted">
        <AppIcon :name="icon" :size="20" />
      </span>
      <span class="min-w-0 flex-1 truncate" :class="selected ? 'text-ink' : 'text-muted'">
        {{ selected?.label ?? placeholder }}
      </span>
      <AppIcon :name="open ? 'chevron-up' : 'chevron-down'" :size="20" class="shrink-0 text-muted" />
    </button>

    <p v-if="error" class="mt-1.5 text-[12px] leading-[1.5] text-danger">{{ error }}</p>
    <p v-else-if="hint" class="mt-1.5 text-[12px] leading-[1.5] text-muted">{{ hint }}</p>

    <Transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="opacity-0 -translate-y-1"
      leave-active-class="transition duration-75 ease-in"
      leave-to-class="opacity-0 -translate-y-1"
    >
      <ul
        v-if="open"
        ref="listbox"
        role="listbox"
        tabindex="-1"
        class="absolute left-0 top-[calc(100%+6px)] z-40 max-h-72 w-full min-w-[180px] overflow-auto rounded-lg border border-line bg-white p-2 outline-none"
        @keydown="handleKeydown"
      >
        <li
          v-for="(option, index) in options"
          :key="option.value"
          role="option"
          :aria-selected="option.value === modelValue"
          class="flex min-h-11 cursor-pointer items-center rounded-md px-3 text-[13px] leading-[1.5] transition-colors"
          :class="[
            option.value === modelValue ? 'bg-brand-100 font-semibold text-brand-700' : 'text-ink',
            index === activeIndex ? 'bg-app' : '',
            option.disabled ? 'cursor-not-allowed text-muted opacity-60' : 'hover:bg-app',
          ]"
          @click.stop="choose(option)"
          @mouseenter="activeIndex = index"
        >
          {{ option.label }}
        </li>
      </ul>
    </Transition>
  </div>
</template>
