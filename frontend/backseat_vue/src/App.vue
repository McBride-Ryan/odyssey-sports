<script>
import FantasyFootball from './views/sportsAPI/FantasyFootball.vue';
export default {
  components: { FantasyFootball }
}
</script>

<template>
  <nav
    class="w-full grid md:justify-items-stretch lg:grid-cols-3 lg:items-center py-4 px-6 md:px-16 content-center inline-grid">
    <div class="lg:flex hidden">
      <div class="relative justify-self-start lg:inline-grid items-center rounded-md py-2">
        <div class="flex inline-flex absolute">
          <button>
            <svg class="z-50 hover:cursor-pointer fill-current w-5 text-gray-500 ml-2 pr-1 " viewBox="0 0 24 24">
              <path class="heroicon-ui"
                d="M16.32 14.9l5.39 5.4a1 1 0 01-1.42 1.4l-5.38-5.38a8 8 0 111.41-1.41zM10 16a6 6 0 100-12 6 6 0 000 12z" />
            </svg>
          </button>
          <form method="GET" action="/">
            <input class="z-0 rounded-md text-sm py-2 focus:outline-none focus:shadow-outline pl-4" type="text"
              name="search" placeholder="Search...">
          </form>
        </div>
      </div>
    </div>

    <div class="md:mt-0 grid justify-self-center inline-grid">
      <router-link to="/">
        <h1 class="text-4xl text-white">Django-Vue</h1>
      </router-link>
    </div>
    <div class="md:mt-0 grid items-center justify-self-end lg:grid">
      <div class=" top-0 right-0 px-6 py-4 sm:block">

        <div>
          <router-link to="/login" class="text-sm text-white underline">Log in</router-link>
          <span class="text-white">|</span>
          <router-link to="/register" class="ml-4 text-sm text-white underline">Register</router-link>
        </div>
      </div>
    </div>
  </nav>



  <router-link to="/about" class="text-blue-500">
    <span>About</span>
  </router-link>



  <section>
    <router-view></router-view>
  </section>
</template>

<style scoped>
nav {
  background-color: black;
}
</style>
