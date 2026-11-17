<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppBreadcrumbs from '@/shared/components/layout/AppBreadcrumbs.vue'
import Timeline from '@/shared/components/data/Timeline.vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppIcon from '@/shared/components/ui/AppIcon.vue'
import AppTextarea from '@/shared/components/ui/AppTextarea.vue'
import InlineAlert from '@/shared/components/ui/InlineAlert.vue'
import PageErrorState from '@/shared/components/ui/PageErrorState.vue'
import StatusBadge from '@/shared/components/ui/StatusBadge.vue'
import DeleteTicketDialog from '@/modules/tech/tickets/components/DeleteTicketDialog.vue'
import TicketStatusSelect from '@/modules/tech/tickets/components/TicketStatusSelect.vue'
import { useTicketsStore } from '@/stores/tickets.store'
import { useAuthStore } from '@/stores/auth.store'
import { useUiStore } from '@/stores/ui.store'
import { formatFullDateTime } from '@/shared/utils/format'
import type { TicketStatus } from '@/types'

const route = useRoute()
const router = useRouter()
const store = useTicketsStore()
const auth = useAuthStore()
const ui = useUiStore()

const ticketId = computed(() => String(route.params.id ?? ''))
const ticket = computed(() => store.getById(ticketId.value))
const status = ref<TicketStatus>('abierto')
const reply = ref('')
const replySaved = ref(false)
const saveError = ref('')
const deleteOpen = ref(false)

const dirty = computed(
  () => Boolean(ticket.value) && (status.value !== ticket.value?.status || reply.value !== ticket.value?.reply),
)

const replyHint = computed(() => {
  if (replySaved.value) return 'Tu respuesta se ha añadido al historial del ticket.'
  if (reply.value.trim()) return 'Respuesta lista para enviar'
  return 'Añade contexto sobre la revisión o la solución de la incidencia.'
})

const reversedHistory = computed(() => [...(ticket.value?.history ?? [])].reverse())

watch(
  ticket,
  (value) => {
    if (!value) return
    status.value = value.status
    reply.value = value.reply
  },
  { immediate: true },
)

async function save(): Promise<void> {
  if (!ticket.value || !dirty.value) return
  saveError.value = ''
  const hadReply = reply.value.trim().length > 0
  try {
    await store.saveTicket(ticket.value.id, status.value, reply.value)
    reply.value = ''
    replySaved.value = hadReply
    ui.pushToast('success', 'Ticket actualizado correctamente')
  } catch (cause) {
    saveError.value =
      cause instanceof Error ? cause.message : 'No se ha podido completar la acción. Inténtalo de nuevo.'
  }
}

function cancel(): void {
  if (!ticket.value) return
  status.value = ticket.value.status
  reply.value = ticket.value.reply
  replySaved.value = false
  saveError.value = ''
}

async function confirmDelete(): Promise<void> {
  if (!ticket.value) return
  try {
    await store.removeTicket(ticket.value.id)
    deleteOpen.value = false
    await router.push('/tecnico/tickets')
  } catch (cause) {
    ui.pushToast('error', cause instanceof Error ? cause.message : 'No se pudo eliminar el ticket.')
  }
}

onMounted(async () => {
  await store.load()
})
</script>

