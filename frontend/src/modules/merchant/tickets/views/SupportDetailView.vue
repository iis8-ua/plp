<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSupportStore } from '@/stores/support.store'
import { useUiStore } from '@/stores/ui.store'
import AppBreadcrumbs from '@/shared/components/layout/AppBreadcrumbs.vue'
import Timeline from '@/shared/components/data/Timeline.vue'
import AppButton from '@/shared/components/ui/AppButton.vue'
import AppTextarea from '@/shared/components/ui/AppTextarea.vue'
import PageErrorState from '@/shared/components/ui/PageErrorState.vue'
import StatusBadge from '@/shared/components/ui/StatusBadge.vue'
import { formatFullDateTime } from '@/shared/utils/format'

const route = useRoute()
const router = useRouter()
const store = useSupportStore()
const ui = useUiStore()

const ticketId = computed(() => String(route.params.id ?? ''))
const ticket = computed(() => store.getById(ticketId.value))
const comment = ref('')

async function sendComment(): Promise<void> {
  if (!ticket.value || !comment.value.trim()) return
  try {
    await store.comment(ticket.value.id, comment.value.trim())
    comment.value = ''
    ui.pushToast('success', 'Comentario enviado')
  } catch (cause) {
    ui.pushToast('error', cause instanceof Error ? cause.message : 'No se pudo enviar el comentario.')
  }
}

onMounted(() => {
  void store.load()
})
</script>

<template>
  <div class="space-y-6">
    <div v-if="store.loading && !ticket" class="space-y-4">
      <div class="h-4 w-40 animate-pulse rounded bg-line-soft" />
      <div class="h-72 animate-pulse rounded-lg bg-line-soft" />
    </div>

    <PageErrorState
      v-else-if="!ticket"
      title="Ticket no encontrado"
      description="No hemos podido localizar este ticket o ya no está disponible."
      action-label="Volver a soporte"
      @action="router.push('/comercio/tickets')"
    />

    <template v-else>
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <AppBreadcrumbs
          :items="[{ label: 'Soporte', to: '/comercio/tickets' }, { label: `Ticket #${ticket.id}` }]"
          separator=">"
        />
        <AppButton to="/comercio/tickets" variant="secondary" class="min-w-[212px]">
          Volver a soporte
        </AppButton>
      </div>

      <div>
        <h1 class="text-[28px] font-semibold leading-[1.5] text-ink lg:text-[32px]">
          Ticket #{{ ticket.id }}
        </h1>
      </div>

      <div class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_392px]">
        <div class="space-y-6">
          <section class="rounded-lg border border-line bg-white p-6">
            <div class="flex flex-wrap items-start justify-between gap-3">
              <h2 class="text-[22px] font-semibold leading-[1.5] text-ink">{{ ticket.subject }}</h2>
              <StatusBadge kind="ticket" :status="ticket.status" size="md" />
            </div>
            <p class="mt-1 text-[13px] leading-[1.5] text-muted">
              Creado el {{ formatFullDateTime(ticket.createdAt) }}
            </p>

            <div class="mt-5 border-t border-line pt-5">
              <p class="text-[14px] font-semibold leading-[1.5] text-ink">Descripción</p>
              <p class="mt-2 text-[14px] leading-[1.5] text-secondary">{{ ticket.description }}</p>
            </div>
          </section>

          <section class="rounded-lg border border-line bg-white p-6">
            <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Conversación</h2>

            <div v-if="ticket.messages.length === 0" class="mt-4 text-[14px] leading-[1.5] text-muted">
              Todavía no hay mensajes en este ticket.
            </div>

            <div v-else class="mt-4 space-y-3">
              <article
                v-for="message in ticket.messages"
                :key="message.id"
                class="rounded-md border border-line px-4 py-3"
                :class="message.role === 'tecnico' ? 'bg-app' : 'bg-white'"
              >
                <div class="flex flex-wrap items-start justify-between gap-2">
                  <p class="text-[12px] font-semibold leading-[1.5] text-brand-700">
                    {{ message.author }}
                    <span class="font-normal text-muted">
                      · {{ message.role === 'tecnico' ? 'Técnica de soporte' : 'Tú' }}
                    </span>
                  </p>
                  <p class="text-[12px] leading-[1.5] text-muted">
                    {{ formatFullDateTime(message.createdAt) }}
                  </p>
                </div>
                <p class="mt-1 text-[14px] leading-[1.5] text-ink">{{ message.message }}</p>
              </article>
            </div>
          </section>

          <section class="rounded-lg border border-line bg-white p-6">
            <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Añadir comentario</h2>
            <div class="mt-4">
              <AppTextarea
                v-model="comment"
                placeholder="Escribe un comentario"
                :rows="3"
                aria-label="Comentario del ticket"
              />
            </div>
            <div class="mt-3 flex justify-end">
              <AppButton
                class="min-w-[156px]"
                :loading="store.saving"
                :disabled="!comment.trim()"
                @click="sendComment"
              >
                Enviar
              </AppButton>
            </div>
          </section>
        </div>

        <aside class="h-fit rounded-lg border border-line bg-white p-6">
          <h2 class="text-[18px] font-semibold leading-[1.5] text-ink">Historial</h2>
          <div class="mt-5">
            <Timeline :entries="ticket.history" />
          </div>
        </aside>
      </div>
    </template>
  </div>
</template>
