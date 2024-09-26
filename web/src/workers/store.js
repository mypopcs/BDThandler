import { createStore } from 'vuex'
import axios from 'axios'
import Dexie from 'dexie'

// 初始化 Dexie 数据库
const db = new Dexie('AnalyzedDatabase')
db.version(1).stores({
  analyzedData: '++id'
})

export default createStore({
  state: {
    sourceData: [], // 原始数据
    analyzedData: [], // 分析后的数据
    tableColumns: [], // 表格列
    total: 0, // 总数据量
    loading: false, // 数据加载状态
    currentPage: 1,
    pageSize: 20,
    dataLimit: 500, //数据限制量
  },
  mutations: { // 响应式同步状态变化
    setSourceData(state, data) { // 设置表格数据
      state.sourceData = data
    },
    setAnalyzedData(state, data) { // 设置分析后的数据
      state.analyzedData = data
    },
    setTableColumns(state, columns) { // 设置表格列
      state.tableColumns = columns
    },
    setTotal(state, total) { // 设置总数据量
      state.total = total
    },
    setLoading(state, loading) { // 设置加载状态
      state.loading = loading
    },
    setCurrentPage(state, page) { // 设置当前页
      state.currentPage = page
    },
    setPageSize(state, size) { // 设置每页数据量
      state.pageSize = size
    },
    setDataLimit(state, limit) { // 设置数据限制
      state.dataLimit = limit
    },
  },
  actions: { // 动作函数用于处理异步操作
    async fetchData({ commit, state }) { // 获取数据的动作
      commit('setLoading', true) // 开始加载数据，设置 loading 状态为 true
      try {
        const response = await axios.get(`http://localhost:5000/get_source_data`, {
          params: {
            limit: state.dataLimit,
            page: state.currentPage,
            per_page: state.pageSize
          }
        })
        // 请求成功，使用 commit 调用 mutations 更新状态
        commit('setSourceData', response.data.data)
        commit('setTotal', response.data.total)
        commit('setTableColumns', response.data.columns)
      } catch (error) {
        console.error('Error fetching data:', error)
      }
      commit('setLoading', false)
    },
    // 获取分析后数据的动作
    async fetchAnalyzedData({ commit }) {
      try {
        await db.analyzedData.clear() // 清空数据库中的分析数据
        const response = await axios.get(`http://localhost:5000/get_analyzed_data`)
        if (response.data.data && response.data.data.length > 0) {
          await db.analyzedData.bulkAdd(response.data.data); // 只有在有数据时才添加到本地数据库
        }
        const analyzedData = await db.analyzedData.toArray() // 从数据库中获取所有分析数据
        commit('setAnalyzedData', analyzedData); // 更新 Vuex 状态
        console.log('分析后的数据:', analyzedData);
      } catch (error) {
        console.error('Error fetching analyzed data:', error)
        if (error.response) {
          console.error('Error details:', error.response.data);
        }
        // 出错时也要清空本地数据和更新状态
        await db.analyzedData.clear();
        commit('setAnalyzedData', []);
      }
    }
  },
  getters: { // 计算属性
    combinedData: (state) => { // 将原始数据和分析后的数据合并
      return state.sourceData.map((sourceItem, index) => ({
        commentA: sourceItem['评论内容'] || '',
        commentB: (state.analyzedData[index] && state.analyzedData[index]['评论内容']) || ''
      }))
    },
    paginatedCombinedData: (state, getters) => { // 获取分页后的合并数据
      const start = (state.currentPage - 1) * state.pageSize
      const end = start + state.pageSize
      return getters.combinedData.slice(start, end)
    },
  }
})