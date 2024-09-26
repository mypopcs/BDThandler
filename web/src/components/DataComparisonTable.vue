<template>
  <div>
    <el-table :data="paginatedCombinedData">
      <el-table-column prop="commentA" label="源数据"> </el-table-column>
      <el-table-column prop="commentB" label="清洗后数据"> </el-table-column>
    </el-table>
    <el-row :gutter="20" style="padding: 16px 0">
      <el-col :span="2">
        <el-select v-model="dataLimit" @change="handleLimitChange">
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
import { mapGetters, mapState, mapMutations, mapActions } from 'vuex'

export default {
  name: 'DataComparisonTable',
  computed: {
    //计算属性
    ...mapGetters(['paginatedCombinedData']),
    ...mapState(['currentPage', 'pageSize', 'total', 'dataLimit'])
  },
  created() {
    this.fetchInitialData() // 组件创建时获取初始数据
  },
  //定义组件的方法，用来处理组件的逻辑，例如响应用户的操作、与服务器通信、修改组件的状态等。
  methods: {
    ...mapMutations(['setCurrentPage', 'setPageSize', 'setDataLimit']),
    ...mapActions(['fetchData', 'fetchAnalyzedData']),
    async fetchInitialData() {
      await this.fetchData()
      await this.fetchAnalyzedData()
    },
    handleLimitChange(value) {
      this.setDataLimit(value)
      this.setCurrentPage(1)
      this.fetchData()
    },
    handleSizeChange(value) {
      this.setPageSize(value)
      this.fetchData()
    },
    handleCurrentChange(value) {
      this.setCurrentPage(value)
      this.fetchData()
    }
  }
}
</script>