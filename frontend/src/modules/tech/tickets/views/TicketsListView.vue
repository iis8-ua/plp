<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '@/shared/components/layout/PageHeader.vue'
import DataTable, { type DataColumn } from '@/shared/components/data/DataTable.vue'
import StatCard from '@/shared/components/data/StatCard.vue'
import ActionMenu from '@/shared/components/ui/ActionMenu.vue'
import AppAvatar from '@/shared/components/ui/AppAvatar.vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppPagination from '@/shared/components/ui/AppPagination.vue'
import AppSelect from '@/shared/components/ui/AppSelect.vue'
import EmptyState from '@/shared/components/ui/EmptyState.vue'
import StatusBadge from '@/shared/components/ui/StatusBadge.vue'
import AssignTechnicianDialog from '@/modules/tech/tickets/components/AssignTechnicianDialog.vue'
import DeleteTicketDialog from '@/modules/tech/tickets/components/DeleteTicketDialog.vue'
import TicketFilters from '@/modules/tech/tickets/components/TicketFilters.vue'
import { useAuthStore } from '@/stores/auth.store'
import { useTicketsStore } from '@/stores/tickets.store'
import { useUiStore } from '@/stores/ui.store'
import { formatDate, formatDateTime } from '@/shared/utils/format'
import type { Ticket } from '@/types'

const store = useTicketsStore()
const auth = useAuthStore()
const ui = useUiStore()
const router = useRouter()

const deleting = ref<Ticket | null>(null)
const deleteOpen = ref(false)
const assignTarget = ref<Ticket | null>(null)
const assignOpen = ref(false)

const columns: DataColumn[] = [
  { key: 'id', label: 'ID', class: 'w-[64px]', headerClass: 'w-[64px]', mobile: false },
  { key: 'merchant', label: 'Comercio', class: 'w-[136px]', headerClass: 'w-[136px]' },
  { key: 'subject', label: 'Asunto' },
  { key: 'status', label: 'Estado', class: 'w-[96px]', headerClass: 'w-[96px]' },
  { key: 'createdAt', label: 'Fecha de creación', class: 'w-[104px]', headerClass: 'w-[104px]', mobile: false },
  { key: 'updatedAt', label: 'Última actualización', class: 'w-[124px]', headerClass: 'w-[124px]', mobile: false },
  { key: 'assignee', label: 'Responsable', class: 'w-[132px]', headerClass: 'w-[132px]' },
  { key: 'actions', label: 'Acciones', class: 'w-[280px]', headerClass: 'w-[280px]' },
]

const sortOptions = [
  { value: 'abiertos-antiguos', label: 'Abiertos más antiguos primero' },
  { value: 'recientes', label: 'Actualizados recientemente' },
  { value: 'antiguos', label: 'Más antiguos primero' },
]

const assignmentTabs: Array<{ value: 'mios' | 'sin-asignar' | 'todos'; label: string }> = [
  { value: 'mios', label: 'Asignados a mí' },
  { value: 'sin-asignar', label: 'Sin asignar' },
  { value: 'todos', label: 'Todos' },
]

const timestamp = computed(() => {
  if (!store.lastUpdated) return ''
  return `Actualizado hoy, ${store.lastUpdated.slice(11, 16)}`
})

const empty = computed(() => !store.loading && store.sorted.length === 0)

function menuItems(): Array<{ key: string; label: string; tone: 'primary' | 'danger' }> {
  const items: Array<{ key: string; label: string; tone: 'primary' | 'danger' }> = [
    { key: 'status', label: 'Cambiar estado', tone: 'primary' },
  ]
  if (auth.role === 'admin') {
    items.push({ key: 'assign', label: 'Asignar', tone: 'primary' })
  }
  items.push({ key: 'delete', label: 'Eliminar', tone: 'danger' })
  return items
}

function openTicket(ticket: Ticket): void {
  void router.push(`/tecnico/tickets/${ticket.id}`)
}

function openDelete(ticket: Ticket): void {
  deleting.value = ticket
  deleteOpen.value = true
}

function openAssign(ticket: Ticket): void {
  assignTarget.value = ticket
  assignOpen.value = true
}

async function assignSelf(ticket: Ticket): Promise<void> {
  try {
    await store.assignTo(ticket.id)
    ui.pushToast('success', `Ticket #${ticket.id} asignado a ti`)
  } catch (cause) {
    ui.pushToast('error', cause instanceof Error ? cause.message : 'No se pudo asignar el ticket.')
  }
}

async function confirmAssign(technicianId: string): Promise<void> {
  if (!assignTarget.value) return
  try {
    await store.assignTo(assignTarget.value.id, technicianId)
    assignOpen.value = false
    assignTarget.value = null
    ui.pushToast('success', 'Ticket asignado correctamente')
  } catch (cause) {
    ui.pushToast('error', cause instanceof Error ? cause.message : 'No se pudo asignar el ticket.')
  }
}

async function confirmDelete(): Promise<void> {
  if (!deleting.value) return
  try {
    await store.removeTicket(deleting.value.id)
    deleteOpen.value = false
    deleting.value = null
  } catch (cause) {
    ui.pushToast('error', cause instanceof Error ? cause.message : 'No se pudo eliminar el ticket.')
  }
}

onMounted(() => {
  void store.load()
})
</script>

