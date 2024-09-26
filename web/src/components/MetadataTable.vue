<template>
  <div>
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
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'MetadataTable',
  data() {
    return {
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
  computed: {
    ...mapState(['tableData', 'tableColumns', 'loading'])
  }
}
</script>