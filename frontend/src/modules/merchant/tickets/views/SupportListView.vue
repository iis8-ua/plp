<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { useSupportStore } from '@/stores/support.store'
import { useUiStore } from '@/stores/ui.store'
import PageHeader from '@/shared/components/layout/PageHeader.vue'
import DataTable, { type DataColumn } from '@/shared/components/data/DataTable.vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppInput from '@/shared/components/ui/AppInput.vue'
import AppPagination from '@/shared/components/ui/AppPagination.vue'
import AppSelect from '@/shared/components/ui/AppSelect.vue'
import EmptyState from '@/shared/components/ui/EmptyState.vue'
import StatusBadge from '@/shared/components/ui/StatusBadge.vue'
import NewTicketDialog from '@/modules/merchant/tickets/components/NewTicketDialog.vue'
import { formatDate, formatTime } from '@/shared/utils/format'
import { TICKET_STATUS_OPTIONS } from '@/shared/utils/status'

const store = useSupportStore()
const auth = useAuthStore()
const ui = useUiStore()
const router = useRouter()

const newOpen = ref(false)

const columns: DataColumn[] = [
  { key: 'id', label: 'ID', class: 'w-[110px]', headerClass: 'w-[110px]' },
  { key: 'subject', label: 'Asunto' },
  { key: 'status', label: 'Estado', class: 'w-[140px]', headerClass: 'w-[140px]' },
  { key: 'createdAt', label: 'Creación', class: 'w-[150px]', headerClass: 'w-[150px]', mobile: false },
  { key: 'updatedAt', label: 'Última actualización', class: 'w-[190px]', headerClass: 'w-[190px]', mobile: false },
  { key: 'actions', label: 'Ver', class: 'w-[90px]', headerClass: 'w-[90px]' },
]

const statusOptions = [{ value: 'todos', label: 'Todos los estados' }, ...TICKET_STATUS_OPTIONS]

const hasFilters = computed(
  () => Boolean(store.filters.search) || store.filters.status !== 'todos',
)

const empty = computed(() => !store.loading && store.sorted.length === 0)

async function submitTicket(payload: { subject: string; description: string }): Promise<void> {
  try {
    await store.create({
      companyId: auth.user?.companyId ?? '',
      companyName: auth.user?.companyName ?? auth.user?.name ?? 'Comercio',
      subject: payload.subject,
      description: payload.description,
    })
    newOpen.value = false
    store.filters.search = ''
    store.filters.status = 'todos'
    store.page = 1
    ui.pushToast('success', 'Ticket enviado correctamente')
  } catch (cause) {
    ui.pushToast('error', cause instanceof Error ? cause.message : 'No se pudo enviar el ticket.')
  }
}

onMounted(() => {
  void store.load()
})
</script>

