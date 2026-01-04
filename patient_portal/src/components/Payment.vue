<template>
  <div class="h-full flex flex-col justify-center animate-fade-in relative px-4">
    <!-- Receipt Container -->
    <div class="bg-white rounded-[40px] shadow-2xl shadow-slate-200/50 border border-slate-100 overflow-hidden w-full max-w-md mx-auto">
      <!-- Receipt Header -->
      <div class="bg-slate-900 px-10 py-12 text-center relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-1 bg-brand-orange"></div>
        <div class="p-4 bg-white/10 rounded-2xl inline-block mb-6 backdrop-blur-md">
          <CreditCardIcon class="w-8 h-8 text-white" />
        </div>
        <h2 class="text-2xl font-black text-white tracking-tight mb-2 uppercase">Payment Summary</h2>
        <p class="text-[10px] font-black text-white/40 uppercase tracking-[0.3em]">Official Receipt</p>
      </div>

      <!-- Receipt Body -->
      <div class="px-10 py-10 relative">
        <!-- Decorative Side Notches -->
        <div class="absolute -left-3 top-0 bottom-0 flex flex-col justify-around py-4 opacity-10">
          <div v-for="i in 12" :key="i" class="w-6 h-6 rounded-full bg-slate-200"></div>
        </div>
        <div class="absolute -right-3 top-0 bottom-0 flex flex-col justify-around py-4 opacity-10">
          <div v-for="i in 12" :key="i" class="w-6 h-6 rounded-full bg-slate-200"></div>
        </div>

        <!-- Line Items -->
        <div class="space-y-8 relative z-10">
          <div class="flex flex-col gap-1 text-center bg-slate-50 p-6 rounded-3xl border border-slate-100 mb-8">
            <span class="text-[10px] font-black text-slate-300 uppercase tracking-widest">Consulting Specialist</span>
            <span class="text-lg font-black text-slate-900">{{ practitioner }}</span>
          </div>

          <div class="flex items-center justify-between">
            <div class="flex flex-col gap-1">
              <span class="text-[10px] font-black text-slate-300 uppercase tracking-widest leading-none">Consultation Fee</span>
              <span class="text-xs font-bold text-slate-400">Fixed rate charge</span>
            </div>
            <span class="text-lg font-black text-slate-900">{{ formatCurrency(consultationFee, currency) }}</span>
          </div>

          <div v-if="registrationFee > 0" class="flex items-center justify-between">
            <div class="flex flex-col gap-1">
              <span class="text-[10px] font-black text-slate-300 uppercase tracking-widest leading-none">Registration</span>
              <span class="text-xs font-bold text-slate-400">One-time processing</span>
            </div>
            <span class="text-lg font-black text-slate-900">{{ formatCurrency(registrationFee, currency) }}</span>
          </div>

          <!-- Dotted Divider -->
          <div class="border-t-2 border-dashed border-slate-100 my-8"></div>

          <!-- Total -->
          <div class="flex items-end justify-between">
            <div class="flex flex-col gap-1">
              <span class="text-[11px] font-black text-brand-orange uppercase tracking-[0.2em] leading-none">Final Amount</span>
              <span class="text-xs font-bold text-slate-300 italic">Taxes Included</span>
            </div>
            <div class="text-4xl font-black text-slate-900 tracking-tighter drop-shadow-sm">
              {{ formatCurrency(totalAmount, currency) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Background Decoration -->
    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] bg-brand-orange/5 blur-[120px] rounded-full -z-10 pointer-events-none"></div>

    <ErrorMessage v-if="error" class="mt-8 max-w-md mx-auto" :message="error" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ErrorMessage } from 'frappe-ui'
import { formatCurrency } from "@/utils/formatters"
import { CreditCardIcon } from 'lucide-vue-next'

const practitioner = defineModel('practitioner')
const consultationFee = defineModel('consultationFee')
const registrationFee = defineModel('registrationFee')
const error = defineModel('error')
const currency = defineModel('currency')

const totalAmount = computed(() => {
	return (consultationFee.value || 0) + (registrationFee.value || 0)
})
</script>
