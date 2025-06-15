<template>
  <div class="settings-container">
    <el-form :model="config" label-width="180px" label-position="right">
      <el-form-item label="ComfyUI 插件目录路径">
        <el-input v-model="config.comfyui_path" placeholder="例如: D:/ComfyUI/custom_nodes"></el-input>
      </el-form-item>
      <el-form-item label="Python 解释器路径">
        <el-input v-model="config.python_path" placeholder="例如: D:/ComfyUI/python_embeded/python.exe"></el-input>
      </el-form-item>
      
      <!-- 核心修改：将输入框改为下拉选择框 -->
      <el-form-item label="pip 镜像源">
        <el-select v-model="config.pip_mirror" placeholder="请选择或输入镜像源" style="width: 100%;" clearable filterable allow-create>
          <el-option
            v-for="item in mirrorOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          >
            <span style="float: left">{{ item.label }}</span>
            <span style="float: right; color: var(--el-text-color-secondary); font-size: 13px">{{ item.name }}</span>
          </el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="saveConfig">保存配置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';

const API_BASE_URL = 'http://localhost:8000';

const config = ref({
  comfyui_path: '',
  python_path: '',
  pip_mirror: '', // 默认值为空字符串
});

// --- 新增：定义内置的镜像源选项 ---
const mirrorOptions = ref([
  {
    value: '',
    label: '默认 (pypi.org)',
    name: 'Official'
  },
  {
    value: 'https://pypi.tuna.tsinghua.edu.cn/simple',
    label: '清华大学',
    name: 'Tsinghua'
  },
  {
    value: 'https://mirrors.aliyun.com/pypi/simple/',
    label: '阿里云',
    name: 'Aliyun'
  },
  {
    value: 'http://pypi.douban.com/simple/',
    label: '豆瓣',
    name: 'Douban'
  },
  {
    value: 'https://pypi.mirrors.ustc.edu.cn/simple/',
    label: '中国科学技术大学',
    name: 'USTC'
  }
]);


const fetchConfig = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/config`);
    config.value = response.data;
    // 如果加载的配置是 null 或 undefined，给一个默认值
    if (config.value.pip_mirror === null || typeof config.value.pip_mirror === 'undefined') {
        config.value.pip_mirror = '';
    }
  } catch (error) {
    ElMessage.error('获取配置失败: ' + (error.response?.data?.detail || error.message));
  }
};

const saveConfig = async () => {
  try {
    await axios.post(`${API_BASE_URL}/api/config`, config.value);
    ElMessage.success('配置已保存！');
  } catch (error) {
    ElMessage.error('保存配置失败: ' + (error.response?.data?.detail || error.message));
  }
};

onMounted(() => {
  fetchConfig();
});
</script>

<style scoped>
.settings-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
</style>