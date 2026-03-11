<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 py-12 md:py-24 animate-fade-up w-full">
    <div v-if="loading" class="flex flex-col items-center justify-center p-12">
      <div class="w-12 h-12 border-4 border-slate-100 border-t-brand-orange rounded-full animate-spin mb-4"></div>
      <p class="text-slate-500 font-medium">Fetching appointment details...</p>
    </div>

    <div v-else-if="error" class="bg-white rounded-3xl p-8 md:p-12 text-center shadow-sm border border-slate-100">
      <div class="w-20 h-20 bg-red-50 text-red-500 rounded-full flex items-center justify-center mx-auto mb-6">
        <XIcon class="w-10 h-10" />
      </div>
      <h2 class="text-2xl md:text-3xl font-black text-slate-900 mb-4">Unable to Load Appointment</h2>
      <p class="text-slate-500 mb-8">{{ error }}</p>
      <router-link to="/dashboard">
        <button class="bg-slate-900 text-white px-8 py-3 rounded-2xl font-bold hover:bg-slate-800 transition-all">
          Go to Dashboard
        </button>
      </router-link>
    </div>

    <div v-else-if="appointment" class="bg-white rounded-[32px] overflow-hidden shadow-[0_40px_120px_-20px_rgba(0,0,0,0.08)] border border-slate-50 relative">
      <!-- Decorative Background Elements -->
      <div class="absolute top-0 right-0 w-96 h-96 bg-brand-orange/5 rounded-full blur-3xl -mr-48 -mt-48 text-transparent pointer-events-none">.</div>
      
      <!-- Status Header -->
      <div class="p-8 md:p-12 text-center border-b border-slate-100 relative z-10" :class="isSuccess ? 'bg-green-50/50' : 'bg-orange-50/50'">
        <div 
          class="w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-6 shadow-sm"
          :class="isSuccess ? 'bg-green-100 text-green-600' : 'bg-orange-100 text-orange-600'"
        >
          <CheckIcon v-if="isSuccess" class="w-12 h-12" />
          <ClockIcon v-else class="w-12 h-12" />
        </div>
        
        <h1 class="text-3xl md:text-4xl font-black tracking-tight mb-3" :class="isSuccess ? 'text-green-900' : 'text-orange-900'">
          {{ isSuccess ? 'Booking Confirmed!' : 'Booking Pending' }}
        </h1>
        <p class="text-base md:text-lg" :class="isSuccess ? 'text-green-700/80' : 'text-orange-700/80'">
          {{ isSuccess 
              ? 'Your appointment has been successfully booked and paid.' 
              : 'Your appointment is booked. Payment is marked as Pay Later.' 
          }}
        </p>
      </div>

      <!-- Appointment Details -->
      <div class="p-8 md:p-12 relative z-10">
        <div class="flex items-center justify-between mb-8">
          <div>
            <p class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">Reference No.</p>
            <p class="text-sm font-bold text-slate-900"># {{ appointment.name }}</p>
          </div>
          <Badge
            variant="subtle"
            size="lg"
            class="rounded-xl px-4 py-1.5 text-xs font-black uppercase tracking-widest text-slate-900"
            :theme="getStatusColor(appointment.status)">
            {{ appointment.status }}
          </Badge>
        </div>

        <div class="bg-slate-50 rounded-3xl p-6 md:p-8 space-y-6 border border-slate-100">
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-white shadow-sm flex items-center justify-center shrink-0">
              <CalendarIcon class="w-5 h-5 text-slate-400" />
            </div>
            <div>
              <p class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">Date & Time</p>
              <p class="text-base font-bold text-slate-900">{{ formatDate(appointment.appointment_date) }}</p>
              <p class="text-sm font-medium text-slate-500">{{ formatTime(appointment.appointment_time) }}</p>
            </div>
          </div>

          <div class="h-px w-full bg-slate-200/60"></div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="flex items-start gap-4">
              <div v-if="appointment.patient_image" class="w-10 h-10 rounded-xl overflow-hidden shadow-sm shrink-0">
                <img :src="appointment.patient_image" class="w-full h-full object-cover" />
              </div>
              <div v-else class="w-10 h-10 rounded-xl bg-brand-orange/10 flex items-center justify-center text-brand-orange font-bold shrink-0">
                {{ appointment.patient_name?.charAt(0) }}
              </div>
              <div>
                <p class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">Patient</p>
                <p class="text-sm font-bold text-slate-900">{{ appointment.patient_name }}</p>
              </div>
            </div>

            <div class="flex items-start gap-4">
              <div v-if="appointment.practitioner_image" class="w-10 h-10 rounded-xl overflow-hidden shadow-sm shrink-0">
                <img :src="appointment.practitioner_image" class="w-full h-full object-cover" />
              </div>
              <div v-else class="w-10 h-10 rounded-xl bg-slate-900 text-white flex items-center justify-center font-bold shrink-0">
                {{ appointment.practitioner_name?.charAt(0) }}
              </div>
              <div>
                <p class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">Practitioner</p>
                <p class="text-sm font-bold text-slate-900">{{ appointment.practitioner_name }}</p>
              </div>
            </div>
          </div>
          
          <div class="h-px w-full bg-slate-200/60"></div>
          
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-white shadow-sm flex items-center justify-center text-slate-400 font-bold">$</div>
              <div>
                <p class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">Consultation Fee</p>
                <p class="text-lg font-black text-slate-900">
                  <template v-if="appointment.consultation_charge > 0">
                    {{ formatCurrency(appointment.consultation_charge, appointment.default_currency) }}
                  </template>
                  <template v-else>—</template>
                </p>
              </div>
            </div>
            <Badge :variant="'subtle'" :theme="appointment.invoiced == 1 ? 'green' : 'orange'">
              {{ appointment.invoiced ? 'Paid' : 'Unpaid' }}
            </Badge>
          </div>
        </div>

        <!-- Actions -->
        <div class="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
          <router-link to="/dashboard">
            <button class="w-full sm:w-auto px-8 py-3.5 rounded-2xl font-bold bg-slate-900 text-white hover:bg-slate-800 transition-all flex items-center justify-center gap-2">
              View All Appointments
            </button>
          </router-link>
          <router-link to="/">
            <button class="w-full sm:w-auto px-8 py-3.5 rounded-2xl font-bold bg-slate-100 text-slate-600 hover:bg-slate-200 transition-all flex items-center justify-center gap-2">
              Back to Home
            </button>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { createResource, Badge } from 'frappe-ui'
