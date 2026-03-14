<template>
  <div class="print-container bg-white min-h-screen p-8 max-w-4xl mx-auto text-gray-900">
    <div v-if="record" class="space-y-6">
      <!-- Clinic Header (Matches Portal) -->
      <div class="flex items-center justify-between border-b border-gray-200 pb-6 mb-8">
        <div>
          <img :src="clinicLogo" alt="Clinic Logo" class="h-12 w-auto object-contain print-logo" />
        </div>
        <div class="text-right">
          <h1 class="text-2xl font-semibold">{{ record.title }}</h1>
          <p class="text-gray-500 mt-1">{{ record.type }}</p>
        </div>
      </div>

      <!-- Patient & Date Meta -->
      <div class="flex justify-between items-start bg-gray-50 p-4 rounded-xl border border-gray-100">
        <div>
          <p class="text-sm text-gray-500 uppercase tracking-wide font-semibold">Patient</p>
          <p class="font-medium mt-1">{{ record.patient }}</p>
        </div>
        <div class="text-right">
          <p class="text-sm text-gray-500 uppercase tracking-wide font-semibold">Date</p>
          <p class="font-medium mt-1">{{ record.date }} at {{ record.time }}</p>
        </div>
      </div>

      <!-- Record Content -->
      <div class="mt-8 prose prose-gray max-w-none print-prose" v-html="record.content"></div>
      
      <!-- Footer -->
      <div class="mt-16 pt-8 border-t border-gray-200 text-center text-sm text-gray-400 print-footer">
        <p>This is a computer generated document and requires no signature.</p>
        <p class="mt-1">Generated from the Patient Portal on {{ currentDate }}</p>
      </div>
    </div>
    
    <div v-else class="flex flex-col items-center justify-center h-64">
      <p class="text-gray-500">Loading print data...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import dayjs from 'dayjs'

const clinicLogo = '/assets/healthcare/images/zan-center-for-women-logo.png'
const record = ref(null)
const currentDate = ref(dayjs().format('MMM D, YYYY h:mm A'))

onMounted(() => {
  const data = localStorage.getItem('print_record_data')
  if (data) {
    try {
      record.value = JSON.parse(data)
      
      // Delay printing slightly to allow images/fonts to render
      setTimeout(() => {
        window.print()
        
        // Optional: clear the localstorage after printing
        // localStorage.removeItem('print_record_data')
      }, 500)
    } catch (e) {
      console.error("Error parsing print data", e)
    }
  }
})
</script>

<style>
/* Base print layout resets to ensure clean PDF output */
@media print {
  @page {
    margin: 0.75in;
  }
  
  body, .print-container {
    background: transparent !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  /* Force background colors to print if needed */
  * {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
}

/* Ensure injected tables look good on paper */
::v-deep(.print-prose table) {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1.5rem;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
  border: 1px solid #e5e7eb;
}
::v-deep(.print-prose table th) {
  text-align: left;
  padding: 0.75rem 1rem;
  background-color: #f9fafb !important;
  border-bottom: 2px solid #e5e7eb;
  font-weight: 600;
  color: #111827;
}
::v-deep(.print-prose table td) {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e5e7eb;
  color: #374151;
}
::v-deep(.print-prose p) {
  margin-bottom: 0.75rem;
  color: #111827;
}
::v-deep(.print-prose h1), ::v-deep(.print-prose h2), ::v-deep(.print-prose h3), ::v-deep(.print-prose h4) {
  color: #111827;
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}
</style>
