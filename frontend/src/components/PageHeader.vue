<template>
  <div class="page-header">
    <div class="ph-left">
      <div v-if="icon" class="ph-icon">
        <AppIcon :name="icon" :size="18" />
      </div>
      <div class="ph-text">
        <h2 class="ph-title">{{ title }}</h2>
        <p v-if="subtitle" class="ph-sub">{{ subtitle }}</p>
      </div>
    </div>
    <div v-if="$slots.actions" class="ph-actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
import AppIcon from './AppIcon.vue'
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  icon: { type: String, default: '' }
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}
.ph-left {
  display: flex;
  gap: 12px;
  align-items: center;
  min-width: 0;
}
.ph-icon {
  width: 40px;
  height: 40px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-soft);
  color: var(--primary-strong);
  border: 1px solid var(--primary-line);
  flex-shrink: 0;
}
.ph-title {
  margin: 0;
  font-size: var(--fs-xl);
  font-weight: 600;
  line-height: 1.2;
}
.ph-sub {
  margin: 4px 0 0;
  color: var(--text-muted);
  font-size: var(--fs-sm);
  line-height: 1.4;
}
.ph-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
</style>