<template>
  <div v-if="store.loading && !ticket" class="space-y-4">
    <div class="h-5 w-40 animate-pulse rounded bg-line-soft" />
    <div class="h-10 w-72 animate-pulse rounded bg-line-soft" />
    <div class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_392px]">
      <div class="h-80 animate-pulse rounded-lg bg-line-soft" />
      <div class="h-80 animate-pulse rounded-lg bg-line-soft" />
    </div>
  </div>

  <PageErrorState
    v-else-if="!ticket"
    title="Ticket no encontrado"
    description="Puede que se haya eliminado o que el enlace ya no esté disponible."
    action-label="Volver a la bandeja"
    @action="router.push('/tecnico/tickets')"
  />

  <div v-else class="space-y-6">
    <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
      <div class="min-w-0">
        <AppBreadcrumbs :items="[{ label: 'Tickets', to: '/tecnico/tickets' }, { label: `#${ticket.id}` }]" />
        <h1 class="mt-3 text-[26px] font-semibold leading-[1.5] text-ink">Ticket #{{ ticket.id }}</h1>
        <p class="mt-0.5 text-[14px] leading-[1.5] text-muted">
          Revisa la incidencia y mantén al comercio informado.
        </p>
      </div>
      <AppButton to="/tecnico/tickets" variant="secondary" class="min-w-[212px]">
        <AppIcon name="arrow-left" :size="18" /> Volver a la bandeja
      </AppButton>
    </div>

    <InlineAlert v-if="saveError" tone="error" class="max-w-[584px] lg:ml-auto" @dismiss="saveError = ''">
      {{ saveError }}
    </InlineAlert>

    <div class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_392px]">
      <div class="space-y-6">
        <section class="rounded-lg border border-line bg-white p-6">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <h2 class="text-[22px] font-semibold leading-[1.5] text-ink">{{ ticket.subject }}</h2>
            <StatusBadge kind="ticket" :status="ticket.status" />
          </div>

          <div class="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2">
            <div>
              <p class="plp-micro">COMERCIO</p>
              <p class="mt-1 text-[14px] font-medium text-ink">{{ ticket.merchant }}</p>
            </div>
            <div>
              <p class="plp-micro">FECHA DE APERTURA</p>
              <p class="mt-1 text-[14px] font-medium text-ink">{{ formatFullDateTime(ticket.openedAt) }}</p>
            </div>
          </div>

          <div class="my-6 h-px bg-line" />

          <h3 class="text-[18px] font-semibold leading-[1.5] text-ink">Descripción de la incidencia</h3>
          <div class="mt-3 space-y-4 text-[14px] leading-[1.5] text-secondary">
            <p>{{ ticket.description }}</p>
            <p v-if="ticket.id === '1042'">
              Ocurre con Visa y Mastercard. Hemos probado en distintos navegadores y el error persiste.
              Referencia de la operación: PLP-88214.
            </p>
          </div>
        </section>

        <section class="rounded-lg border border-line bg-white p-6">
          <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Respuesta al comercio</h2>
          <p class="mt-1 text-[12px] leading-[1.5] text-muted">
            El comercio verá este mensaje en su ticket de soporte.
          </p>

          <div class="mt-5">
            <AppTextarea
              v-model="reply"
              :rows="5"
              placeholder="Escribe una respuesta para el comercio…"
              :hint="replyHint"
              @update:model-value="replySaved = false"
            />
          </div>
        </section>
      </div>

      <div class="space-y-6">
        <section class="rounded-lg border border-line bg-white p-6">
          <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Gestión</h2>
          <p class="mt-4 text-[14px] font-medium leading-[1.5] text-ink">Estado del ticket</p>
          <div class="mt-2">
            <TicketStatusSelect v-model="status" />
          </div>
          <div class="mt-5 space-y-3">
            <AppButton block :loading="store.saving" @click="save">Guardar cambios</AppButton>
            <AppButton variant="secondary" block @click="cancel">Cancelar</AppButton>
          </div>
          <p v-if="dirty" class="mt-3 text-[12px] leading-[1.5] text-muted">Cambios sin guardar</p>
        </section>

        <section class="rounded-lg border border-line bg-white p-6">
          <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Historial de cambios</h2>
          <div class="mt-5">
            <Timeline :entries="reversedHistory" />
          </div>
        </section>

        <div v-if="auth.role === 'admin'">
          <AppButton variant="danger" block @click="deleteOpen = true">Eliminar ticket</AppButton>
          <p class="mt-2 text-center text-[12px] leading-[1.5] text-muted">Esta acción es permanente.</p>
        </div>
      </div>
    </div>

    <DeleteTicketDialog
      :open="deleteOpen"
      :ticket-id="ticket.id"
      :loading="store.saving"
      @confirm="confirmDelete"
      @cancel="deleteOpen = false"
    />
  </div>
</template>
