<template>
  <div>
    <div class="page-header">
      <h3>公告管理</h3>
      <el-button type="primary" size="small" @click="openCreate()" v-if="isManager">
        <Plus /> 发布公告
      </el-button>
    </div>

    <div style="padding:16px">
      <!-- 滚动条消息 -->
      <el-card style="margin-bottom:16px" v-if="ticker">
        <template #header>
          <div class="card-header-title">
            <el-icon color="#E6A23C"><Bell /></el-icon>
            滚动消息
          </div>
        </template>
        <div class="ticker-list">
          <div v-for="t in tickers" :key="t.id" class="ticker-item">
            <el-icon color="#E6A23C"><ChatLineSquare /></el-icon>
            <span>{{ t.content }}</span>
            <el-tag type="info" size="small" style="margin-left:auto">{{ t.created_at?.slice(0,10) }}</el-tag>
            <div v-if="isManager" style="display:flex; gap:4px; margin-left:8px">
              <el-button size="small" text type="primary" @click="openEdit(t)">编辑</el-button>
              <el-button size="small" text type="danger" @click="deleteNotice(t.id)">删除</el-button>
            </div>
          </div>
          <el-empty v-if="!tickers.length" description="暂无滚动消息" :image-size="50" />
        </div>
      </el-card>

      <!-- 公告列表 -->
      <el-card>
        <template #header>
          <div class="card-header-title">
            <el-icon color="#409EFF"><Document /></el-icon>
            公告列表
          </div>
        </template>

        <div class="notice-list">
          <div v-for="n in notices" :key="n.id" class="notice-item">
            <div class="notice-header">
              <span class="notice-title">{{ n.title }}</span>
              <el-tag type="primary" size="small" effect="plain">公告</el-tag>
              <span class="notice-time">{{ n.created_at?.slice(0,10) }}</span>
              <div v-if="isManager" style="display:flex; gap:4px; margin-left:auto">
                <el-button size="small" text type="primary" @click="openEdit(n)">编辑</el-button>
                <el-button size="small" text type="danger" @click="deleteNotice(n.id)">删除</el-button>
              </div>
            </div>
            <div class="notice-content">{{ n.content }}</div>
          </div>
          <el-empty v-if="!notices.length" description="暂无公告" :image-size="80" />
        </div>
      </el-card>
    </div>

    <!-- 发布/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editMode ? '编辑公告' : '发布公告'" width="540px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="类型">
          <el-radio-group v-model="form.notice_type">
            <el-radio :value="1">公告</el-radio>
            <el-radio :value="2">滚动条</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" :rows="4" placeholder="请输入内容" />
        </el-form-item>
        <el-form-item label="是否显示">
          <el-switch v-model="form.is_visible" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveNotice" :loading="saving">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Bell, ChatLineSquare, Document } from '@element-plus/icons-vue'
import { apiFetch } from '@/utils/api.js'

const user = computed(() => JSON.parse(localStorage.getItem('user') || '{}'))
const isManager = computed(() => user.value.role <= 4)

const notices = ref([])
const tickers = ref([])
const loading = ref(false)
const ticker = ref(true)

const dialogVisible = ref(false)
const editMode = ref(false)
const saving = ref(false)
const form = ref({ title: '', content: '', notice_type: 1, is_visible: 1, id: null })

const loadData = async () => {
  loading.value = true
  try {
    const all = await apiFetch('/api/notices?notice_type=0')
    notices.value = all.filter(n => n.notice_type === 1)
    tickers.value = all.filter(n => n.notice_type === 2)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  editMode.value = false
  form.value = { title: '', content: '', notice_type: 1, is_visible: 1, id: null }
  dialogVisible.value = true
}

const openEdit = (item) => {
  editMode.value = true
  form.value = { ...item }
  dialogVisible.value = true
}

const saveNotice = async () => {
  if (!form.value.content) return ElMessage.warning('请填写内容')
  saving.value = true
  try {
    if (editMode.value && form.value.id) {
      await apiFetch(`/api/notices/${form.value.id}`, {
        method: 'PUT', body: JSON.stringify(form.value)
      })
    } else {
      await apiFetch('/api/notices', {
        method: 'POST', body: JSON.stringify(form.value)
      })
    }
    ElMessage.success(editMode.value ? '更新成功' : '发布成功')
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    saving.value = false
  }
}

const deleteNotice = async (id) => {
  await ElMessageBox.confirm('确认删除该公告？', '提示', { type: 'warning' })
  await apiFetch(`/api/notices/${id}`, { method: 'DELETE' })
  ElMessage.success('已删除')
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.page-header { display:flex; justify-content:space-between; align-items:center; padding:16px 16px 0; }
.page-header h3 { margin:0; font-size:16px; color:#333; font-weight:600; }
.card-header-title { display:flex; align-items:center; gap:6px; font-weight:600; }

.ticker-list { display:flex; flex-direction:column; gap:8px; }
.ticker-item {
  display: flex; align-items: center; gap:8px;
  padding: 8px 12px; background: #fffbf0; border-radius: 6px;
  border-left: 3px solid #E6A23C;
  font-size: 13px; color: #333;
}

.notice-list { display:flex; flex-direction:column; gap:12px; }
.notice-item {
  padding: 14px 16px; border-radius: 8px;
  border: 1px solid #F0E0EB; background: #fefefe;
  transition: box-shadow 0.2s;
}
.notice-item:hover { box-shadow: 0 2px 8px rgba(233, 30, 99, 0.1); }
.notice-header { display:flex; align-items:center; gap:8px; margin-bottom:8px; }
.notice-title { font-size:14px; font-weight:600; color:#333; }
.notice-time { font-size:12px; color:#aaa; }
.notice-content { font-size:13px; color:#666; line-height:1.6; white-space:pre-wrap; }
</style>
