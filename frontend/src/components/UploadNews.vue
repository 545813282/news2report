<template>
  <el-card class="upload-card">
    <template #header>
      <div class="card-header">
        <span>📤 上传新文章</span>
      </div>
    </template>

    <!-- 输入方式选择 -->
    <el-radio-group v-model="inputMode" class="mode-selector">
      <el-radio-button label="text">📝 手动输入</el-radio-button>
      <el-radio-button label="pdf">📄 上传 PDF</el-radio-button>
      <el-radio-button label="url">🌐 网页链接</el-radio-button>
    </el-radio-group>

    <!-- 手动输入模式 -->
    <el-form
      v-if="inputMode === 'text'"
      ref="textFormRef"
      :model="textForm"
      :rules="textRules"
      label-position="top"
      class="upload-form"
    >
      <el-row :gutter="20">
        <el-col :span="16">
          <el-form-item label="文章标题" prop="title">
            <el-input v-model="textForm.title" placeholder="请输入新闻标题" clearable />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="发布时间" prop="published_at">
            <el-date-picker
              v-model="textForm.published_at"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="来源" prop="source">
            <el-input v-model="textForm.source" placeholder="如：机器之心、TechCrunch" clearable />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="原文链接" prop="url">
            <el-input v-model="textForm.url" placeholder="https://..." clearable />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="语言" prop="language">
        <el-radio-group v-model="textForm.language">
          <el-radio label="zh">中文</el-radio>
          <el-radio label="en">英文</el-radio>
          <el-radio label="zh-en">中英混合</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="正文内容" prop="content">
        <el-input
          v-model="textForm.content"
          type="textarea"
          :rows="8"
          placeholder="请粘贴新闻正文内容..."
        />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" :loading="submitting" @click="handleTextSubmit">
          {{ submitting ? 'AI 分析中...' : '上传并分析' }}
        </el-button>
        <el-button @click="resetTextForm">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- PDF 上传模式 -->
    <el-form
      v-if="inputMode === 'pdf'"
      ref="pdfFormRef"
      :model="pdfForm"
      :rules="pdfRules"
      label-position="top"
      class="upload-form"
    >
      <el-form-item label="PDF 文件" prop="file">
        <el-upload
          ref="pdfUploader"
          action="#"
          :auto-upload="false"
          :limit="1"
          :on-change="handlePdfChange"
          :on-remove="handlePdfRemove"
          accept=".pdf"
        >
          <el-button type="primary">选择 PDF 文件</el-button>
          <template #tip>
            <div class="el-upload__tip">请上传 PDF 格式文件，文件大小建议不超过 20MB</div>
          </template>
        </el-upload>
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="16">
          <el-form-item label="文章标题" prop="title">
            <el-input v-model="pdfForm.title" placeholder="留空使用文件名" clearable />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="发布时间" prop="published_at">
            <el-date-picker
              v-model="pdfForm.published_at"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="来源" prop="source">
            <el-input v-model="pdfForm.source" placeholder="如：arXiv、公司财报" clearable />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="原文链接" prop="url">
            <el-input v-model="pdfForm.url" placeholder="https://..." clearable />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="语言" prop="language">
        <el-radio-group v-model="pdfForm.language">
          <el-radio label="zh">中文</el-radio>
          <el-radio label="en">英文</el-radio>
          <el-radio label="zh-en">中英混合</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" :loading="submitting" @click="handlePdfSubmit">
          {{ submitting ? 'AI 分析中...' : '上传 PDF 并分析' }}
        </el-button>
        <el-button @click="resetPdfForm">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 网页链接模式 -->
    <el-form
      v-if="inputMode === 'url'"
      ref="urlFormRef"
      :model="urlForm"
      :rules="urlRules"
      label-position="top"
      class="upload-form"
    >
      <el-form-item label="网页链接" prop="url">
        <el-input v-model="urlForm.url" placeholder="https://..." clearable />
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="16">
          <el-form-item label="文章标题" prop="title">
            <el-input v-model="urlForm.title" placeholder="留空自动提取" clearable />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="发布时间" prop="published_at">
            <el-date-picker
              v-model="urlForm.published_at"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="来源" prop="source">
            <el-input v-model="urlForm.source" placeholder="留空自动识别" clearable />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="语言" prop="language">
            <el-radio-group v-model="urlForm.language">
              <el-radio label="zh">中文</el-radio>
              <el-radio label="en">英文</el-radio>
              <el-radio label="zh-en">中英混合</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item>
        <el-button type="primary" :loading="submitting" @click="handleUrlSubmit">
          {{ submitting ? '抓取并分析中...' : '抓取网页并分析' }}
        </el-button>
        <el-button @click="resetUrlForm">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 分析结果 -->
    <div v-if="result" class="result-section">
      <el-divider />
      <div class="result-title">
        <span>✅ 分析完成</span>
        <el-tag type="success" size="small">{{ result.id }}</el-tag>
        <el-button
          v-if="result.structured?.report_pdf_path"
          type="primary"
          size="small"
          @click="downloadReport('analysis')"
        >
          下载 AI 分析报告 PDF
        </el-button>
        <el-button
          v-if="result.structured?.structured_pdf_path"
          type="info"
          size="small"
          @click="downloadReport('structured')"
        >
          下载结构化分析报告 PDF
        </el-button>
        <el-button
          type="primary"
          size="small"
          @click="downloadOriginal"
        >
          下载原文
        </el-button>
      </div>

      <el-row :gutter="24" class="result-content">
        <el-col :span="12">
          <div class="panel-title">📄 原文内容</div>
          <div class="original-text">{{ result.structured.original_text }}</div>
        </el-col>
        <el-col :span="12">
          <div class="panel-title">🧠 AI 结构化分析</div>

          <div class="analysis-section">
            <div class="section-title">分类</div>
            <el-tag type="primary" size="small">{{ result.structured.category }}</el-tag>
          </div>

          <div class="analysis-section">
            <div class="section-title">标签</div>
            <el-tag
              v-for="tag in result.structured.tags"
              :key="tag"
              type="info"
              size="small"
              class="tag-item"
            >
              {{ tag }}
            </el-tag>
          </div>

          <div class="analysis-section">
            <div class="section-title">AI 摘要</div>
            <p class="ai-summary">{{ result.structured.ai_summary }}</p>
          </div>

          <div class="analysis-section">
            <div class="section-title">AI 观点</div>
            <p class="viewpoint">{{ result.structured.ai_opinion.viewpoint }}</p>
            <div class="opinion-tags">
              <el-tag size="small">重要性: {{ result.structured.ai_opinion.significance }}</el-tag>
              <el-tag size="small">影响: {{ result.structured.ai_opinion.impact_direction }}</el-tag>
            </div>
          </div>

          <div class="analysis-section" v-if="result.structured.entities.length > 0">
            <div class="section-title">关键实体</div>
            <el-tag
              v-for="entity in result.structured.entities"
              :key="entity.name"
              type="info"
              size="small"
              class="tag-item"
            >
              {{ entity.name }} <span class="entity-type">({{ entity.type }})</span>
            </el-tag>
          </div>

          <div class="analysis-section" v-if="result.structured.key_points.length > 0">
            <div class="section-title">核心要点</div>
            <ol class="key-points">
              <li v-for="(point, idx) in result.structured.key_points" :key="idx">{{ point }}</li>
            </ol>
          </div>
        </el-col>
      </el-row>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules, UploadFile } from 'element-plus'