import { CheckIcon, XIcon, ClockIcon, CalendarIcon } from 'lucide-vue-next'
import dayjs from 'dayjs'

const route = useRoute()
const appointmentId = route.params.id

const appointment = ref(null)
const loading = ref(true)
const error = ref(null)

const isSuccess = computed(() => {
  if (!appointment.value) return false
  if (appointment.value.status === 'Cancelled') return false
  return appointment.value.invoiced === 1 || appointment.value.paid_amount > 0
})

const fetchAppointment = createResource({
  url: 'healthcare.healthcare.api.patient_portal.get_appointment_by_id',
  makeParams() {
    return {
      appointment_id: appointmentId
    }
  },
  onSuccess(data) {
    if (data) {
      appointment.value = data
    } else {
      error.value = "Appointment not found or you don't have permission to view it."
    }
    loading.value = false
  },
  onError(err) {
    error.value = err.messages?.[0] || 'Failed to fetch appointment details.'
    loading.value = false
  }
})

onMounted(() => {
  if (appointmentId) {
    fetchAppointment.fetch()
  } else {
    error.value = "No appointment ID provided."
    loading.value = false
  }
})

// Format helpers
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return dayjs(dateStr).format('ddd, MMM D, YYYY')
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  return dayjs(`2000-01-01 ${timeStr}`).format('h:mm A')
}

const formatCurrency = (amount, currency = 'USD') => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: currency,
    maximumFractionDigits: 0
  }).format(amount)
}

const getStatusColor = (status) => {
  switch (status) {
    case "Confirmed": return "green"
    case "Open":
    case "Scheduled": return "blue"
    case "Cancelled": return "red"
    case "Checked In": return "purple"
    case "Checked Out": return "gray"
    default: return "gray"
  }
}
</script>
