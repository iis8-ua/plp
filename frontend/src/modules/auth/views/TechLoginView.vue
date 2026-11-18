<script setup lang="ts">
import AuthLayout from '@/layouts/AuthLayout.vue'
import LoginForm from '@/modules/auth/components/LoginForm.vue'
</script>

<template>
  <AuthLayout portal-label="PORTAL DE SOPORTE" footer-message="Soporte de pagos, sin complicaciones.">
    <LoginForm portal="tecnico" />
  </AuthLayout>
</template>
