<script>
import { FantasyFootballAPI } from '../../api/main.js'
export default {
  name: 'FantasyFootball',
  async created() {
    console.log( 'loading' )
    this.isLoading = true;
    let { data } = await FantasyFootballAPI.fetchData();
    this.players = data.context
    this.isLoading = true;
  },
  data() {
    return {
      isLoading: false,
      article: {
        body: "",
        category_id: "",
        created: "",
        id: "",
        title: "",
        updated: "",
        user_id: "",
      },
      players: [],
      headers: [
        { text: "PosRank", value: "PosRank", width: 10, sortable: true },
        { text: "Player", value: "Player", width: 200, sortable: true },
        { text: "Tm", value: "Tm", sortable: true },
        { text: "Receiving_Tgt", value: "Receiving_Tgt", sortable: true },
        { text: "Receiving_Rec", value: "Receiving_Rec", sortable: true },
        { text: "Receiving_Yds", value: "Receiving_Yds", sortable: true },
        { text: "Receiving_YR", value: "Receiving_YR", sortable: true },
        { text: "Receiving_TD", value: "Receiving_TD", sortable: true },
        { text: "PPR", value: "PPR", sortable: true },
      ],
    };
  },
};
</script>

<template>
  <EasyDataTable :headers="headers" :items="players" :rows-per-page="10" :sort-by="sortBy" :sort-type="sortType"
    buttons-pagination alternating border-cell>

    <template #header-PosRank="header">
      <div>
        <span>PosRank</span>
      </div>
    </template>
    <template #item-PosRank="player">
      <span>{{ player.PosRank }}</span>
    </template>

    <template #header-Player="header">
      <div>
        <span>Player</span>
      </div>
    </template>
    <template #item-Player="player">
      <span>{{ player.Player }}</span>
    </template>

    <template #header-Tm="header">
      <div>
        <span>Tm</span>
      </div>
    </template>
    <template #item-Tm="player">
      <span>{{ player.Tm }}</span>
    </template>



    <template #header-Receiving_Tgt="header">
      <div>
        <span>Receiving_Tgt</span>
      </div>
    </template>
    <template #item-Receiving_Tgt="player">
      <span>{{ player.Receiving_Tgt }}</span>
    </template>

    <template #header-Receiving_Rec="header">
      <div>
        <span>Receiving_Rec</span>
      </div>
    </template>
    <template #item-Receiving_Rec="player">
      <span>{{ player.Receiving_Rec }}</span>
    </template>

    <template #header-Receiving_Yds="header">
      <div>
        <span>Receiving_Yds</span>
      </div>
    </template>
    <template #item-Receiving_Yds="player">
      <span>{{ player.Receiving_Yds }}</span>
    </template>

    <template #header-Receiving_YR="header">
      <div>
        <span>Receiving_YR</span>
      </div>
    </template>
    <template #item-Receiving_YR="player">
      <span>{{ player.Receiving_YR }}</span>
    </template>

    <template #header-Receiving_TD="header">
      <div>
        <span>Receiving_TD</span>
      </div>
    </template>
    <template #item-Receiving_TD="player">
      <span>{{ player.Receiving_TD }}</span>
    </template>

    <template #header-PPR="header">
      <div>
        <span>PPR</span>
      </div>
    </template>
    <template #item-PPR="player">
      <span>{{ player.PPR }}</span>
    </template>

  </EasyDataTable>
</template>