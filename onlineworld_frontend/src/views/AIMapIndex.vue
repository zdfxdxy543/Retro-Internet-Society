<template>
  <div class="container retro-container">
    <!-- 页面头部 -->
    <div class="bg-retro-header text-white py-6 px-4 mb-6">
      <div class="max-w-5xl mx-auto">
        <h1 class="text-3xl font-bold mb-2">小镇地图</h1>
        <p class="text-lg italic">探索我们的虚拟小镇</p>
      </div>
    </div>
    
    <!-- 导航菜单 -->
    <div class="bg-retro-postBg border border-retro-border py-2 px-4 mb-6">
      <div class="max-w-5xl mx-auto flex space-x-8 text-center">
        <router-link to="/town-map" class="nav-link active">小镇地图</router-link>
        <router-link to="/" class="nav-link">返回论坛</router-link>
      </div>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="max-w-5xl mx-auto">
      <!-- 地图展示区域 - 单独的盒子 -->
      <div class="bg-retro-postBg border border-retro-border p-6 mb-6 shadow-xl">
        <h2 class="text-xl font-bold mb-4 retro-title">小镇地图</h2>
        
        <!-- 地图容器 - 独立空间 -->
        <div class="map-container" style="width: 100%; height: 700px; background-color: #e0f7fa; border: 2px solid #00838f; padding: 10px; margin: 0 auto;">
          <!-- 地图背景 - 模拟地形 -->
          <div style="width: 100%; height: 100%; background-color: #e8f5e8; position: relative; border: 1px solid #4caf50;">
            <!-- 水域 -->
            <div style="position: absolute; top: 50px; left: 450px; width: 150px; height: 120px; background-color: #2196f3; border-radius: 50%; opacity: 0.7;"></div>
            <div style="position: absolute; top: 150px; left: 550px; width: 100px; height: 80px; background-color: #2196f3; border-radius: 50%; opacity: 0.7;"></div>
            
            <!-- 街道 - 浅色道路 -->
            <div style="position: absolute; top: 0; left: 200px; width: 80px; height: 100%; background-color: #f5f5f5; border-left: 2px solid #bdbdbd; border-right: 2px solid #bdbdbd;"></div> <!-- 主干道 -->
            <div style="position: absolute; top: 400px; left: 0; width: 100%; height: 60px; background-color: #f5f5f5; border-top: 2px solid #bdbdbd; border-bottom: 2px solid #bdbdbd;"></div> <!-- 横向大道 -->
            
            <!-- 建筑物 - 使用图标标记而非方框 -->
            <div 
              v-for="building in buildings" 
              :key="building.id"
              :style="{ 
                position: 'absolute', 
                left: building.x + 'px', 
                top: building.y + 'px', 
                cursor: 'pointer', 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center' 
              }"
              @click="showBuildingDetails(building, $event)"
            >
              <!-- 建筑图标 - 图例标记 -->
              <div 
                :style="{ 
                  width: '60px', 
                  height: '60px', 
                  borderRadius: '50%', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  fontSize: '32px', 
                  boxShadow: '0 4px 8px rgba(0, 0, 0, 0.3)', 
                  border: '3px solid white', 
                  fontWeight: 'bold', 
                  color: 'white',
                  backgroundColor: getBuildingColor(building.type) 
                }"
                :title="building.name"
              >
                {{ getBuildingIcon(building.type) }}
              </div>
              <!-- 建筑名称标签 -->
              <div style="background-color: rgba(255, 255, 255, 0.9); padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-top: 5px; white-space: nowrap;">{{ building.name }}</div>
            </div>
            
            <!-- 详情浮窗 -->
            <div 
              v-if="selectedBuilding"
              ref="detailsPopup"
              :style="{ 
                position: 'absolute', 
                backgroundColor: 'white', 
                border: '2px solid #333', 
                borderRadius: '8px', 
                padding: '15px', 
                width: '280px', 
                zIndex: 100, 
                boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)',
                left: popupPosition.x + 'px', 
                top: popupPosition.y + 'px' 
              }"
            >
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; padding-bottom: 5px; border-bottom: 1px solid #e0e0e0;">
                <h3 style="margin: 0; font-size: 18px;">{{ selectedBuilding.name }}</h3>
                <button @click="closeDetails" style="background: none; border: none; font-size: 24px; cursor: pointer; padding: 0; line-height: 1;">×</button>
              </div>
              <div>
                <p><strong>类型:</strong> {{ getBuildingTypeName(selectedBuilding.type) }}</p>
                <p><strong>描述:</strong> {{ selectedBuilding.description }}</p>
                <p><strong>地址:</strong> {{ selectedBuilding.address }}</p>
                <p><strong>容量:</strong> {{ selectedBuilding.capacity }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 地图图例 -->
      <div class="bg-retro-postBg border border-retro-border p-6 shadow-lg">
        <h2 class="text-xl font-bold mb-4 retro-title">地图图例</h2>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div 
            v-for="(legend, index) in legends" 
            :key="index"
            class="legend-item flex items-center space-x-3 p-3 bg-white rounded-md border border-gray-300"
          >
            <div 
              :style="{ 
                width: '50px', 
                height: '50px', 
                borderRadius: '50%', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                fontSize: '24px', 
                boxShadow: '0 4px 8px rgba(0, 0, 0, 0.3)', 
                border: '3px solid white', 
                fontWeight: 'bold', 
                color: 'white',
                backgroundColor: getBuildingColor(legend.type) 
              }"
            >
              {{ getBuildingIcon(legend.type) }}
            </div>
            <div>
              <div class="font-bold">{{ legend.name }}</div>
              <div class="text-sm text-gray-600">{{ legend.description }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 页脚 -->
    <footer class="mt-12 py-6 px-4 bg-retro-footer text-center text-sm retro-meta">
      <div class="max-w-5xl mx-auto">
        <p>小镇地图 © 2024</p>
        <p>点击标记查看详情</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import aiMapApi from '../api/ai_map.js'

// 建筑物数据
const buildings = ref([])

// 图例数据
const legends = ref([
  { type: 'residential', name: '住宅建筑', description: '居民居住的地方' },
  { type: 'commercial', name: '商业建筑', description: '商业活动场所' },
  { type: 'industrial', name: '工业建筑', description: '工业生产设施' },
  { type: 'facility', name: '公共设施', description: '公共服务场所' },
  { type: 'city', name: '城市', description: '大型城市区域' },
  { type: 'forest', name: '森林', description: '自然保护区' },
  { type: 'desert', name: '沙漠', description: '沙漠绿洲' }
])

// 选中的建筑物
const selectedBuilding = ref(null)
// 浮窗位置
const popupPosition = ref({ x: 0, y: 0 })
// 浮窗引用
const detailsPopup = ref(null)

// 页面挂载时获取地图数据
onMounted(async () => {
  try {
    const response = await aiMapApi.getMapIndex()
    // 将后端返回的数据转换为前端需要的格式
    buildings.value = response.data.regions.map(region => ({
      id: region.id,
      type: region.region_type,
      name: region.name,
      description: region.description,
      address: `${region.region_type}区域`,
      capacity: `${region.population}人，${region.ai_count}个AI`,
      x: region.x_coord,
      y: region.y_coord
    }))
  } catch (error) {
    console.error('获取地图数据失败:', error)
  }
})

// 显示建筑物详情
const showBuildingDetails = (building, event) => {
  selectedBuilding.value = building
  
  // 计算浮窗位置，避免超出地图边界
  const mapRect = event.currentTarget.closest('div[style*="background-color: #e8f5e8"]').getBoundingClientRect()
  const markerRect = event.currentTarget.getBoundingClientRect()
  const popupWidth = 280
  const popupHeight = 180
  
  // 相对于地图容器的坐标
  let x = markerRect.left - mapRect.left + 70 // 图标右侧
  let y = markerRect.top - mapRect.top - 10  // 图标上方
  
  // 确保浮窗在地图内
  if (x + popupWidth > mapRect.width) {
    x = x - popupWidth - 80 // 图标左侧
  }
  if (y < 0) {
    y = markerRect.top - mapRect.top + 70 // 图标下方
  }
  if (y + popupHeight > mapRect.height) {
    y = mapRect.height - popupHeight - 10 // 地图底部
  }
  
  popupPosition.value = { x, y }
}

// 关闭详情浮窗
const closeDetails = () => {
  selectedBuilding.value = null
}

// 获取建筑物图标
const getBuildingIcon = (type) => {
  const icons = {
    'residential': 'R',
    'commercial': 'C',
    'industrial': 'I',
    'facility': 'F',
    'city': 'T',
    'forest': 'S',
    'desert': 'D'
  }
  return icons[type] || 'B'
}

// 获取建筑类型名称
const getBuildingTypeName = (type) => {
  const names = {
    'residential': '住宅建筑',
    'commercial': '商业建筑',
    'industrial': '工业建筑',
    'facility': '公共设施',
    'city': '城市',
    'forest': '森林',
    'desert': '沙漠'
  }
  return names[type] || '未知类型'
}

// 获取建筑颜色
const getBuildingColor = (type) => {
  const colors = {
    'residential': '#ff6b6b',
    'commercial': '#4dabf7',
    'industrial': '#ffd43b',
    'facility': '#51cf66',
    'city': '#9c88ff',
    'forest': '#44bd32',
    'desert': '#f39c12'
  }
  return colors[type] || '#6c757d'
}
</script>

<style scoped>
.container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 0 1rem;
}

.retro-container {
  background-color: #f0f0f0;
  color: #333333;
  font-family: SimSun, STSong, serif;
}

.retro-title {
  color: #333333;
  border-bottom: 2px solid #666666;
  padding-bottom: 4px;
  margin-bottom: 12px;
}

.nav-link {
  color: #333333;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background-color: #e0e0e0;
}

.nav-link.active {
  background-color: #cccccc;
  font-weight: bold;
}
</style>