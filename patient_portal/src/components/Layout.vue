<template>
  <div class="min-h-screen flex flex-col bg-slate-50 selection:bg-brand-orange/10">
    <!-- Header -->
    <header class="glass-morphism sticky top-0 z-50 px-6 py-4 flex items-center justify-between transition-all duration-300 w-full">
      <div class="flex items-center gap-10">
        <router-link to="/" class="flex items-center gap-2.5 group cursor-pointer">
          <div class="w-10 h-10 bg-navy rounded-2xl flex items-center justify-center shadow-lg shadow-navy/20 group-hover:scale-110 transition-transform duration-500">
            <ActivityIcon class="w-6 h-6 text-white" />
          </div>
          <h1 class="text-2xl font-black text-navy tracking-tight">Med<span class="text-brand-orange">Connect</span></h1>
        </router-link>
        
        <nav class="hidden lg:flex items-center gap-8 text-[15px] font-semibold text-slate-500">
          <router-link to="/" class="hover:text-navy transition-colors relative group" active-class="text-navy">
            Find Doctors
            <span class="absolute -bottom-1 left-0 w-0 h-0.5 bg-brand-orange transition-all group-hover:w-full"></span>
          </router-link>
          <router-link to="/dashboard" class="hover:text-navy transition-colors relative group" active-class="text-navy">
            Dashboard
            <span class="absolute -bottom-1 left-0 w-0 h-0.5 bg-brand-orange transition-all group-hover:w-full"></span>
          </router-link>
          <a href="#" class="hover:text-navy transition-colors relative group">
            Lab Tests
            <span class="absolute -bottom-1 left-0 w-0 h-0.5 bg-brand-orange transition-all group-hover:w-full"></span>
          </a>
        </nav>
      </div>

      <div class="flex items-center gap-5">
        <Button
          v-if="!isGuest && !patient"
          variant="outline"
          class="!rounded-2xl !px-6 !border-slate-200 hover:!bg-slate-50 transition-all font-semibold"
          @click="goToRegistration"
        >
          Register as Patient
        </Button>

        <Dropdown
          v-if="!isGuest"
          :options="userMenuOptions"
        >
          <template #target>
            <div class="flex items-center gap-3 cursor-pointer group p-1 pr-3 rounded-2xl hover:bg-slate-50 transition-all">
              <Avatar
                :image="userInfo.image"
                :label="userInfo.full_name"
                size="md"
                class="ring-2 ring-slate-100 group-hover:ring-brand-orange/30 transition-all"
              />
              <div class="text-left hidden sm:block">
                <p class="text-sm font-bold text-navy leading-none">{{ userInfo.full_name }}</p>
                <p class="text-[11px] font-medium text-slate-400 mt-1">{{ userInfo.email }}</p>
              </div>
            </div>
          </template>
        </Dropdown>

        <Button
          v-if="isGuest"
          variant="solid"
          class="!rounded-2xl !px-8 !bg-navy hover:!bg-navy-light transition-all shadow-lg shadow-navy/10 font-bold"
          @click="goToLogin"
        >
          Login
        </Button>
      </div>
    </header>

    <!-- Page Content -->
    <main class="flex-1 w-full">
      <slot></slot>
    </main>

    <!-- Footer -->
    <footer class="py-12 px-6 border-t border-slate-100 bg-white w-full">
      <div class="mx-auto flex flex-col md:flex-row justify-between items-center gap-8 w-full px-4">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 bg-navy rounded-xl flex items-center justify-center">
            <ActivityIcon class="w-5 h-5 text-white" />
          </div>
          <h1 class="text-xl font-black text-navy tracking-tight">MedConnect</h1>
        </div>
        <p class="text-slate-400 text-sm font-medium">© 2026 MedConnect Healthcare Portal. All rights reserved.</p>
        <div class="flex gap-6 text-slate-400">
          <a href="#" class="hover:text-navy transition-colors">Privacy</a>
          <a href="#" class="hover:text-navy transition-colors">Terms</a>
          <a href="#" class="hover:text-navy transition-colors">Support</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ActivityIcon } from 'lucide-vue-next'
import { Button, Avatar, Dropdown } from 'frappe-ui'

const props = defineProps({
  userInfo: { type: Object, default: () => ({}) },
  isGuest: { type: Boolean, default: true },
  patient: { type: Object, default: null }
})

const userMenuOptions = [
  {
    label: 'Logout',
    onClick: () => {
      window.location.href = '/api/method/logout';
    },
    icon: 'log-out'
  }
]

const goToLogin = () => {
  window.location.href = `/login?redirect-to=${window.location.pathname}`;
}

const goToRegistration = () => {
  window.location.href = '/patient-registration';
}
</script>
