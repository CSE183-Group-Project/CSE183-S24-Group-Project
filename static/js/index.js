"use strict";

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
//let app = {};

//------- code from Leaflet ------------------

let map;

let app = {}

app.init = () => {
    app.map = L.map('map').setView([51.505, -0.09], 13)
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright"OpenStreetMap</a>'
    }).addTo(app.map);
    // Adds listener
    //app.map.on('click', app.click_listener);
    //app.map.on('dbclick', app.dbclick_listener);
};

//----- end of Leaflet ----------------------

// beginning of already contained code from starter_vue3
/*let app = {};
app.data = {    
    data: function() {
        return {
            // Complete as you see fit.
            my_value: 1, // This is an example.
        };
    },
    methods: {
        // Complete as you see fit.
        my_function: function() {
            // This is an example.
            this.my_value += 1;
        },
    }
};
*/
app.vue = Vue.createApp(app.data).mount("#app");

app.load_data = function () {
    axios.get(my_callback_url).then(function (r) {
        app.vue.my_value = r.data.my_value;
    });
}

app.load_data();

