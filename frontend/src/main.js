import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import App from './App.vue'
import router from './router'
import { useUiStore } from './stores/ui'
import './assets/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

// Sync persisted theme onto <html> (index.html already pre-paints it to avoid a flash).
const ui = useUiStore()
ui.applyTheme()

app.mount('#app')
