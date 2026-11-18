import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { UserProfile } from '@/types'
import { changePassword, fetchProfile, updateProfile } from '@/services/profile.service'

export const useProfileStore = defineStore('profile', () => {
  const profile = ref<UserProfile | null>(null)
  const loading = ref(false)
  const saving = ref(false)
  const error = ref('')
  const loaded = ref(false)

  async function load(force = false): Promise<void> {
    if (loaded.value && !force) return
    loading.value = true
    error.value = ''
    try {
      profile.value = await fetchProfile()
      loaded.value = true
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'No se pudo cargar el perfil.'
    } finally {
      loading.value = false
    }
  }

  async function save(payload: Record<string, string>): Promise<UserProfile> {
    saving.value = true
    error.value = ''
    try {
      profile.value = await updateProfile(payload)
      return profile.value
    } finally {
      saving.value = false
    }
  }

  async function updatePassword(currentPassword: string, newPassword: string): Promise<void> {
    saving.value = true
    error.value = ''
    try {
      await changePassword(currentPassword, newPassword)
    } finally {
      saving.value = false
    }
  }

  return { profile, loading, saving, error, loaded, load, save, updatePassword }
})
