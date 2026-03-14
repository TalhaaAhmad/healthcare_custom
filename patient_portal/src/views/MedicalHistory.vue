<template>
  <div class="px-4 sm:px-6 md:px-10 py-6 md:py-16 max-w-7xl mx-auto space-y-10">
    <!-- Header Section -->
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-4">
      <div>
        <h1 class="text-3xl md:text-5xl font-semibold tracking-tight text-gray-900 mb-2">
          Medical History
        </h1>
        <p class="text-base md:text-xl text-gray-500">
          View your past clinical encounters, lab tests, and procedures.
        </p>
      </div>
      <div>
        <Button size="lg" variant="subtle" @click="historyResource.reload()">
          Refresh History
        </Button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="historyResource.loading" class="flex flex-col items-center justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-primary"></div>
      <p class="mt-4 text-gray-500">Loading your medical records...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="!historyResource.data || historyResource.data.length === 0" 
         class="bg-white rounded-3xl md:rounded-[48px] p-10 md:p-20 text-center border shadow-sm flex flex-col items-center justify-center">
      <div class="bg-gray-50 text-gray-400 p-6 rounded-full mb-6 relative">
        <svg class="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <h3 class="text-xl font-medium text-gray-900 mb-2">No Records Found</h3>
      <p class="text-gray-500 max-w-md">
        There are currently no medical records on file for your profile. Records will appear here after your first consultation or test.
      </p>
    </div>

    <!-- History Timeline -->
    <div v-else class="space-y-6 md:space-y-8 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-gray-200 before:to-transparent">
      
      <div v-for="(record, index) in historyResource.data" :key="record.name" 
           class="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
        
        <!-- Timeline Dot (Mobile: Left, Desktop: Center) -->
        <div class="flex items-center justify-center w-10 h-10 rounded-full border-4 border-white bg-white shadow-sm absolute left-0 md:left-1/2 -translate-x-0 md:-translate-x-1/2 shrink-0 z-10 transition-colors duration-300"
             :class="getTypeColorVariant(record.reference_doctype, 'dot')">
          <component :is="getIconForType(record.reference_doctype)" class="w-4 h-4" />
        </div>

        <!-- Card Container -->
        <div class="w-[calc(100%-3rem)] md:w-[calc(50%-2.5rem)] ml-auto md:ml-0 overflow-hidden transform transition-all duration-300 hover:-translate-y-1">
          <div class="bg-white rounded-2xl md:rounded-3xl p-6 md:p-8 shadow-sm border border-gray-100/50 hover:shadow-md transition-shadow relative overflow-hidden group">
            
            <!-- Type Accent Line -->
            <div class="absolute top-0 left-0 w-full h-1" :class="getTypeColorVariant(record.reference_doctype, 'border')"></div>

            <div class="flex justify-between items-start mb-4">
              <div>
                <Badge :class="getTypeColorVariant(record.reference_doctype, 'badge')" class="mb-3 px-2.5 py-1 text-xs font-medium rounded-full border-0">
                  {{ record.reference_doctype }}
                </Badge>
                <h3 class="font-semibold text-lg text-gray-900 group-hover:text-brand-primary transition-colors">
                  {{ record.reference_name }}
                </h3>
              </div>
              <div class="text-right shrink-0 flex flex-col items-end gap-2">
                <div>
                  <span class="block text-sm font-medium text-gray-900">{{ formatDate(record.communication_date) }}</span>
                  <span class="block text-xs mt-1 text-gray-500">{{ formatTime(record.communication_date) }}</span>
                </div>
                <button @click="printRecord(record)" class="p-1.5 text-gray-400 hover:text-brand-primary hover:bg-brand-50 rounded-lg transition-colors border border-transparent shadow-none" title="Print Record">
                  <PrinterIcon class="w-4 h-4" />
                </button>
              </div>
            </div>

            <!-- Patient Chip (Shown if viewing records for a relative) -->
            <div v-if="record.patient_name !== currentUserName" class="inline-flex items-center gap-1.5 px-2 py-1 bg-gray-50 rounded-md mb-4 text-xs font-medium text-gray-600 border border-gray-100">
              <UserIcon class="w-3 h-3" />
              {{ record.patient_name }}
            </div>

            <!-- Record Content (HTML Rendered) -->
            <div v-if="record.subject" class="prose prose-sm max-w-none text-gray-600 prose-p:leading-relaxed prose-headings:font-medium prose-headings:text-gray-900 line-clamp-4 group-hover:line-clamp-none transition-all duration-500" v-html="record.subject"></div>

            <!-- Attachment Button if exists -->
            <div v-if="record.attach" class="mt-6 pt-4 border-t border-gray-50 flex items-center justify-between">
              <span class="text-sm font-medium text-gray-500 flex items-center gap-1.5">
                <PaperclipIcon class="w-4 h-4" />
                Attachment Available
              </span>
              <a :href="record.attach" target="_blank" class="inline-flex items-center justify-center gap-2 rounded-xl bg-gray-50 hover:bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 transition-colors shadow-sm ring-1 ring-inset ring-gray-300/30">
                <FileTextIcon class="w-4 h-4 text-gray-500" />
                View File
              </a>
            </div>
          </div>
        </div>

      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { createResource, Badge, Button } from 'frappe-ui'
