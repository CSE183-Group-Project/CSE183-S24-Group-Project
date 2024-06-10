"use strict";


let app = {
};

app.init = () => {
    app.map = L.map('map').setView([51.505, -0.09], 13);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(app.map);

    app.updateHeatmap = (species = '') => {
        const url = `${get_checklist_data_url}?species=${species}`//`/bird_watching/get_checklist_data?species=${species}`;
        axios.get(url)
            .then(response => {
                const data = response.data;
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
        axios.get(get_species_url) //'/bird_watching/get_species'
            .then(response => {
                const species = response.data;
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
    app.updateHeatmap();

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const userLocation = [lat, lon];

            app.map.setView(userLocation, 13);

            L.marker(userLocation).addTo(app.map)
                .openPopup();
        }, error => {
            console.error("Error getting user's location: ", error);
        });
    } else {
        console.error('Geolocation is not supported by this browser.');
    };

    // Init FeatureGroup
    app.drawnItems = new L.FeatureGroup();
    app.map.addLayer(app.drawnItems);

    // Init draw control for FeatureGroup component
    let drawControl = new L.Control.Draw({
        edit: {
            featureGroup: app.drawnItems
        },
        draw: {
            rectangle: true,
            polyline: false,
            polygon: false,
            circle: false,
            marker: false,
            circlemarker: false,
        }
    });
    app.map.addControl(drawControl);

    app.map.on(L.Draw.Event.CREATED, function(event) {
        let layer = event.layer;
        app.drawnItems.addLayer(layer);
    })
};

// Define the Vue.js app data and methods
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
