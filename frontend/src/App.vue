<template>
  <el-container style="height: 100vh;">
    <el-header class="main-header">
      <h1>ComfyUI 依赖管理工具 (ComfyUI Node Manager)</h1>
    </el-header>
    <el-main>
      <el-tabs v-model="activeTab" type="border-card">
        <el-tab-pane label="管理器 (Manager)" name="manager">
          <ManagerView v-if="activeTab === 'manager'" />
        </el-tab-pane>
        <el-tab-pane label="设置 (Settings)" name="settings">
          <SettingsView v-if="activeTab === 'settings'" />
        </el-tab-pane>
      </el-tabs>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref } from 'vue';
import ManagerView from './views/ManagerView.vue';
import SettingsView from './views/SettingsView.vue';

const activeTab = ref('manager');
</script>

<style>
body {
  margin: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}
.main-header {
  line-height: 60px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}
.el-tabs__content {
    padding: 20px;
}
</style>