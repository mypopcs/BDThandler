<template>
  <div>
    <h1>Database Data</h1>
    <h2>上传数据</h2>
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
    <h2>数据对比</h2>
    <el-table :data="paginatedCombinedData">
      <el-table-column
        v-for="column in combinedColumns"
        :key="column.prop"
        :prop="column.prop"
        :label="column.label"
      >
      </el-table-column>
    </el-table>
    <el-pagination
      @size-change="handleCompareSizeChange"
      @current-change="handleCurrentChange"
      :current-page="CompareCurrentPage"
      :page-sizes="[10, 20, 50, 100]"
      :page-size="ComparePageSize"
      :total="combinedData.length"
      layout="total, sizes, prev, pager, next, jumper"
    >
    </el-pagination>
    <h2>元数据</h2>
    <el-table
      v-loading="loading"
      :data="tableData"
      border
      height="450"
      stripe
      style="width: 100%"
    >
      <el-table-column
        v-for="column in tableColumns"
        :key="column"
        :prop="column"
        :label="column"
        :width="columnWidths[column] || 'auto'"
        show-overflow-tooltip
      ></el-table-column>
    </el-table>
    <el-empty v-if="tableData.length === 0" description="没有数据"></el-empty>
    <el-row :gutter="20" style="padding: 16px 0">
      <el-col :span="2">
        <el-select v-model="dataLimit" @change="fetchData">
          <el-option label="500条" :value="500"></el-option>
          <el-option label="1000条" :value="1000"></el-option>
          <el-option label="2000条" :value="2000"></el-option>
          <el-option label="全量数据" :value="-1"></el-option>
        </el-select>
      </el-col>
      <el-col :span="22">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
        >
        </el-pagination>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import Dexie from 'dexie'
import { ElMessage } from 'element-plus'

export default {
  data() {
    return {
      CompareCurrentPage: 1,
      ComparePageSize: 20,
      analyzedTotal: 0,
      db: null,
      analyzedData: [],
      loading: false,
      loadingText: '加载中...',
      tableData: [],
      currentPage: 1,
      pageSize: 20,
      total: 0,
      fileList: [],
      dataLimit: 500,
      uploadProgress: 0,
      uploading: false,
      tableColumns: [],
      displayColumns: ['评论内容'],
      columnWidths: {
        搜索词: '100px',
        用户昵称: '150px',
        发布时间: '100px',
        发布地点: '100px',
        点赞数: '80px',
        评论数: '80px',
        采集时间: '200px',
        文章ID: '230px',
        当前类别: '100px'
      }
    }
  },
  async created() {
    this.db = new Dexie('AnalyzedDatabase')
    this.db.version(1).stores({
      analyzedData: '++id'
    })
    await this.db.open()
    await this.fetchData()
    await this.fetchAnalyzedData()
  },
  mounted() {
    this.fetchData()
  },
  computed: {
    combinedData() {
      //合并两个数据源
      return this.tableData.map((item, index) => ({
        ...item,
        ...this.analyzedData[index]
      }))
    },
    combinedColumns() {
      //定义要显示的列
      return [
        { prop: '评论内容', label: '清洗前数据' },
        { prop: '评论内容', label: '清洗后数据' }
      ]
    },
    paginatedCombinedData() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.combinedData.slice(start, end)
    }
  },
  methods: {
    handleCompareSizeChange(newSize) {
      this.ComparePageSize = newSize
    },
    handleCompareCurrentChange(newPage) {
      this.CompareCurrentPage = newPage
    },
    async fetchData() {
      this.loading = true
      try {
        const response = await this.$axios.get(
          `http://localhost:5000/get-data`,
          {
            params: {
              limit: this.dataLimit,
              page: this.currentPage,
              per_page: this.pageSize
            }
          }
        )
        console.log('Fetched data:', response.data)
        this.tableData = response.data.data
        this.total = response.data.total
        this.tableColumns = response.data.columns

        // // 存储前2000条数据到IndexedDB
        // console.log('Storing first 2000 records in IndexedDB')
        // await this.db.analyzedData.clear()
        // await this.db.analyzedData.bulkAdd(this.tableData.slice(0, 2000))
        // this.analyzedData = await this.db.analyzedData.toArray()
        // console.log('Stored data:', this.analyzedData)
      } catch (error) {
        console.error('Error fetching data:', error)
      }
      this.loading = false
    },
    async fetchAnalyzedData() {
      try {
        const response = await this.$axios.get(
          `http://localhost:5000/get-data?limit=500`
        )
        await this.db.analyzedData.clear()
        await this.db.analyzedData.bulkAdd(response.data.data)
        this.analyzedData = await this.db.analyzedData.toArray()
        this.analyzedTotal = this.analyzedData.length
        console.log('Fetched and stored analyzed data:', this.analyzedData)
      } catch (error) {
        console.error('Error fetching analyzed data:', error)
      }
    },
    handleProgress(event) {
      this.uploading = true
      this.uploadProgress = Math.round(event.percent)
    },
    handleSuccess(response) {
      this.uploading = false
      this.uploadProgress = 100
      ElMessage.success('文件上传成功，正在处理数据...')
      this.loading = true
      this.loadingText = '正在加载数据，请稍候...'
      this.processFile(response.file_path)
    },
    handleError(err) {
      this.uploading = false
      this.uploadProgress = 0
      console.error('上传失败:', err)
      ElMessage.error('上传失败')
    },
    processFile(filePath) {
      this.$axios
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
    },
    handleLimitChange() {
      this.currentPage = 1
      this.fetchData()
    },
    handleSizeChange(newSize) {
      this.pageSize = newSize
      this.fetchData()
    },
    handleCurrentChange(newPage) {
      this.currentPage = newPage
      this.fetchData()
    }
  }
}
</script>