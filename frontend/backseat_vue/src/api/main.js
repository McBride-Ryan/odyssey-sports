import axios from "axios";

export const FantasyFootballAPI = {
    fetchData() {
        return axios.get('http://127.0.0.1:8000/test');
    },
};