<template>
  <el-card class="box-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span>已安装的依赖 ({{ filteredPackages.length }})</span>
        <el-input 
          v-model="searchTerm" 
          placeholder="搜索包..." 
          clearable
          style="width: 200px; margin-left: auto;"
          :prefix-icon="Search"
        />
      </div>
    </template>
    <el-scrollbar height="60vh" ref="scrollbarRef">
      <ul class="package-list" ref="listRef">
        <li v-for="pkg in filteredPackages" 
            :key="pkg.name"
            :class="{ 'highlight': getNormalizedName(pkg.name) === highlightedPackage }"
            :data-pkg-name="getNormalizedName(pkg.name)"
        >
          {{ pkg.name }}=={{ pkg.version }}
        </li>
      </ul>
    </el-scrollbar>
  </el-card>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { Search } from '@element-plus/icons-vue';

const props = defineProps({
  packages: {
    type: Array,
    required: true,
  },
  highlightedPackage: {
    type: String,
    default: null
  }
});

const searchTerm = ref('');
const scrollbarRef = ref(null);
const listRef = ref(null);

// <--- 新增：定义一个可复用的规范化函数 --->
const getNormalizedName = (name) => {
  return name.toLowerCase().replace(/_/g, '-');
};

const filteredPackages = computed(() => {
  if (!searchTerm.value) {
    return props.packages;
  }
  return props.packages.filter(pkg =>
    pkg.name.toLowerCase().includes(searchTerm.value.toLowerCase())
  );
});

watch(() => props.highlightedPackage, (newPkgName) => {
  if (newPkgName && listRef.value) {
    // newPkgName 已经是规范化后的，所以可以直接使用
    const element = listRef.value.querySelector(`[data-pkg-name="${newPkgName}"]`);
    if (element) {
      scrollbarRef.value.setScrollTop(element.offsetTop - (scrollbarRef.value.$el.clientHeight / 2) + (element.clientHeight / 2));
    }
  }
});
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.package-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
}
.package-list li {
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  transition: background-color 0.3s ease;
}
.package-list li:last-child {
  border-bottom: none;
}
.package-list li.highlight {
  background-color: #e6f7ff;
}
</style>