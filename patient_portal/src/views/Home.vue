<template>
  <div>
    <!-- Hero Section -->
    <section class="relative py-10 md:py-20 px-4 md:px-6 overflow-hidden w-full">
      <div class="absolute inset-0 bg-gradient-to-b from-slate-100/50 to-transparent -z-10"></div>
      <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-brand-orange/5 rounded-full blur-3xl -mr-64 -mt-64 text-transparent">.</div>
      <div class="absolute bottom-0 left-0 w-[400px] h-[400px] bg-navy/5 rounded-full blur-3xl -ml-48 -mb-48 text-transparent">.</div>
      
      <div class="max-w-5xl mx-auto text-center animate-fade-up">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-brand-orange/10 text-brand-orange text-xs font-black uppercase tracking-widest mb-5 md:mb-6">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-orange opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-brand-orange"></span>
          </span>
          Premium Healthcare 
        </div>
        <h2 class="text-4xl sm:text-5xl md:text-7xl font-black text-navy mb-4 md:mb-6 tracking-tight leading-[1.1]">
          Find Your Best <span class="text-brand-orange drop-shadow-sm">Specialist</span>
        </h2>
        <p class="text-base md:text-xl text-slate-500 mb-8 md:mb-12 max-w-2xl mx-auto font-medium px-2">
          Book appointments with world-class practitioners and manage your healthcare journey in one place.
        </p>
        
        <!-- Search Bar -->
        <div class="p-1.5 bg-white rounded-2xl shadow-xl shadow-slate-200/50 flex flex-col md:flex-row gap-2 max-w-2xl mx-auto border border-slate-100">
          <!-- Search Input -->
          <div class="flex-1 relative">
            <SearchIcon class="absolute left-4 md:left-6 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search by doctor name or expertise..."
              class="w-full pl-11 md:pl-14 pr-4 md:pr-6 py-3 md:py-4 bg-transparent text-sm font-bold text-slate-900 placeholder:text-slate-400 outline-none"
            />
          </div>
          
          <button class="bg-slate-900 text-white rounded-xl py-3 px-6 md:px-8 flex items-center justify-center gap-2 hover:bg-slate-800 transition-all font-bold text-xs uppercase tracking-widest group shadow-lg shadow-slate-900/10">
            <SearchIcon class="w-4 h-4" />
            <span class="sm:inline">Search</span>
          </button>
        </div>
      </div>
    </section>



    <!-- Therapy Plans Section -->
    <section class="w-full px-4 md:px-6 mb-10 md:mb-20 animate-fade-up stagger-1" v-if="therapyTemplates.length > 0">
      <div class="max-w-7xl mx-auto">
        <div class="mb-6 md:mb-8 flex items-end justify-between">
          <div>
            <h3 class="text-xl md:text-2xl font-black text-navy tracking-tight">Therapy Plans</h3>
            <p class="text-slate-500 font-medium text-sm md:text-base">Comprehensive care packages</p>
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="plan in therapyTemplates" :key="plan.name"
                @click="openBookingModel(plan)"
                class="group relative overflow-hidden bg-white p-5 md:p-6 rounded-[20px] md:rounded-[24px] border border-slate-100 hover:border-slate-200 transition-all cursor-pointer hover:shadow-xl hover:shadow-slate-200/50"
            >
                <div class="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                </div>
                <div class="relative z-10">
                    <h3 class="font-bold text-slate-900 text-base md:text-lg mb-1">{{ plan.plan_name }}</h3>
                    <div class="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wider mb-4">
                        <div class="w-1.5 h-1.5 rounded-full bg-brand-orange"></div>
                        {{ plan.total_sessions }} Sessions
                    </div>
                    <div class="flex items-center gap-2 text-sm font-bold text-brand-orange group-hover:gap-3 transition-all">
                        Book Now 
                    </div>
                </div>
            </div>
        </div>
      </div>
    </section>



    <!-- Practitioners Section -->
    <section class="w-full px-4 md:px-6 mb-12 md:mb-24 animate-fade-up stagger-2" v-if="filteredPractitioners.length > 0">
      <div class="max-w-7xl mx-auto flex flex-wrap items-start md:items-center justify-between gap-3 mb-6 md:mb-8">
        <div>
          <h3 class="text-2xl md:text-3xl font-black text-navy tracking-tight mb-1 md:mb-2">
            {{ selectedDepartment ? `Best in ${selectedDepartment}` : 'Top Rated Specialists' }}
          </h3>
          <div class="flex items-center gap-2">
            <span class="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
            <p class="text-sm md:text-[15px] text-slate-500 font-semibold">{{ filteredPractitioners.length }} active practitioners available</p>
          </div>
        </div>
      </div>
      <div class="max-w-7xl mx-auto">
        <PractitionerSelector
          :items="paginatedPractitioners"
          :page="practitionerPage"
          :totalPages="totalPractitionerPages"
          @update:page="practitionerPage = $event"
          @book="openBookingForPractitioner"
        />
      </div>
    </section>

    <!-- Booking Dialogs -->
    <BookAppointmentModel v-model="showBookingDialog" :practitioner="selectedPractitioner" />
    <BookTherapySessionModel v-model="showTherapyBookingDialog" />
    <BookTherapyPlanModel v-model="showTherapyPlanDialog" :initial-template="selectedPlanTemplate" />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { createResource } from 'frappe-ui'
