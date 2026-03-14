<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 py-12 md:py-24 animate-fade-up w-full">
    <!-- Loading -->
    <div v-if="loading" class="flex flex-col items-center justify-center p-12">
      <div class="w-12 h-12 border-4 border-slate-100 border-t-brand-orange rounded-full animate-spin mb-4"></div>
      <p class="text-slate-500 font-medium">Fetching appointment details...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-white rounded-3xl p-8 md:p-12 text-center shadow-sm border border-slate-100">
      <div class="w-20 h-20 bg-red-50 text-red-500 rounded-full flex items-center justify-center mx-auto mb-6">
        <XCircleIcon class="w-10 h-10" />
      </div>
      <h2 class="text-2xl md:text-3xl font-black text-slate-900 mb-4">Unable to Load Appointment</h2>
      <p class="text-slate-500 mb-8">{{ error }}</p>
      <router-link to="/dashboard">
        <button class="bg-slate-900 text-white px-8 py-3 rounded-2xl font-bold hover:bg-slate-800 transition-all">
          Go to Dashboard
        </button>
      </router-link>
    </div>

    <!-- Main Content -->
    <div v-else-if="appointment" class="space-y-6">
      <!-- Status Card -->
      <div class="bg-white rounded-[32px] overflow-hidden shadow-[0_40px_120px_-20px_rgba(0,0,0,0.08)] border border-slate-50 relative">
        <div class="absolute top-0 right-0 w-96 h-96 rounded-full blur-3xl -mr-48 -mt-48 text-transparent pointer-events-none"
          :class="statusConfig.bgBlur">.</div>
        
        <!-- Status Header -->
        <div class="p-8 md:p-12 text-center border-b border-slate-100 relative z-10" :class="statusConfig.headerBg">
          <div class="w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-6 shadow-sm"
            :class="statusConfig.iconBg">
            <component :is="statusConfig.icon" class="w-12 h-12" />
          </div>
          
          <h1 class="text-3xl md:text-4xl font-black tracking-tight mb-3" :class="statusConfig.titleColor">
            {{ statusConfig.title }}
          </h1>
          <p class="text-base md:text-lg max-w-md mx-auto" :class="statusConfig.subtitleColor">
            {{ statusConfig.subtitle }}
          </p>

          <!-- Failure Reason -->
          <div v-if="paymentState === 'failed' && appointment.payment_failure_reason"
            class="mt-6 mx-auto max-w-md bg-red-100/60 border border-red-200 rounded-2xl px-5 py-3 text-sm text-red-700 font-medium">
            <span class="font-black">Reason:</span> {{ appointment.payment_failure_reason }}
          </div>
        </div>

        <!-- Appointment Details -->
        <div class="p-8 md:p-12 relative z-10">
          <div class="flex items-center justify-between mb-8">
            <div>
              <p class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">Reference No.</p>
              <p class="text-sm font-bold text-slate-900"># {{ appointment.name }}</p>
            </div>
            <Badge variant="subtle" size="lg"
              class="rounded-xl px-4 py-1.5 text-xs font-black uppercase tracking-widest text-slate-900"
              :theme="getStatusColor(appointment.status)">
              {{ appointment.status }}
            </Badge>
          </div>

          <div class="bg-slate-50 rounded-3xl p-6 md:p-8 space-y-6 border border-slate-100">
            <!-- Date & Time -->
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

            <!-- Patient & Practitioner -->
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
            
            <!-- Fee & Payment Status -->
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-white shadow-sm flex items-center justify-center text-slate-400 font-bold">
                  <BanknoteIcon class="w-5 h-5" />
                </div>
                <div>
                  <p class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">Consultation Fee</p>
                  <p class="text-lg font-black text-slate-900">
                    <template v-if="displayFee > 0">
                      {{ formatCurrency(displayFee, appointment.default_currency) }}
                    </template>
                    <template v-else>—</template>
                  </p>
                </div>
              </div>
              <Badge :variant="'subtle'" :theme="paymentBadgeTheme">
                {{ paymentBadgeLabel }}
              </Badge>
            </div>

            <!-- Transaction ID if available -->
            <div v-if="appointment.payment_id" class="flex items-center gap-3 pt-2">
              <div class="w-10 h-10 rounded-xl bg-white shadow-sm flex items-center justify-center shrink-0">
                <HashIcon class="w-5 h-5 text-slate-400" />
              </div>
              <div>
                <p class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">Transaction ID</p>
                <p class="text-sm font-bold text-slate-900 font-mono">{{ appointment.payment_id }}</p>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
            <button v-if="paymentState === 'success'" @click="printInvoice"
              class="w-full sm:w-auto px-8 py-3.5 rounded-2xl font-bold bg-brand-orange text-white hover:bg-brand-orange/90 transition-all flex items-center justify-center gap-2 shadow-lg shadow-brand-orange/20">
              <DownloadIcon class="w-4 h-4" />
              Download Invoice
            </button>
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

      <!-- Printable Invoice (hidden, used for PDF generation) -->
      <div id="invoice-print-area" class="hidden">
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 700px; margin: 0 auto; padding: 40px; color: #1e293b;">
          <!-- Invoice Header -->
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 40px; border-bottom: 3px solid #f1f5f9; padding-bottom: 30px;">
            <div>
              <h1 style="font-size: 28px; font-weight: 900; margin: 0 0 4px 0; color: #0f172a;">INVOICE</h1>
              <p style="font-size: 13px; color: #94a3b8; margin: 0; font-weight: 600; letter-spacing: 1px;">APPOINTMENT RECEIPT</p>
            </div>
            <div style="text-align: right;">
              <p style="font-size: 12px; color: #94a3b8; margin: 0 0 4px 0; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">Reference</p>
              <p style="font-size: 16px; font-weight: 800; color: #0f172a; margin: 0;"># {{ appointment.name }}</p>
              <p style="font-size: 12px; color: #64748b; margin: 6px 0 0 0;">{{ formatDate(appointment.appointment_date) }}</p>
            </div>
          </div>

          <!-- Status Banner -->
          <div :style="`background: ${paymentState === 'success' ? '#f0fdf4' : paymentState === 'failed' ? '#fef2f2' : '#fffbeb'}; border: 1px solid ${paymentState === 'success' ? '#bbf7d0' : paymentState === 'failed' ? '#fecaca' : '#fde68a'}; border-radius: 12px; padding: 14px 20px; margin-bottom: 30px; text-align: center;`">
            <p :style="`margin: 0; font-weight: 800; font-size: 14px; color: ${paymentState === 'success' ? '#166534' : paymentState === 'failed' ? '#991b1b' : '#92400e'};`">
              {{ paymentState === 'success' ? '✓ PAYMENT SUCCESSFUL' : paymentState === 'failed' ? '✗ PAYMENT FAILED' : '⏳ PAYMENT PENDING' }}
            </p>
          </div>

          <!-- Details Table -->
          <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
            <tr style="border-bottom: 1px solid #f1f5f9;">
              <td style="padding: 14px 0; font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; width: 40%;">Patient</td>
              <td style="padding: 14px 0; font-size: 14px; font-weight: 700; color: #0f172a;">{{ appointment.patient_name }}</td>
            </tr>
            <tr style="border-bottom: 1px solid #f1f5f9;">
              <td style="padding: 14px 0; font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">Practitioner</td>
              <td style="padding: 14px 0; font-size: 14px; font-weight: 700; color: #0f172a;">{{ appointment.practitioner_name }}</td>
            </tr>
            <tr style="border-bottom: 1px solid #f1f5f9;">
              <td style="padding: 14px 0; font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">Appointment Date</td>
              <td style="padding: 14px 0; font-size: 14px; font-weight: 700; color: #0f172a;">{{ formatDate(appointment.appointment_date) }}</td>
            </tr>
            <tr style="border-bottom: 1px solid #f1f5f9;">
              <td style="padding: 14px 0; font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">Appointment Time</td>
              <td style="padding: 14px 0; font-size: 14px; font-weight: 700; color: #0f172a;">{{ formatTime(appointment.appointment_time) }}</td>
            </tr>
            <tr style="border-bottom: 1px solid #f1f5f9;">
              <td style="padding: 14px 0; font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">Status</td>
              <td style="padding: 14px 0; font-size: 14px; font-weight: 700; color: #0f172a;">{{ appointment.status }}</td>
            </tr>
            <tr v-if="appointment.payment_id" style="border-bottom: 1px solid #f1f5f9;">
              <td style="padding: 14px 0; font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">Transaction ID</td>
              <td style="padding: 14px 0; font-size: 14px; font-weight: 700; color: #0f172a; font-family: monospace;">{{ appointment.payment_id }}</td>
            </tr>
          </table>

          <!-- Amount Section -->
          <div style="background: #f8fafc; border-radius: 16px; padding: 24px; border: 1px solid #e2e8f0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 14px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 1px;">Total Amount</span>
              <span style="font-size: 24px; font-weight: 900; color: #0f172a;">
                {{ displayFee > 0 ? formatCurrency(displayFee, appointment.default_currency) : '—' }}
              </span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px; padding-top: 12px; border-top: 1px dashed #e2e8f0;">
              <span style="font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">Payment Status</span>
              <span :style="`font-size: 13px; font-weight: 800; color: ${paymentState === 'success' ? '#166534' : paymentState === 'failed' ? '#991b1b' : '#92400e'};`">
                {{ paymentBadgeLabel }}
              </span>
            </div>
          </div>

          <!-- Footer -->
          <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #f1f5f9; text-align: center;">
            <p style="font-size: 12px; color: #94a3b8; margin: 0;">This is a computer-generated invoice. No signature required.</p>
            <p style="font-size: 11px; color: #cbd5e1; margin: 8px 0 0 0;">Generated on {{ new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { createResource, Badge } from 'frappe-ui'
import { 
  CheckCircleIcon, XCircleIcon, ClockIcon, CalendarIcon, 
  DownloadIcon, BanknoteIcon, HashIcon,
  AlertTriangleIcon
} from 'lucide-vue-next'
import dayjs from 'dayjs'

const route = useRoute()
const appointmentId = route.params.id

const appointment = ref(null)
const loading = ref(true)
const error = ref(null)

// Determine payment state: 'success', 'failed', or 'pending'
const paymentState = computed(() => {
  if (!appointment.value) return 'pending'
  const ps = appointment.value.payment_status
  if (ps === 'Captured') return 'success'
  if (ps === 'Failed') return 'failed'
  // If invoiced via other means (Razorpay etc.) 
  if (appointment.value.invoiced === 1 || appointment.value.paid_amount > 0) return 'success'
  return 'pending'
})

// Dynamic config for the three states
const statusConfig = computed(() => {
  switch (paymentState.value) {
    case 'success':
      return {
        icon: CheckCircleIcon,
        title: 'Payment Successful!',
        subtitle: 'Your appointment has been confirmed and payment has been received.',
        headerBg: 'bg-green-50/50',
        iconBg: 'bg-green-100 text-green-600',
        titleColor: 'text-green-900',
        subtitleColor: 'text-green-700/80',
        bgBlur: 'bg-green-500/5',
      }
    case 'failed':
      return {
        icon: XCircleIcon,
        title: 'Payment Failed',
        subtitle: 'Your payment could not be processed. The appointment has been booked but payment is pending.',
        headerBg: 'bg-red-50/50',
        iconBg: 'bg-red-100 text-red-600',
        titleColor: 'text-red-900',
        subtitleColor: 'text-red-700/80',
        bgBlur: 'bg-red-500/5',
      }
    default: // pending
      return {
        icon: ClockIcon,
        title: 'Payment Pending',
        subtitle: 'Your appointment is booked. Payment is marked as due at clinic.',
        headerBg: 'bg-orange-50/50',
        iconBg: 'bg-orange-100 text-orange-600',
        titleColor: 'text-orange-900',
        subtitleColor: 'text-orange-700/80',
        bgBlur: 'bg-brand-orange/5',
      }
  }
})

const displayFee = computed(() => {
  if (!appointment.value) return 0
  return appointment.value.payment_record_amount || appointment.value.consultation_charge || appointment.value.paid_amount || 0
})

const paymentBadgeTheme = computed(() => {
  switch (paymentState.value) {
    case 'success': return 'green'
    case 'failed': return 'red'
    default: return 'orange'
  }
})

const paymentBadgeLabel = computed(() => {
  switch (paymentState.value) {
    case 'success': return 'Paid'
    case 'failed': return 'Failed'
    default: return 'Unpaid'
  }
})

const fetchAppointment = createResource({
  url: 'healthcare.healthcare.api.patient_portal.get_appointment_by_id',
  makeParams() {
    return { appointment_id: appointmentId }
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

// Print / Download Invoice as PDF
const printInvoice = () => {
  const invoiceEl = document.getElementById('invoice-print-area')
  if (!invoiceEl) return

  const printWindow = window.open('', '_blank', 'width=800,height=900')
  printWindow.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Invoice - ${appointment.value.name}</title>
      <style>
        @media print {
          body { margin: 0; padding: 0; }
          @page { margin: 15mm; }
        }
        body { font-family: 'Segoe UI', Arial, sans-serif; }
      </style>
    </head>
    <body>
      ${invoiceEl.innerHTML}
    </body>
    </html>
  `)
  printWindow.document.close()
  setTimeout(() => {
    printWindow.print()
  }, 300)
}

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