const inputMode = ref('text')
const submitting = ref(false)
const result = ref<any>(null)

// 手动输入表单
const textFormRef = ref<FormInstance>()
const textForm = reactive({
  title: '',
  content: '',
  source: '',
  published_at: '',
  url: '',
  language: 'zh',
})

const textRules: FormRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [
    { required: true, message: '请输入正文', trigger: 'blur' },
    { min: 10, message: '正文至少 10 个字符', trigger: 'blur' },
  ],
  source: [{ required: true, message: '请输入来源', trigger: 'blur' }],
  published_at: [{ required: true, message: '请选择发布时间', trigger: 'change' }],
}

// PDF 表单
const pdfFormRef = ref<FormInstance>()
const pdfUploader = ref<any>(null)
const pdfForm = reactive({
  title: '',
  source: '',
  published_at: '',
  url: '',
  language: 'zh',
})
const pdfFile = ref<File | null>(null)

const pdfRules: FormRules = {
  title: [{ required: false }],
}

const handlePdfChange = (uploadFile: UploadFile) => {
  pdfFile.value = uploadFile.raw || null
}

const handlePdfRemove = () => {
  pdfFile.value = null
}

// URL 表单
const urlFormRef = ref<FormInstance>()
const urlForm = reactive({
  url: '',
  title: '',
  source: '',
  published_at: '',
  language: 'zh',
})

