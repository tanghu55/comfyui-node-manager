<template>
  <el-card class="box-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span>插件列表 ({{ plugins.length }})</span>
      </div>
    </template>
    <el-menu @select="handleSelect">
      <el-menu-item v-for="plugin in plugins" :key="plugin.name" :index="plugin.name">
        <el-icon v-if="!plugin.has_reqs"><CircleCheck /></el-icon>
        <el-icon v-else><List /></el-icon>
        <template #title>{{ plugin.name }}</template>
      </el-menu-item>
    </el-menu>
  </el-card>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  plugins: {
    type: Array,
    required: true,
  },
  pluginStatus: {
      type: Object,
      required: true,
  }
});

const emit = defineEmits(['plugin-selected']);

const handleSelect = (index) => {
  emit('plugin-selected', index);
};
</script>

<style scoped>
.el-menu {
    border-right: none;
}
</style>