<template>
  <div class="calendar-container w-full select-none">
    <!-- Premium Header -->
    <div class="flex items-center justify-between mb-8 px-2">
      <div class="flex flex-col">
        <h3 class="text-2xl font-black text-slate-900 tracking-tight">{{ currentMonthName }}</h3>
        <p class="text-[11px] font-bold text-slate-300 uppercase tracking-[0.2em] mt-1">{{ currentYear }}</p>
      </div>
      
      <div class="flex items-center gap-3">
        <button 
          @click="prevMonth"
          class="w-10 h-10 flex items-center justify-center rounded-xl bg-slate-50 text-slate-400 hover:bg-slate-900 hover:text-white transition-all active:scale-90"
        >
          <ChevronLeftIcon class="w-4 h-4" />
        </button>
        <button 
          @click="nextMonth"
          class="w-10 h-10 flex items-center justify-center rounded-xl bg-slate-50 text-slate-400 hover:bg-slate-900 hover:text-white transition-all active:scale-90"
        >
          <ChevronRightIcon class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Minimalist Weekdays -->
    <div class="grid grid-cols-7 gap-1 mb-4">
      <div v-for="day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']" :key="day"
        class="text-[10px] font-black text-slate-300 uppercase tracking-widest text-center py-2"
      >
        {{ day }}
      </div>
    </div>

    <!-- High-end Grid -->
    <div class="grid grid-cols-7 gap-1">
      <div v-for="blank in blanks" :key="'blank-'+blank" class="h-14"></div>
      
      <div v-for="day in daysInMonth" :key="day"
        @click="!isPast(day) && selectDay(day)"
        class="group relative h-14 flex items-center justify-center transition-all duration-300"
      >
        <div 
          class="absolute inset-1 rounded-2xl transition-all duration-500"
          :class="[
            activeDay === day 
              ? 'bg-slate-900 shadow-lg shadow-slate-900/20 scale-100' 
              : isPast(day) 
                ? 'bg-transparent scale-0' 
                : 'bg-slate-50/0 group-hover:bg-slate-50 group-hover:scale-100'
          ]"
        ></div>
        
        <span 
          class="relative text-sm font-black transition-colors duration-300"
          :class="[
            activeDay === day 
              ? 'text-white' 
              : isPast(day) 
                ? 'text-slate-200 cursor-not-allowed' 
                : 'text-slate-600 group-hover:text-slate-900'
          ]"
        >
          {{ day }}
        </span>

        <!-- Today Indicator -->
        <div 
          v-if="isToday(day)"
          class="absolute bottom-2.5 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full"
          :class="activeDay === day ? 'bg-white/40' : 'bg-brand-orange'"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ChevronLeftIcon, ChevronRightIcon } from 'lucide-vue-next'

const currentMonth = ref(new Date().getMonth())
const currentYear = ref(new Date().getFullYear())
const today = ref(new Date())
const activeDay = ref(today.value.getDate())

const emit = defineEmits(["update:selectedDate"])

const currentMonthName = computed(() => {
  return new Date(currentYear.value, currentMonth.value).toLocaleString('default', { month: 'long' })
})

const daysInMonth = computed(() => {
  return new Date(currentYear.value, currentMonth.value + 1, 0).getDate()
})

const blanks = computed(() => {
  const startOfMonth = new Date(currentYear.value, currentMonth.value, 1)
  return startOfMonth.getDay()
})

const isToday = (day) => {
  const date = new Date(currentYear.value, currentMonth.value, day)
  return date.toDateString() === today.value.toDateString()
}

const isPast = (day) => {
  const date = new Date(currentYear.value, currentMonth.value, day)
  const todayReset = new Date(today.value.getFullYear(), today.value.getMonth(), today.value.getDate())
  return date < todayReset
}

function prevMonth() {
  activeDay.value = null
  emit("update:selectedDate", null)
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value -= 1
  } else currentMonth.value--
}

function nextMonth() {
  activeDay.value = null
  emit("update:selectedDate", null)
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value += 1
  } else currentMonth.value++
}

function selectDay(day) {
  activeDay.value = day
  emit("update:selectedDate", formatDate(day))
}

function formatDate(day) {
  const year = currentYear.value
  const month = String(currentMonth.value + 1).padStart(2, '0')
  const date = String(day).padStart(2, '0')
  return `${year}-${month}-${date}`
}

onMounted(() => {
  if (!isPast(today.value.getDate())) {
    selectDay(today.value.getDate())
  }
})
</script>
