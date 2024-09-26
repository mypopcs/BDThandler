<template>
  <el-form
    style="max-width: 980px"
    label-position="top"
    label-width="auto"
    model="sizeForm"
  >
    <el-form-item label="正则匹配">
      <div
        v-for="(regex, index) in regexList"
        :key="regex.id"
        style="width: 100%; display: flex; margin-bottom: 8px"
      >
        <el-input
          v-model="regex.description"
          placeholder="正则用途描述"
          style="width: 560px; margin-right: 16px"
        ></el-input>
        <el-input
          v-model="regex.pattern"
          placeholder="请输入正则表达式"
          style="margin-right: 16px"
        ></el-input>
        <el-button type="danger" @click="removeRegex(index)"> 删除 </el-button>
      </div>
    </el-form-item>
    <el-form-item label="同义词词典">
      <el-input
        placeholder="请输入同义词，格式为'替换词:待替换词1,待替换词2'，每行一组"
        v-model="synonymText"
        type="textarea"
        :rows="10"
      ></el-input>
    </el-form-item>
    <el-form-item label="停用词词典">
      <el-input
        placeholder="请输入停用词，每行一个"
        v-model="stopwordText"
        type="textarea"
        :rows="10"
      ></el-input>
    </el-form-item>
    <el-form-item style="margin-top: 16px">
      <el-button @click="addRegex">添加正则</el-button>
      <el-button
        type="primary"
        @click="submitAnalysisConfig"
        :loading="isLoading"
        >{{ isLoading ? '分析中...' : '开始分析' }}</el-button
      >
    </el-form-item>
  </el-form>
</template>

<script>
import Dexie from 'dexie'
import axios from 'axios'

const db = new Dexie('regexConfigDB')
db.version(1).stores({
  regexList: '++id, pattern, description',
  synonyms: '++id, text',
  stopwords: '++id, text'
})

export default {
  data() {
    return {
      regexList: [], //初始化正则
      isLoading: false,
      progress: 0,
      synonymText: '',
      stopwordText: ''
    }
  },
  created() {
    this.loadAnalysisConfig()
  },
  methods: {
    addRegex() {
      const newRegex = { id: Date.now(), pattern: '', description: '' } // 使用时间戳作为临时ID
      this.regexList.push(newRegex)
    },
    async removeRegex(index) {
      const regex = this.regexList[index]
      this.regexList.splice(index, 1)

      // 如果正则表达式有ID（已保存到数据库），则从数据库中删除
      if (regex.id && typeof regex.id === 'number') {
        try {
          await db.regexList.delete(regex.id)
          console.log(`Deleted regex with id ${regex.id} from database`)
        } catch (error) {
          console.error('Error deleting regex from database:', error)
          this.$message.error('从数据库删除正则表达式失败')
        }
      }

      // 确保列表中至少有一个正则表达式
      if (this.regexList.length === 0) {
        this.addRegex()
      }
    },
    async loadAnalysisConfig() {
      try {
        const regexData = await db.regexList.toArray()
        this.regexList =
          regexData.length > 0
            ? regexData
            : [{ id: Date.now(), pattern: '', description: '' }]
        const synonyms = await db.synonyms.toArray()
        this.synonymText = synonyms.map((s) => s.text).join('\n')
        const stopwords = await db.stopwords.toArray()
        this.stopwordText = stopwords.map((s) => s.text).join('\n')
      } catch (error) {
        this.$message.error('加载配置失败', error)
        this.regexList = [{ id: Date.now(), pattern: '', description: '' }]
      }
    },
    async submitAnalysisConfig() {
      if (this.regexList.length === 0) {
        this.$message.warning('请至少添加一个正则表达式')
        return
      }
      //上传数据
      this.isLoading = true
      //保存到本地
      try {
        await db.transaction(
          'rw',
          db.regexList,
          db.synonyms,
          db.stopwords,
          async () => {
            // 清除旧数据
            await db.regexList.clear()
            await db.synonyms.clear()
            await db.stopwords.clear()
            // 添加新数据，并更新本地列表中的ID
            for (let regex of this.regexList) {
              const id = await db.regexList.add({
                pattern: regex.pattern,
                description: regex.description
              })
              regex.id = id
            }
            await db.synonyms.add({ text: this.synonymText })
            await db.stopwords.add({ text: this.stopwordText })
          }
        )
        // 准备后端数据
        const analysisConfig = {
          regexList: this.regexList.map(({ pattern }) => ({ regex: pattern })),
          //同义词
          // synonyms: this.synonymText
          //   .split('\n')
          //   .filter(Boolean)
          //   .map((line) => line.split(',').map((word) => word.trim())),
          synonyms: this.synonymText
            .split('\n')
            .filter(Boolean)
            .map((line) => {
              const [replacement, words] = line.split(':')
              return {
                replacement: replacement.trim(),
                words: words.split(',').map((word) => word.trim())
              }
            }),
          stopwords: this.stopwordText
            .split('\n')
            .filter(Boolean)
            .map((word) => word.trim())
        }
        // Send to backend
        const response = await axios.post(
          'http://localhost:5000/update_analysis_config',
          analysisConfig
        )
        if (response.data.success) {
          this.$message.success('分析成功')
          setTimeout(() => {
            window.location.reload()
          }, 1000)
        } else {
          this.$message.error('分析失败')
        }
        // this.$message.success('配置已保存')
      } catch (error) {
        console.error('Error updating analysis configuration:', error)
        this.$message.error('更新分析配置失败')
      } finally {
        this.isLoading = false
      }
      // const regexData = this.regexList.map(({ pattern }) => ({
      //   regex: pattern
      // }))

      // try {
      //   const response = await axios.post(
      //     'http://localhost:5000/update_regex',
      //     regexData
      //   )
      //   if (response.data.success) {
      //     this.$message.success('分析成功')
      //     // 自动刷新页面
      //     setTimeout(() => {
      //       window.location.reload()
      //     }, 1000)
      //   } else {
      //     this.$message.error('分析失败')
      //   }
      // } catch (error) {
      //   console.error('Error sending regex to backend:', error)
      //   this.$message.error('发送正则表达式到后端失败')
      // } finally {
      //   this.isLoading = false
      // }
    }
  }
}
</script>