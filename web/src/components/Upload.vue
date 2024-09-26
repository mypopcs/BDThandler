<template>
  <el-upload
    class="upload-demo"
    action="http://localhost:5000/upload"
    :on-progress="handleProgress"
    :on-success="handleSuccess"
    :on-error="handleError"
    :file-list="fileList"
    accept=".xlsx,.xls"
  >
    <el-button type="primary">点击上传</el-button>
    <template #tip>
      <div class="el-upload__tip">只能上传xlsx/xls文件</div>
    </template>
  </el-upload>
  <el-progress :percentage="uploadProgress" v-if="uploading"></el-progress>
</template>

<script>
import { ref } from 'vue'
// import { useDataStore } from '../workers/dataStore'
import { ElMessage } from 'element-plus'
import axios from 'axios'
export default {
  name: 'UploadBar',
  setup() {
    // const dataStore = useDataStore()
    const state = ref({
      uploadProgress: 0,
      uploading: false
    })
    const handleProgress = (event) => {
      state.value.uploading = true
      state.value.uploadProgress = Math.round(event.percent)
    }

    const handleSuccess = (response) => {
      state.value.uploading = false
      state.value.uploadProgress = 100
      ElMessage.success('文件上传成功，正在处理数据...')
      processFile(response.file_path)
    }

    const handleError = (err) => {
      state.value.uploading = false
      state.value.uploadProgress = 0
      console.error('上传失败:', err)
      ElMessage.error('上传失败')
    }
    const processFile = (filePath) => {
      axios
        .post('http://localhost:5000/process', { file_path: filePath })
        .then((response) => {
          if (response.data.parse_success) {
            ElMessage.success('数据处理完成')
            this.fetchData()
          }
        })
        .catch((error) => {
          ElMessage.error('数据处理失败: ' + error.response.data.error)
          this.loading = false
        })
    }
    return {
      handleProgress,
      handleSuccess,
      handleError
    }
  }
}
</script>

<style>
</style>