import DepartmentSelector from '@/components/DepartmentSelector.vue'
import PractitionerSelector from '@/components/PractitionerSelector.vue'

import BookAppointmentModel from '@/components/BookAppointmentModel.vue'
import BookTherapySessionModel from '@/components/BookTherapySessionModel.vue'
import BookTherapyPlanModel from '@/components/BookTherapyPlanModel.vue'
import { SearchIcon, BuildingIcon, ChevronDownIcon } from 'lucide-vue-next'

// Dashboard state
const searchQuery = ref('');
const selectedDepartment = ref(null);
const deptPage = ref(1);
const practitionerPage = ref(1);
const itemsPerPage = 8; // Increased for full width

// Booking dialog state
const showBookingDialog = ref(false);
const showTherapyBookingDialog = ref(false);
const showTherapyPlanDialog = ref(false);
const selectedPractitioner = ref(null);

// --- Resources ---
const getDepartments = createResource({
  url: "/api/method/healthcare.healthcare.api.patient_portal.get_departments",
  method: "GET",
});
getDepartments.fetch();

const getPractitioners = createResource({
  url: "/api/method/healthcare.healthcare.api.patient_portal.get_practitioners",
  method: "GET",
});
getPractitioners.fetch();


const therapyTemplates = ref([])
const fetchTherapyTemplates = createResource({
	url: '/api/method/healthcare.healthcare.api.patient_portal.get_therapy_plan_templates',
	method: 'GET',
	onSuccess(data) {
		therapyTemplates.value = data.slice(0, 4) // Show top 4
	}
})
fetchTherapyTemplates.fetch();

// --- Computed ---
const departments = computed(() => getDepartments.data || []);
const practitioners = computed(() => getPractitioners.data || []);

const filteredPractitioners = computed(() => {
  let list = practitioners.value;
  if (selectedDepartment.value) {
    list = list.filter(p => p.department === selectedDepartment.value);
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    list = list.filter(p => 
      p.practitioner_name?.toLowerCase().includes(q) ||
      p.department?.toLowerCase().includes(q) ||
      p.designation?.toLowerCase().includes(q)
    );
  }
  return list;
});

const totalDeptPages = computed(() => Math.ceil(departments.value.length / itemsPerPage) || 1);
const paginatedDepartments = computed(() => {
  const start = (deptPage.value - 1) * itemsPerPage;
  return departments.value.slice(start, start + itemsPerPage);
});

const totalPractitionerPages = computed(() => Math.ceil(filteredPractitioners.value.length / itemsPerPage) || 1);
const paginatedPractitioners = computed(() => {
  const start = (practitionerPage.value - 1) * itemsPerPage;
  return filteredPractitioners.value.slice(start, start + itemsPerPage);
});

// --- Watchers ---
watch(selectedDepartment, () => {
  practitionerPage.value = 1;
});

watch(searchQuery, () => {
  practitionerPage.value = 1;
});

// --- Methods ---
const handleDepartmentSelect = (dept) => {
  selectedDepartment.value = selectedDepartment.value === dept ? null : dept;
};

const openBookingForPractitioner = (practitioner) => {
  selectedPractitioner.value = practitioner;
  showBookingDialog.value = true;
};

const handleServiceSelect = (serviceTitle) => {
  if (serviceTitle === 'Book Appointment') {
    showBookingDialog.value = true;
  } else if (serviceTitle === 'Therapy Sessions') {
    if (getTherapyPlans.data?.length > 0) {
      showTherapyBookingDialog.value = true;
    } else {
      showTherapyPlanDialog.value = true;
    }
  }
};

const selectedPlanTemplate = ref(null)
const openBookingModel = (template) => {
    selectedPlanTemplate.value = template
	showTherapyPlanDialog.value = true
}
</script>
