<template>
  <el-row :gutter="20">
    <!-- 左栏: 插件列表 -->
    <el-col :span="6">
      <PluginList 
        :plugins="plugins" 
        :plugin-status="pluginStatus"
        @plugin-selected="handlePluginSelect" 
      />
    </el-col>

    <!-- 中栏: 选中插件的依赖 -->
    <el-col :span="10">
      <DependencyView
        :plugin-name="selectedPlugin"
        :requirements="pluginRequirements"
        :installed-packages="installedPackages"
        @request-refresh="fetchAllData"
        @dependency-click="handleDependencyClick"
      />
    </el-col>

    <!-- 右栏: 已安装的依赖 -->
    <el-col :span="8">
      <InstalledList 
        :packages="installedPackages"
        :highlighted-package="highlightedPackage"
      />
    </el-col>
  </el-row>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { ElMessage, ElNotification } from 'element-plus';
import PluginList from '../components/PluginList.vue';
import DependencyView from '../components/DependencyView.vue';
import InstalledList from '../components/InstalledList.vue';
// import { compare } from 'compare-versions'; // 不再需要在这里导入

const API_BASE_URL = 'http://localhost:8000';

const plugins = ref([]);
const installedPackages = ref([]);
const pluginRequirements = ref([]);
const selectedPlugin = ref(null);
const highlightedPackage = ref(null); // <--- 新增：用于高亮的包名

const fetchAllData = async () => {
  // ... (此函数内容不变)
  try {
    const [pluginsRes, installedRes] = await Promise.all([
      axios.get(`${API_BASE_URL}/api/plugins`),
      axios.get(`${API_BASE_URL}/api/python/installed_packages`),
    ]);
    plugins.value = pluginsRes.data;
    installedPackages.value = installedRes.data;
     ElNotification({
        title: '成功',
        message: '数据已刷新',
        type: 'success',
        duration: 2000
      });
  } catch (error) {
    ElMessage.error('加载初始数据失败: ' + (error.response?.data?.detail || error.message));
  }
};

onMounted(fetchAllData);

const handlePluginSelect = async (pluginName) => {
  highlightedPackage.value = null; // <--- 新增：切换插件时清除高亮
  selectedPlugin.value = pluginName;
  pluginRequirements.value = [];
  try {
    const response = await axios.get(`${API_BASE_URL}/api/plugins/${pluginName}/requirements`);
    pluginRequirements.value = response.data;
  } catch (error) {
    ElMessage.error(`获取 ${pluginName} 的依赖失败: ` + (error.response?.data?.detail || error.message));
  }
};

// <--- 新增：处理中栏点击事件的方法 --->
const handleDependencyClick = (packageName) => {
  highlightedPackage.value = packageName;
};


// ... (pluginStatus 计算属性不变)
const pluginStatus = computed(() => {
    const statusMap = {};
    if (!plugins.value.length || !installedPackages.value.length) {
        return statusMap;
    }
    plugins.value.forEach(p => {
        statusMap[p.name] = 'unknown';
    });
    return statusMap;
});
</script>