<template>
  <div class="space-y-6">
    <PageHeader
      title="Tu bandeja, al día"
      description="Consulta, prioriza y resuelve las incidencias de los comercios."
      :timestamp="timestamp"
    />

    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard label="Total" :value="store.stats.total" context="Todos los tickets" tone="brand" />
      <StatCard label="Abiertos" :value="store.stats.abierto" context="Pendientes de revisión" tone="warning" />
      <StatCard
        label="En proceso"
        :value="store.stats['en-proceso']"
        context="En manos del equipo"
        tone="info"
      />
      <StatCard label="Cerrados" :value="store.stats.cerrado" context="Incidencias resueltas" tone="success" />
    </div>

    <section class="rounded-lg border border-line bg-white">
      <div class="p-5">
        <TicketFilters />
      </div>

      <div class="flex flex-wrap items-center gap-2 px-5 pb-4">
        <div class="inline-flex overflow-hidden rounded-md border border-line">
          <button
            v-for="tab in assignmentTabs"
            :key="tab.value"
            type="button"
            class="h-9 px-4 text-[13px] font-medium transition-colors"
            :class="
              store.filters.assignee === tab.value
                ? 'bg-brand-700 text-white'
                : 'bg-white text-secondary hover:bg-app'
            "
            @click="store.filters.assignee = tab.value"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>

      <div class="flex flex-col gap-3 px-5 pb-4 sm:flex-row sm:items-center sm:justify-between">
        <p class="text-[13px] font-medium leading-[1.5] text-muted">
          {{ store.sorted.length }} tickets
        </p>
        <div class="flex w-full flex-col gap-2 sm:w-auto sm:flex-row sm:items-center">
          <span class="text-[12px] leading-[1.5] text-muted">Ordenar:</span>
          <AppSelect
            v-model="store.filters.sort"
            :options="sortOptions"
            size="sm"
            class="w-full sm:w-[360px]"
            :ariaLabel="'Ordenar tickets'"
          />
        </div>
      </div>

      <EmptyState
        v-if="empty"
        title="No hay tickets que coincidan con los filtros"
        description="Prueba con otra búsqueda o restablece los filtros."
        action-label="Limpiar filtros"
        icon="search"
        @action="store.clearFilters()"
      />

      <template v-else>
        <DataTable
          :columns="columns"
          :rows="store.paginated"
          :loading="store.loading"
          :skeleton-rows="5"
        >
          <template #cell-id="{ row }">
            <span class="font-semibold text-brand-700">#{{ row.id }}</span>
          </template>
          <template #cell-merchant="{ row }">
            <span class="font-medium text-ink">{{ row.merchant }}</span>
          </template>
          <template #cell-subject="{ row }">
            <span class="text-ink">{{ row.subject }}</span>
          </template>
          <template #cell-status="{ row }">
            <StatusBadge kind="ticket" :status="row.status" />
          </template>
          <template #cell-createdAt="{ row }">
            <span class="text-muted">{{ formatDate(row.createdAt) }}</span>
          </template>
          <template #cell-updatedAt="{ row }">
            <span class="text-muted">{{ formatDateTime(row.updatedAt) }}</span>
          </template>
          <template #cell-assignee="{ row }">
            <div v-if="row.assignee" class="flex items-center gap-2">
              <AppAvatar :name="row.assignee.name" :size="32" shape="circle" tone="brand" />
              <span class="truncate text-[13px] text-ink">{{ row.assignee.name }}</span>
            </div>
            <span v-else class="text-[13px] text-muted">Sin asignar</span>
          </template>
          <template #cell-actions="{ row }">
            <div class="flex items-center justify-end gap-2">
              <AppButton variant="neutral" size="sm" class="min-w-14" @click="openTicket(row)">
                Ver
              </AppButton>

              <template v-if="auth.role === 'admin'">
                <AppButton
                  variant="secondary"
                  size="sm"
                  class="min-w-[128px]"
                  @click="openAssign(row)"
                >
                  {{ row.assignee ? 'Reasignar' : 'Asignar técnico' }}
                </AppButton>
              </template>

              <template v-else>
                <span
                  v-if="row.assignee?.id === auth.user?.id"
                  class="inline-flex h-9 min-w-[128px] items-center justify-center rounded-md bg-success-bg px-2 text-[12px] font-semibold text-success-text"
                >
                  Asignado a ti
                </span>
                <span
                  v-else-if="row.assignee"
                  class="inline-flex h-9 min-w-[128px] items-center justify-center px-2 text-[12px] text-muted"
                >
                  {{ row.assignee.name }}
                </span>
                <AppButton
                  v-else
                  variant="secondary"
                  size="sm"
                  class="min-w-[128px]"
                  @click="assignSelf(row)"
                >
                  Asígnamelo
                </AppButton>
              </template>

              <ActionMenu
                :items="menuItems()"
                :ariaLabel="'Más acciones del ticket'"
                bordered
                @select="
                  (key) => {
                    if (key === 'status') openTicket(row)
                    if (key === 'assign') openAssign(row)
                    if (key === 'delete') openDelete(row)
                  }
                "
              />
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

    <p class="text-[12px] leading-[1.5] text-muted">
      Solo el equipo técnico puede gestionar y eliminar tickets.
    </p>

    <DeleteTicketDialog
      :open="deleteOpen"
      :ticket-id="deleting?.id ?? ''"
      :loading="store.saving"
      @confirm="confirmDelete"
      @cancel="deleteOpen = false"
    />

    <AssignTechnicianDialog
      :open="assignOpen"
      :loading="store.saving"
      @confirm="confirmAssign"
      @cancel="assignOpen = false"
    />
  </div>
</template>
