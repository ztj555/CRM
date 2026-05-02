<template>
  <div class="login-bg">
    <!-- 背景装饰圆 -->
    <div class="bg-circle circle-1"></div>
    <div class="bg-circle circle-2"></div>
    <div class="bg-circle circle-3"></div>

    <div class="login-card">
      <!-- Logo -->
      <div class="login-logo">
        <div class="logo-circle">CRM</div>
        <div class="logo-text">
          <h1>融鑫汇</h1>
          <p>客户管理系统</p>
        </div>
      </div>

      <div class="login-divider"></div>

      <!-- 表单 -->
      <div class="login-form-title">账号登录</div>
      <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
        <div class="input-group">
          <div class="input-icon"><User /></div>
          <el-form-item prop="username" style="flex:1; margin:0">
            <el-input
              v-model="form.username"
              placeholder="请输入账号"
              size="large"
              :prefix-icon="User"
              style="height:46px"
            />
          </el-form-item>
        </div>

        <div class="input-group" style="margin-top:16px">
          <div class="input-icon"><Lock /></div>
          <el-form-item prop="password" style="flex:1; margin:0">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
              style="height:46px"
            />
          </el-form-item>
        </div>

        <el-button
          type="primary"
          size="large"
          :loading="loading"
          style="width:100%; height:46px; font-size:15px; margin-top:24px; background:linear-gradient(135deg,#E91E63,#F06292); border:none; border-radius:8px"
          @click="handleLogin"
        >
          登 录
        </el-button>
      </el-form>

      <div class="login-tips">
        <el-icon><InfoFilled /></el-icon>
        <span>默认账号：admin &nbsp;|&nbsp; 密码：admin123</span>
      </div>
    </div>

    <!-- 底部 -->
    <div class="login-footer">融鑫汇CRM · 局域网版 · {{ new Date().getFullYear() }}</div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, InfoFilled } from '@element-plus/icons-vue'
import { login } from '../api'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const res = await login(form)
    localStorage.setItem('token', res.token)
    localStorage.setItem('user', JSON.stringify(res.user))
    router.push('/dashboard')
  } catch (e) {
    ElMessage.error(e.detail || e || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-bg {
  min-height: 100vh;
  background: linear-gradient(135deg, #FCE4EC 0%, #F8BBD0 40%, #F48FB1 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

/* 装饰圆 */
.bg-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
}
.circle-1 { width: 300px; height: 300px; top: -80px; right: -80px; }
.circle-2 { width: 200px; height: 200px; bottom: 60px; left: -60px; background: rgba(255,255,255,0.1); }
.circle-3 { width: 150px; height: 150px; bottom: -50px; right: 80px; background: rgba(255,255,255,0.08); }

.login-card {
  background: white;
  border-radius: 16px;
  padding: 40px 44px;
  width: 400px;
  box-shadow: 0 20px 60px rgba(233, 30, 99, 0.2), 0 4px 16px rgba(0,0,0,0.08);
  position: relative;
  z-index: 1;
}

.login-logo {
  display: flex;
  align-items: center;
  gap: 14px;
  justify-content: center;
  margin-bottom: 20px;
}
.logo-circle {
  width: 54px;
  height: 54px;
  background: linear-gradient(135deg, #E91E63, #F06292);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 15px;
  font-weight: bold;
  letter-spacing: 2px;
  box-shadow: 0 4px 12px rgba(233, 30, 99, 0.3);
}
.logo-text h1 {
  font-size: 22px;
  color: #E91E63;
  margin: 0 0 4px 0;
  letter-spacing: 4px;
}
.logo-text p {
  font-size: 12px;
  color: #999;
  margin: 0;
}

.login-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, #F8BBD0, transparent);
  margin-bottom: 24px;
}

.login-form-title {
  font-size: 15px;
  color: #666;
  text-align: center;
  margin-bottom: 20px;
  font-weight: 500;
}

.input-group {
  display: flex;
  align-items: center;
  border: 1.5px solid #F8BBD0;
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.2s;
}
.input-group:focus-within {
  border-color: #E91E63;
  box-shadow: 0 0 0 3px rgba(233, 30, 99, 0.1);
}
.input-icon {
  width: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #F48FB1;
  background: #FDF2F7;
  height: 46px;
  flex-shrink: 0;
}

.login-tips {
  margin-top: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: #999;
  font-size: 12px;
}

.login-footer {
  position: absolute;
  bottom: 20px;
  color: rgba(233, 30, 99, 0.5);
  font-size: 12px;
}
</style>
