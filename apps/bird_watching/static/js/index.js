"use strict";

// Define the app object
let app = {};

// Initialize the map and heatmap
app.init = () => {
    // Initialize the Leaflet map
    app.map = L.map('map').setView([51.505, -0.09], 13);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(app.map);

    // Function to update the heatmap based on species
    app.updateHeatmap = (species = '') => {
        fetch(`/bird_watching/get_checklist_data?species=${species}`)
            .then(response => response.json())
            .then(data => {
                if (app.heatmapLayer) {
                    app.map.removeLayer(app.heatmapLayer);
                }
                const heatmapData = data.map(d => [d.lat, d.lng, d.count]);
                app.heatmapLayer = L.heatLayer(heatmapData, {
                    radius: 20, 
                    blur: 15,   
                    maxZoom: 1, 
                    gradient: {
                        0.2: 'blue',
                        0.4: 'lime',
                        0.6: 'yellow',
                        0.8: 'orange',
                        1.0: 'red'
                    },
                    max: 1.0 
                }).addTo(app.map);
            })
            .catch(error => console.error('Error fetching heatmap data:', error));
    };

    // Initialize autocomplete
    const initAutocomplete = () => {
        fetch('/bird_watching/get_species')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(species => {
                const speciesNames = species.map(s => s.common_name);
                $("#species-autocomplete").autocomplete({
                    source: speciesNames,
                    select: (event, ui) => {
                        console.log('Selected species:', ui.item.value);
                        app.updateHeatmap(ui.item.value);
                    }
                });
            })
            .catch(error => console.error('Error fetching species data:', error));
    };

    initAutocomplete();

    // Get the user's location and set the map view to it
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const userLocation = [lat, lon];

            // Update the map view to the user's location
            app.map.setView(userLocation, 13);

            // Add a marker to the user's location
            L.marker(userLocation).addTo(app.map)
                .openPopup();
        }, error => {
            console.error("Error getting user's location: ", error);
        });
    } else {
        console.error('Geolocation is not supported by this browser.');
    }
};

app.data = {
    data: function() {
        return {
            my_value: 1,
        };
    },
    methods: {
        my_function: function() {
            this.my_value += 1;
        },
    },
    mounted() {
        app.init();
    },
};

app.vue = Vue.createApp(app.data).mount("#app");


app.load_data = function () {
    axios.get(my_callback_url).then(function (r) {
        app.vue.my_value = r.data.my_value;
    });
}


app.load_data();
