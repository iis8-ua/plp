<script setup lang="ts" generic="T extends object">
import { computed } from 'vue'

export interface DataColumn {
  key: string
  label: string
  class?: string
  headerClass?: string
  mobile?: boolean
  align?: 'left' | 'right' | 'center'
}

const props = withDefaults(
  defineProps<{
    columns: DataColumn[]
    rows: T[]
    rowKey?: string | ((row: T) => string)
    loading?: boolean
    skeletonRows?: number
  }>(),
  { rowKey: 'id', loading: false, skeletonRows: 5 },
)

function keyFor(row: T): string {
  if (typeof props.rowKey === 'function') return props.rowKey(row)
  return String((row as Record<string, unknown>)[props.rowKey])
}

function valueFor(row: T, key: string): unknown {
  return (row as Record<string, unknown>)[key]
}

const mobileColumns = computed(() => props.columns.filter((column) => column.mobile !== false))
</script>

<template>
  <div>
    <!-- Escritorio / tablet -->
    <div class="hidden overflow-x-auto md:block">
      <table class="w-full min-w-[720px] table-fixed border-collapse">
        <thead>
          <tr class="h-11 bg-app">
            <th
              v-for="column in columns"
              :key="column.key"
              scope="col"
              class="px-5 text-left text-[12px] font-semibold leading-[1.5] text-muted"
              :class="[column.headerClass, column.align === 'right' ? 'text-right' : '', column.align === 'center' ? 'text-center' : '']"
            >
              {{ column.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <template v-if="loading">
            <tr v-for="index in skeletonRows" :key="`skeleton-${index}`" class="h-[62px] border-b border-line-soft">
              <td v-for="column in columns" :key="column.key" class="px-5">
                <span class="block h-3 w-3/4 animate-pulse rounded bg-line-soft" />
              </td>
            </tr>
          </template>
          <tr
            v-for="row in rows"
            v-else
            :key="keyFor(row)"
            class="h-[62px] border-b border-line-soft transition-colors last:border-0 hover:bg-app/60"
          >
            <td
              v-for="column in columns"
              :key="column.key"
              class="px-5 align-middle text-[13px] leading-[1.5]"
              :class="[column.class, column.align === 'right' ? 'text-right' : '', column.align === 'center' ? 'text-center' : '']"
            >
              <slot :name="`cell-${column.key}`" :row="row" :value="valueFor(row, column.key)">
                {{ valueFor(row, column.key) }}
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Móvil -->
    <div class="divide-y divide-line-soft md:hidden">
      <template v-if="loading">
        <div v-for="index in skeletonRows" :key="`mobile-skeleton-${index}`" class="space-y-3 p-4">
          <span class="block h-3 w-1/2 animate-pulse rounded bg-line-soft" />
          <span class="block h-3 w-3/4 animate-pulse rounded bg-line-soft" />
        </div>
      </template>
      <div v-for="row in rows" v-else :key="keyFor(row)" class="p-4">
        <div class="grid grid-cols-2 gap-x-4 gap-y-3">
          <div
            v-for="column in mobileColumns"
            :key="column.key"
            class="min-w-0"
            :class="column.key === 'actions' ? 'col-span-2' : ''"
          >
            <p class="text-[10px] font-semibold uppercase leading-[1.5] tracking-[0.02em] text-muted">
              {{ column.label }}
            </p>
            <div class="mt-0.5 break-words text-[13px] leading-[1.5] text-ink">
              <slot :name="`cell-${column.key}`" :row="row" :value="valueFor(row, column.key)">
                {{ valueFor(row, column.key) }}
              </slot>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
