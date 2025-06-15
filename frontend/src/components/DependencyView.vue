<template>
  <!-- 卡片部分模板不变 -->
  <el-card class="box-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span>依赖项 for: <strong>{{ pluginName || 'N/A' }}</strong></span>
      </div>
    </template>
    <div v-if="!pluginName">
      <el-empty description="请从左侧选择一个插件" />
    </div>
    <div v-else-if="requirements.length === 0">
      <el-empty description="此插件没有 requirements.txt 文件" />
    </div>
    <el-table :data="dependencyStatus" style="width: 100%" v-else @row-click="onRowClick">
      <el-table-column prop="name" label="包名" />
      <el-table-column prop="required" label="要求版本">
        <template #default="scope">
          <el-tooltip :content="scope.row.rawRequirement" placement="top" :disabled="!scope.row.isGit">
            <span>{{ scope.row.required }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column prop="installed" label="已安装版本" />
      <el-table-column prop="status" label="状态">
        <template #default="scope">
          <el-tag :type="scope.row.tagType" disable-transitions>{{ scope.row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button 
            v-if="scope.row.action" 
            type="primary" 
            size="small"
            :loading="loadingStates[scope.row.name]"
            @click.stop="installPackage(scope.row.rawRequirement)"
          >
            {{ scope.row.action }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <!-- 新增：安装日志弹窗 -->
  <el-dialog
    v-model="logDialogVisible"
    title="安装日志"
    width="70%"
    :close-on-click-modal="false"
    @closed="installationLog = []"
  >
    <div class="log-container">
      <pre v-for="(line, index) in installationLog" :key="index">{{ line }}</pre>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button type="primary" @click="logDialogVisible = false" :disabled="isInstalling">
          {{ isInstalling ? '正在安装...' : '关闭' }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, ref, nextTick } from 'vue';
import { ElMessage, ElNotification } from 'element-plus';
import { compare } from 'compare-versions';

// --- script setup 的前半部分基本不变 ---

const props = defineProps({
  pluginName: String,
  requirements: Array,
  installedPackages: Array,
});
const emit = defineEmits(['request-refresh', 'dependency-click']);
const loadingStates = ref({});

// --- 新增：日志弹窗相关的响应式变量 ---
const logDialogVisible = ref(false);
const installationLog = ref([]);
const isInstalling = ref(false);


// --- WebSocket 地址 ---
const WS_BASE_URL = 'ws://localhost:8000';

const parseRequirement = (reqStr) => {
  // ... (此函数内容不变)
  reqStr = reqStr.trim();
  if (reqStr.startsWith('git+')) {
    const eggMatch = reqStr.match(/#egg=([a-zA-Z0-9\-_]+)/);
    if (eggMatch) { return { name: eggMatch[1], specifier: 'git', isGit: true }; }
    const urlMatch = reqStr.match(/\/([a-zA-Z0-9\-_]+)(\.git)?/g);
    if (urlMatch) {
      const lastSegment = urlMatch[urlMatch.length - 1];
      const name = lastSegment.replace(/\//g, '').replace(/\.git/g, '');
      return { name, specifier: 'git', isGit: true };
    }
    return { name: reqStr, specifier: 'git', isGit: true };
  }
  const match = reqStr.match(/^([a-zA-Z0-9\-_.]+)(\[.+\])?\s*([<>=!~].*)?$/);
  if (!match) return { name: reqStr, specifier: '', isGit: false };
  return { name: match[1].trim(), specifier: match[3] ? match[3].trim() : '', isGit: false };
};

const checkVersion = (specifier, version) => {
  // ... (此函数内容不变)
  if (!specifier || specifier === 'any') return true;
  try {
    const operator = specifier.match(/^[<>=!~]+/)[0];
    const versionNumber = specifier.replace(operator, '');
    return compare(version, versionNumber, operator);
  } catch (e) {
    return false;
  }
};

const installedMap = computed(() => {
  // ... (此计算属性不变)
  return new Map(props.installedPackages.map(p => [ p.name.toLowerCase().replace(/_/g, '-'), p.version ]));
});

const dependencyStatus = computed(() => {
  // ... (此计算属性不变)
  if (!props.requirements) return [];
  return props.requirements.map(req => {
    const { name, specifier, isGit } = parseRequirement(req);
    const lookupName = name.toLowerCase().replace(/_/g, '-');
    const installedVersion = installedMap.value.get(lookupName);
    const statusInfo = { name, lookupName, required: isGit ? 'git' : (specifier || 'any'), isGit, rawRequirement: req };
    if (installedVersion) {
      if (isGit || checkVersion(specifier, installedVersion)) {
        return { ...statusInfo, installed: installedVersion, status: '✅ 已安装', tagType: 'success', action: null };
      } else {
        return { ...statusInfo, installed: installedVersion, status: '⚠️ 版本不符', tagType: 'warning', action: '更新/重装' };
      }
    } else {
      return { ...statusInfo, installed: 'N/A', status: '❌ 未安装', tagType: 'danger', action: '安装' };
    }
  });
});

const onRowClick = (row) => {
  // ... (此函数内容不变)
  if (row.installed !== 'N/A') {
    emit('dependency-click', row.lookupName);
  }
};

// --- 重写 installPackage 方法以使用 WebSocket ---
const installPackage = (packageName) => {
  const reqName = parseRequirement(packageName).name;
  loadingStates.value[reqName] = true;
  isInstalling.value = true;
  logDialogVisible.value = true;
  installationLog.value = [`正在准备安装 ${packageName}...`];

  const ws = new WebSocket(`${WS_BASE_URL}/ws/install`);

  ws.onopen = () => {
    // 连接建立后，发送要安装的包名
    ws.send(JSON.stringify({ package_name: packageName }));
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    // 将日志追加到数组中
    installationLog.value.push(data.message);
    
    // 自动滚动到日志底部
    nextTick(() => {
        const container = document.querySelector('.log-container');
        if(container) container.scrollTop = container.scrollHeight;
    });

    if(data.type === 'done'){
        if(data.status === 'success'){
             ElNotification({ title: '成功', message: `${packageName} 安装成功！`, type: 'success' });
             emit('request-refresh'); // 通知父组件刷新数据
        } else {
             ElNotification({ title: '安装失败', message: `安装 ${packageName} 失败，请查看日志详情。`, type: 'error' });
        }
    }
  };

  ws.onerror = (error) => {
    installationLog.value.push(`\n[ERROR] WebSocket 连接出错: ${error.message || '未知错误'}`);
    ElMessage.error('WebSocket 连接失败！');
    isInstalling.value = false;
    loadingStates.value[reqName] = false;
  };

  ws.onclose = () => {
    // 无论成功失败，连接关闭时都结束加载状态
    installationLog.value.push('\n[INFO] 安装进程已结束，连接关闭。');
    isInstalling.value = false;
    loadingStates.value[reqName] = false;
  };
};

</script>

<!-- 新增：日志弹窗的样式 -->
<style scoped>
.log-container {
  background-color: #1e1e1e;
  color: #d4d4d4;
  padding: 15px;
  border-radius: 4px;
  height: 60vh;
  overflow-y: auto;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  white-space: pre-wrap; /* 允许自动换行 */
  word-wrap: break-word;
}
</style>