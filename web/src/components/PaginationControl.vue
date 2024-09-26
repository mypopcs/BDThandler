<template>
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
</template>

<script>
import { mapState, mapMutations, mapActions } from 'vuex'

export default {
  name: 'PaginationControl',
  computed: {
    ...mapState(['currentPage', 'pageSize', 'total', 'dataLimit'])
  },
  methods: {
    ...mapMutations(['setCurrentPage', 'setPageSize', 'setDataLimit']),
    ...mapActions(['fetchData']),
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