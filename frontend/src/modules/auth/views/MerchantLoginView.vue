<script setup lang="ts">
import AuthLayout from '@/layouts/AuthLayout.vue'
import LoginForm from '@/modules/auth/components/LoginForm.vue'
</script>

<template>
  <AuthLayout portal-label="PORTAL DE COMERCIOS" footer-message="Gestiona tus cobros, sin complicaciones.">
    <LoginForm portal="comercio" />
  </AuthLayout>
</template>
