import { createRouter, createWebHistory } from 'vue-router'


import Home from '../views/Home.vue'
import About from '../views/About.vue'
import Register from '../views/Auth/Register.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/about',
    name: 'About',
    component: About
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    // component: () => import(/* webpackChunkName: "about" */ '../views/About.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
//   {
//     path: '/login',
//     name: 'LogIn',
//     component: Login
//   },
//   {
//     path: '/my-account',
//     name: 'MyAccount',
//     component: MyAccount,
//     meta: {
//         requireLogin: true
//     }
//   },
//   {
//     path: '/search',
//     name: 'Search',
//     component: Search
//   },
//   {
//     path: '/cart',
//     name: 'Cart',
//     component: Cart
//   },
//   {
//     path: '/cart/success',
//     name: 'Success',
//     component: Success
//   },
//   {
//     path: '/cart/checkout',
//     name: 'Checkout',
//     component: Checkout,
//     meta: {
//         requireLogin: true
//     }
//   },
//   {
//     path: '/:category_slug/:product_slug',
//     name: 'Product',
//     component: Product
//   },
//   {
//     path: '/:category_slug',
//     name: 'Category',
//     component: Category
//   }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})
// const router = VueRouter.createRouter({
//   // 4. Provide the history implementation to use. We are using the hash history for simplicity here.
//   history: VueRouter.createWebHashHistory(),
//   routes, // short for `routes: routes`
// })


// router.beforeEach((to, from, next) => {
//   if (to.matched.some(record => record.meta.requireLogin) && !store.state.isAuthenticated) {
//     next({ name: 'LogIn', query: { to: to.path } });
//   } else {
//     next()
//   }
// })

export default router