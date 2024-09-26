<!-- App.vue -->
<template>
  <div>
    <h1>Database Data</h1>
    <h2>上传数据</h2>
    <UploadBar></UploadBar>
    <h2>分析配置</h2>
    <AnalysisConfig></AnalysisConfig>
    <h2>数据预览</h2>
    <DataComparisonTable></DataComparisonTable>
  </div>
</template>

<script>
import UploadBar from './components/Upload.vue'
import DataComparisonTable from './components/DataComparisonTable.vue'
import AnalysisConfig from './components/AnalysisConfig.vue'

export default {
  name: 'App',
  components: {
    UploadBar,
    DataComparisonTable,
    AnalysisConfig
  }
}
</script>