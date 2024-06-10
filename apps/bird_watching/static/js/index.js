"use strict";

let app = {
  currentMarker: null,
};

app.init = () => {
  let log = null;
  let lat = null;
  app.map = L.map("map");
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution:
      '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(app.map);

  app.updateHeatmap = (species = "") => {
    const url = `/bird_watching/get_checklist_data?species=${species}`;
    axios
      .get(url)
      .then((response) => {
        const data = response.data.data;
        if (app.heatmapLayer) {
          app.map.removeLayer(app.heatmapLayer);
        }
        const heatmapData = data.slice(1).map((d) => [d.lat, d.lng, d.count]);
        app.heatmapLayer = L.heatLayer(heatmapData, {
          radius: 20,
          blur: 15,
          maxZoom: 1,
          gradient: {
            0.2: "blue",
            0.4: "lime",
            0.6: "yellow",
            0.8: "orange",
            1.0: "red",
          },
          max: 1.0,
        }).addTo(app.map);
      })
      .catch((error) => console.error("Error fetching heatmap data:", error));
  };

  // Initialize autocomplete
  const initAutocomplete = () => {
    axios
      .get("/bird_watching/get_species")
      .then((response) => {
        const species = response.data;
        const speciesNames = species.map((s) => s.common_name);
        $("#species-autocomplete").autocomplete({
          source: speciesNames,
          select: (event, ui) => {
            console.log("Selected species:", ui.item.value);
            app.updateHeatmap(ui.item.value);
          },
        });
      })
      .catch((error) => console.error("Error fetching species data:", error));
  };

  initAutocomplete();
  app.updateHeatmap();

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        const userLocation = [lat, lon];

        app.map.setView(userLocation, 13);
      },
      (error) => {
        console.error("Error getting user's location: ", error);
      },
    );
  } else {
    console.error("Geolocation is not supported by this browser.");
  }

  // Initialize Leaflet Draw
  const drawnItems = new L.FeatureGroup();
  app.map.addLayer(drawnItems);

  const drawControl = new L.Control.Draw({
    draw: {
      polyline: false,
      polygon: false,
      circle: false,
      marker: false,
      circlemarker: false,
      rectangle: true,
    },
    edit: {
      featureGroup: drawnItems,
      remove: true,
    },
  });

  app.map.addControl(drawControl);

  app.map.on(L.Draw.Event.CREATED, (event) => {
    const layer = event.layer;
    drawnItems.addLayer(layer);
    app.selectedBounds = layer.getBounds();
  });

  document.getElementById("stats-button").addEventListener("click", () => {
    if (app.selectedBounds) {
      const ne = app.selectedBounds.getNorthEast();
      const sw = app.selectedBounds.getSouthWest();
      const url = `/bird_watching/statistics?ne_lat=${ne.lat}&ne_lng=${ne.lng}&sw_lat=${sw.lat}&sw_lng=${sw.lng}`;
      window.location.href = url;
    } else {
      alert("Please draw a rectangle on the map to select a region.");
    }
  });

  app.map.on("click", function (e) {
    const latlng = e.latlng;

    // Remove existing marker if present
    if (app.currentMarker) {
      app.map.removeLayer(app.currentMarker);
    }

    // Add new marker
    app.currentMarker = L.marker(latlng).addTo(app.map);
    lat = latlng.lat;
    log = latlng.lng;
    const url = `/bird_watching/checklist?lat=${lat}&lng=${log}`;
    app.currentMarker
      .bindPopup(`<a href="${url}" class="button is-link">Enter Checklist</a>`)
      .openPopup();
  });
};

// Define the Vue.js app data and methods
app.data = {
  data: function () {
    return {
      my_value: 1,
    };
  },
  methods: {
    my_function: function () {
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
};

app.load_data();
