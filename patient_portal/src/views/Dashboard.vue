<template>
  <div class="max-w-7xl mx-auto px-10 py-16 animate-fade-up w-full">
    <div class="bg-white rounded-[48px] p-12 md:p-20 shadow-[0_40px_120px_-20px_rgba(0,0,0,0.08)] border border-slate-50 relative overflow-hidden">
      <!-- Decorative Background Element -->
      <div class="absolute top-0 right-0 w-96 h-96 bg-brand-orange/5 rounded-full blur-3xl -mr-48 -mt-48 text-transparent pointer-events-none">.</div>
      
      <div class="mb-16 flex items-end justify-between relative z-10">
        <div>
          <h3 class="text-5xl font-black text-slate-900 tracking-tight mb-4">Patient Dashboard</h3>
          <p class="text-slate-400 font-medium italic text-xl">Manage your health journey with precision and ease</p>
        </div>
        <div class="hidden md:flex items-center gap-4">
          <div class="bg-slate-900 p-5 rounded-[32px] shadow-xl shadow-slate-900/20 group hover:scale-105 transition-transform">
            <ActivityIcon class="w-8 h-8 text-white group-hover:rotate-12 transition-transform" />
          </div>
        </div>
      </div>
      
      <Tabs as="div" v-model="portal_tabs" :tabs="tabs" class="custom-tabs relative z-10">
        <template #tab-panel="{ tab }">
          <div class="mt-12">
            <transition name="tab-fade" mode="out-in">
              <div v-if="tab.label == 'My Appointments'" :key="'appointments'" class="animate-fade-in">
                <AppointmentModel />
              </div>
              <div v-else-if="tab.label == 'Diagnostics'" :key="'diagnostics'" class="animate-fade-in">
                <DiagnosticModel />
              </div>
              <div v-else-if="tab.label == 'Therapy'" :key="'therapy'" class="animate-fade-in">
                <TherapyModel />
              </div>
            </transition>
          </div>
        </template>
      </Tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { createResource, Tabs } from 'frappe-ui'
import AppointmentModel from '@/components/AppointmentModel.vue'
import DiagnosticModel from '@/components/DiagnosticModel.vue'
import TherapyModel from '@/components/TherapyModel.vue'
import { ActivityIcon } from 'lucide-vue-next'

const portal_tabs = ref(0)
const healthcareSettings = ref({})

// --- Resources ---
const getHealthcareSettings = createResource({
  url: "/api/method/healthcare.healthcare.api.patient_portal.get_settings",
  method: "GET",
  onSuccess(response) {
    if (response) {
      healthcareSettings.value = response
    }
  },
});
getHealthcareSettings.fetch();

// --- Computed ---
const tabs = computed(() => {
  let baseTabs = [{ label: 'My Appointments' }]
  if (healthcareSettings.value.show_diagnostics_tab) {
    baseTabs.push({ label: 'Diagnostics' })
  }
  baseTabs.push({ label: 'Therapy' })
  return baseTabs
})
</script>

<style scoped>
.custom-tabs :deep(.frappe-tab-buttons) {
  @apply flex gap-12 border-b border-slate-100 pb-0;
}
.custom-tabs :deep(.frappe-tab-button) {
  @apply text-sm font-black uppercase tracking-[0.2em] px-0 py-6 transition-all duration-300 text-slate-300 border-none relative overflow-visible;
}
.custom-tabs :deep(.frappe-tab-button-active) {
  @apply text-slate-900 border-none;
}
.custom-tabs :deep(.frappe-tab-button-active)::after {
  content: '';
  @apply absolute bottom-0 left-0 w-full h-1 bg-brand-orange rounded-full;
}

.tab-fade-enter-active,
.tab-fade-leave-active {
  transition: all 0.3s ease;
}
.tab-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.tab-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
