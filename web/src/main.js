import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import mitt from 'mitt'
import store from './workers/store'


const emitter = mitt()
const app = createApp(App)
app.use(ElementPlus)
app.use(store)

app.config.globalProperties.emitter = emitter

app.mount('#app')