<template>
  <div class="space-y-6">
    <PageHeader
      title="Soporte"
      description="Consulta tus tickets y contacta con el equipo de soporte."
    >
      <template #actions>
        <AppButton @click="newOpen = true">+ Nuevo ticket</AppButton>
      </template>
    </PageHeader>

    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
      <div class="rounded-lg border border-line bg-white p-5">
        <div class="flex items-start justify-between gap-3">
          <p class="text-[14px] font-medium leading-[1.5] text-muted">Abiertos</p>
          <span class="rounded-pill bg-warning-bg px-2.5 py-1 text-[11px] font-semibold leading-none text-warning-text">
            Abiertos
          </span>
        </div>
        <p class="mt-2 text-[32px] font-semibold leading-[1.2] text-ink">{{ store.stats.abierto }}</p>
        <p class="mt-2 text-[12px] leading-[1.5] text-muted">Pendientes de revisión</p>
      </div>
      <div class="rounded-lg border border-line bg-white p-5">
        <div class="flex items-start justify-between gap-3">
          <p class="text-[14px] font-medium leading-[1.5] text-muted">En proceso</p>
          <span class="rounded-pill bg-info-bg px-2.5 py-1 text-[11px] font-semibold leading-none text-info-text">
            En proceso
          </span>
        </div>
        <p class="mt-2 text-[32px] font-semibold leading-[1.2] text-ink">{{ store.stats['en-proceso'] }}</p>
        <p class="mt-2 text-[12px] leading-[1.5] text-muted">El equipo está trabajando</p>
      </div>
      <div class="rounded-lg border border-line bg-white p-5">
        <div class="flex items-start justify-between gap-3">
          <p class="text-[14px] font-medium leading-[1.5] text-muted">Cerrados</p>
          <span class="rounded-pill bg-success-bg px-2.5 py-1 text-[11px] font-semibold leading-none text-success-text">
            Cerrados
          </span>
        </div>
        <p class="mt-2 text-[32px] font-semibold leading-[1.2] text-ink">{{ store.stats.cerrado }}</p>
        <p class="mt-2 text-[12px] leading-[1.5] text-muted">Consultas resueltas</p>
      </div>
    </div>

    <section class="rounded-lg border border-line bg-white">
      <div class="grid grid-cols-1 gap-3 p-5 sm:grid-cols-2 xl:grid-cols-[minmax(240px,1fr)_196px_192px]">
        <AppInput
          v-model="store.filters.search"
          icon="search"
          placeholder="ID o asunto del ticket"
          inputmode="search"
          aria-label="Buscar tickets"
        />
        <AppSelect v-model="store.filters.status" :options="statusOptions" :ariaLabel="'Filtrar por estado'" />
        <AppButton variant="secondary" :disabled="!hasFilters" @click="store.clearFilters()">
          Limpiar
        </AppButton>
      </div>

      <div class="flex flex-col gap-2 px-5 pb-4 sm:flex-row sm:items-center sm:justify-between">
        <p class="text-[13px] font-medium leading-[1.5] text-muted">
          {{ store.sorted.length }} tickets
        </p>
        <p class="flex items-center gap-2 text-[12px] leading-[1.5] text-muted">
          <span class="size-2 rounded-full bg-accent" aria-hidden="true" />
          Nueva respuesta del técnico
        </p>
      </div>

      <EmptyState
        v-if="empty"
        title="No hay tickets que coincidan con los filtros"
        description="Prueba con otra búsqueda o restablece los filtros."
        action-label="Limpiar filtros"
        icon="ticket"
        @action="store.clearFilters()"
      />

      <template v-else>
        <DataTable :columns="columns" :rows="store.paginated" :loading="store.loading" :skeleton-rows="5">
          <template #cell-id="{ row }">
            <span class="font-semibold text-ink">#{{ row.id }}</span>
          </template>
          <template #cell-subject="{ row }">
            <span class="flex items-center gap-2 text-ink">
              <span
                v-if="store.hasNewReply(row)"
                class="size-2 shrink-0 rounded-full bg-accent"
                aria-label="Nueva respuesta del técnico"
              />
              {{ row.subject }}
            </span>
          </template>
          <template #cell-status="{ row }">
            <StatusBadge kind="ticket" :status="row.status" />
          </template>
          <template #cell-createdAt="{ row }">
            <div class="text-[12px] leading-[1.5] text-muted">
              <p>{{ formatDate(row.createdAt) }}</p>
              <p>{{ formatTime(row.createdAt).slice(0, 5) }}</p>
            </div>
          </template>
          <template #cell-updatedAt="{ row }">
            <div class="text-[12px] leading-[1.5] text-muted">
              <p>{{ formatDate(row.updatedAt) }}</p>
              <p>{{ formatTime(row.updatedAt).slice(0, 5) }}</p>
            </div>
          </template>
          <template #cell-actions="{ row }">
            <div class="flex justify-end">
              <AppButton
                variant="secondary"
                size="sm"
                class="min-w-[56px]"
                @click="router.push(`/comercio/tickets/${row.id}`)"
              >
                Ver
              </AppButton>
            </div>
          </template>
        </DataTable>

        <div class="border-t border-line px-5 py-4">
          <AppPagination
            :page="store.page"
            :total-pages="store.totalPages"
            :range-start="store.rangeStart"
            :range-end="store.rangeEnd"
            :total="store.sorted.length"
            label="tickets"
            @update:page="store.page = $event"
          />
        </div>
      </template>
    </section>

    <NewTicketDialog
      :open="newOpen"
      :loading="store.saving"
      @submit="submitTicket"
      @cancel="newOpen = false"
    />
  </div>
</template>
