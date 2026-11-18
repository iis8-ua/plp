<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import AppAvatar from '@/shared/components/ui/AppAvatar.vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppIcon from '@/shared/components/ui/AppIcon.vue'
import AppInput from '@/shared/components/ui/AppInput.vue'
import AppModal from '@/shared/components/ui/AppModal.vue'
import { useTechniciansStore } from '@/stores/technicians.store'

const props = withDefaults(
  defineProps<{
    open: boolean
    loading?: boolean
  }>(),
  { loading: false },
)

const emit = defineEmits<{ confirm: [technicianId: string]; cancel: [] }>()

const store = useTechniciansStore()
const search = ref('')
const selected = ref('')

const filtered = computed(() => {
  const term = search.value.trim().toLowerCase()
  return store.technicians.filter(
    (technician) => !term || technician.name.toLowerCase().includes(term),
  )
})

watch(
  () => props.open,
  (open) => {
    if (!open) return
    search.value = ''
    selected.value = ''
    void store.load(true)
  },
)
</script>

<template>
  <AppModal :open="open" size="sm" hide-header :close-on-overlay="!loading" @close="emit('cancel')">
    <div class="flex items-start justify-between gap-4">
      <h2 class="text-[20px] font-semibold leading-[1.5] text-ink">Asignar técnico</h2>
      <button
        type="button"
        class="-mr-2 grid size-9 place-items-center rounded-md text-muted hover:bg-app hover:text-ink"
        aria-label="Cerrar"
        @click="emit('cancel')"
      >
        <AppIcon name="x" :size="18" />
      </button>
    </div>

    <div class="mt-4">
      <AppInput
        v-model="search"
        icon="search"
        placeholder="Buscar técnico..."
        aria-label="Buscar técnico"
      />
    </div>

    <div class="mt-4 max-h-[280px] space-y-2 overflow-y-auto">
      <button
        v-for="technician in filtered"
        :key="technician.id"
        type="button"
        class="flex w-full items-center gap-3 rounded-lg border px-3 py-3 text-left transition-colors"
        :class="
          selected === technician.id
            ? 'border-brand-700 bg-brand-100'
            : 'border-line bg-white hover:bg-app'
        "
        @click="selected = technician.id"
      >
        <AppAvatar :name="technician.name" :size="36" shape="circle" tone="brand" />
        <span class="min-w-0 flex-1">
          <span class="block truncate text-[14px] font-semibold text-ink">{{ technician.name }}</span>
          <span class="block text-[12px] leading-[1.5] text-muted">
            {{ technician.activity.open }} tickets abiertos
          </span>
        </span>
        <AppIcon v-if="selected === technician.id" name="check" :size="18" class="text-brand-700" />
      </button>

      <p v-if="!store.loading && filtered.length === 0" class="py-6 text-center text-[13px] text-muted">
        No hay técnicos que coincidan.
      </p>
    </div>

    <div class="mt-6">
      <AppButton block :disabled="!selected" :loading="loading" @click="emit('confirm', selected)">
        Asignar
      </AppButton>
    </div>
  </AppModal>
</template>