const urlRules: FormRules = {
  url: [
    { required: true, message: '请输入网页链接', trigger: 'blur' },
    { type: 'url', message: '请输入有效的 URL', trigger: 'blur' },
  ],
}

const handleTextSubmit = async () => {
  if (!textFormRef.value) return
  await textFormRef.value.validate(async (valid) => {
    if (!valid) return
    await submit('/api/upload-news', textForm, 'json')
  })
}

const handlePdfSubmit = async () => {
  if (!pdfFile.value) {
    alert('请选择 PDF 文件')
    return
  }

  const formData = new FormData()
  formData.append('file', pdfFile.value)
  if (pdfForm.title) formData.append('title', pdfForm.title)
  if (pdfForm.source) formData.append('source', pdfForm.source)
  if (pdfForm.published_at) formData.append('published_at', pdfForm.published_at)
  if (pdfForm.url) formData.append('url', pdfForm.url)
  formData.append('language', pdfForm.language)

  await submit('/api/upload-pdf', formData, 'form')
}

const handleUrlSubmit = async () => {
  if (!urlFormRef.value) return
  await urlFormRef.value.validate(async (valid) => {
    if (!valid) return
    await submit('/api/fetch-url', urlForm, 'json')
  })
}

const submit = async (url: string, data: any, type: 'json' | 'form') => {
  submitting.value = true
  result.value = null

  try {
    const options: RequestInit = {
      method: 'POST',
      body: type === 'json' ? JSON.stringify(data) : data,
    }
    if (type === 'json') {
      options.headers = { 'Content-Type': 'application/json' }
    }

    const response = await fetch(url, options)
    const resData = await response.json()
    if (!response.ok) {
      throw new Error(resData.detail || `上传失败: ${response.status}`)
    }

    result.value = resData
  } catch (err: any) {
    console.error('上传失败:', err)
    alert(`上传失败: ${err.message}`)
  } finally {
    submitting.value = false
  }
}

const resetTextForm = () => {
  textFormRef.value?.resetFields()
  result.value = null
}

const resetPdfForm = () => {
  pdfFormRef.value?.resetFields()
  pdfFile.value = null
  pdfUploader.value?.clearFiles()
  result.value = null
}

const resetUrlForm = () => {
  urlFormRef.value?.resetFields()
  result.value = null
}

const downloadReport = (type: 'analysis' | 'structured') => {
  if (!result.value?.id) return
  window.open(`/api/reports/${result.value.id}/${type}`, '_blank')
}

const downloadOriginal = () => {
  if (!result.value?.id) return
  window.open(`/api/reports/${result.value.id}/original`, '_blank')
}
</script>

<style scoped>
.upload-card {
  margin-top: 20px;
}

.card-header {
  font-weight: 600;
}

.mode-selector {
  margin-bottom: 24px;
}

.upload-form {
  max-width: 100%;
}

.result-section {
  margin-top: 20px;
}

.result-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 20px;
}

.result-content {
  margin-top: 16px;
}

.panel-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--primary-dark);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--primary);
}

.original-text {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text);
  white-space: pre-wrap;
  background: var(--bg-soft);
  padding: 16px;
  border-radius: 6px;
  border-left: 4px solid var(--primary);
  max-height: 600px;
  overflow-y: auto;
}

.analysis-section {
  margin-bottom: 16px;
  background: var(--bg-soft);
  padding: 12px;
  border-radius: 6px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary-dark);
  margin-bottom: 8px;
}

.ai-summary {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text);
  margin: 0;
}

.viewpoint {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text);
  margin: 0 0 8px 0;
}

.opinion-tags {
  display: flex;
  gap: 8px;
}

.tag-item {
  margin: 0;
}

.entity-type {
  font-size: 11px;
  color: var(--text-muted);
}

.key-points {
  margin: 0;
  padding-left: 18px;
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-secondary);
}

:deep(.el-upload__tip) {
  color: var(--text-secondary);
}
</style>