import dayjs from 'dayjs'
import { 
  FileTextIcon, 
  StethoscopeIcon, 
  FlaskConicalIcon, 
  ActivitySquareIcon,
  UserIcon,
  PaperclipIcon,
  CalendarCheckIcon,
  PillIcon,
  InfoIcon,
  PrinterIcon
} from 'lucide-vue-next'

const currentUserName = computed(() => {
  return window.frappe_boot?.user_info?.full_name || ''
})

const historyResource = createResource({
  url: 'healthcare.healthcare.api.patient_portal.get_medical_history',
  cache: false,
  auto: true
})

const formatDate = (date) => {
  return dayjs(date).format('MMM D, YYYY')
}

const formatTime = (date) => {
  return dayjs(date).format('h:mm A')
}

// Icon Mapping
const getIconForType = (doctype) => {
  switch(doctype) {
    case 'Patient Encounter': return StethoscopeIcon
    case 'Lab Test': return FlaskConicalIcon
    case 'Vital Signs': return ActivitySquareIcon
    case 'Patient Appointment': return CalendarCheckIcon
    case 'Prescription': return PillIcon
    default: return FileTextIcon
  }
}

// Color Theming based on Record Type
const getTypeColorVariant = (doctype, element) => {
  const themes = {
    'Patient Encounter': {
      border: 'bg-emerald-500',
      badge: 'bg-emerald-50 text-emerald-700',
      dot: 'text-emerald-500 group-hover:border-emerald-100 group-hover:bg-emerald-50'
    },
    'Lab Test': {
      border: 'bg-purple-500',
      badge: 'bg-purple-50 text-purple-700',
      dot: 'text-purple-500 group-hover:border-purple-100 group-hover:bg-purple-50'
    },
    'Vital Signs': {
      border: 'bg-rose-500',
      badge: 'bg-rose-50 text-rose-700',
      dot: 'text-rose-500 group-hover:border-rose-100 group-hover:bg-rose-50'
    },
    'Patient Appointment': {
      border: 'bg-blue-500',
      badge: 'bg-blue-50 text-blue-700',
      dot: 'text-blue-500 group-hover:border-blue-100 group-hover:bg-blue-50'
    },
    'default': {
      border: 'bg-amber-500',
      badge: 'bg-amber-50 text-amber-700',
      dot: 'text-amber-500 group-hover:border-amber-100 group-hover:bg-amber-50'
    }
  }

  const theme = themes[doctype] || themes['default']
  return theme[element]
}

const printRecord = (record) => {
  // Store the record HTML temporarily in localStorage so the print window can access it
  localStorage.setItem('print_record_data', JSON.stringify({
    title: record.reference_name,
    type: record.reference_doctype,
    date: formatDate(record.communication_date),
    time: formatTime(record.communication_date),
    patient: record.patient_name,
    content: record.subject
  }))
  
  // Open the print route in a new window
  const printWindow = window.open('#/history/print', '_blank')
  if (printWindow) {
    printWindow.focus()
  }
}
</script>

<style scoped>
/* Styling to ensure the v-html injected tables/content from ERPNext look good */
::v-deep(.prose table) {
  display: block;
  overflow-x: auto;
  white-space: nowrap;
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  -webkit-overflow-scrolling: touch;
}
::v-deep(.prose table th) {
  text-align: left;
  padding: 0.5rem 0.75rem;
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  font-weight: 500;
  color: #374151;
}
::v-deep(.prose table td) {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #f3f4f6;
  color: #6b7280;
}
::v-deep(.prose p) {
  margin-bottom: 0.5rem;
}
::v-deep(.prose ul) {
  list-style-type: disc;
  padding-left: 1.25rem;
  margin-bottom: 0.75rem;
}
</style>
