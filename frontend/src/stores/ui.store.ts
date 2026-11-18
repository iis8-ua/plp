import { ref } from 'vue'
import { defineStore } from 'pinia'

export type ToastType = 'success' | 'error'

export interface Toast {
  id: number
  type: ToastType
  message: string
}

let toastId = 0

export const useUiStore = defineStore('ui', () => {
  const toasts = ref<Toast[]>([])
  const sidebarOpen = ref(false)

  function pushToast(type: ToastType, message: string, duration = 4200): void {
    const id = ++toastId
    toasts.value.push({ id, type, message })
    window.setTimeout(() => dismissToast(id), duration)
  }

  function dismissToast(id: number): void {
    toasts.value = toasts.value.filter((toast) => toast.id !== id)
  }

  function openSidebar(): void {
    sidebarOpen.value = true
  }

  function closeSidebar(): void {
    sidebarOpen.value = false
  }

  return { toasts, sidebarOpen, pushToast, dismissToast, openSidebar, closeSidebar }
})
