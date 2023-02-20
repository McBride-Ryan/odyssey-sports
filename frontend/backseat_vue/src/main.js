import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from '../src/router'
import axios from 'axios'
import App from './App.vue'
import Vue3EasyDataTable from 'vue3-easy-data-table';
import 'vue3-easy-data-table/dist/style.css';


const app = createApp(App)

app.component('EasyDataTable', Vue3EasyDataTable)
    .use(createPinia())
    .use(router, axios)
    .mount('#app')
