<template>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
    <div v-for="service in services" :key="service.title"
      @click="$emit('select', service.title)"
      class="ola-card p-6 flex flex-col items-center text-center cursor-pointer group hover:bg-navy hover:border-navy transition-all duration-500"
    >
      <div class="w-16 h-16 rounded-2xl bg-brand-orange/10 flex items-center justify-center mb-4 group-hover:bg-brand-orange transition-colors">
        <component :is="service.icon" class="w-8 h-8 text-brand-orange group-hover:text-white" />
      </div>
      <h3 class="font-black text-navy group-hover:text-white text-lg">{{ service.title }}</h3>
      <p class="text-xs font-bold text-gray-400 group-hover:text-white/60 uppercase tracking-widest mt-1">{{ service.subtitle }}</p>
      <div class="mt-4 opacity-0 group-hover:opacity-100 transition-opacity">
        <ArrowRightIcon class="w-5 h-5 text-brand-orange" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { 
  CalendarIcon, 
  VideoIcon, 
  FlaskConicalIcon, 
  PillIcon,
  ArrowRightIcon,
  ActivityIcon
} from 'lucide-vue-next'

const services = [
  { title: 'Book Appointment', subtitle: 'In-clinic visit', icon: CalendarIcon },
  { title: 'Video Consult', subtitle: 'Online consultation', icon: VideoIcon },
  { title: 'Therapy Sessions', subtitle: 'Personalized care', icon: ActivityIcon },
]

defineEmits(['select'])
</script>
