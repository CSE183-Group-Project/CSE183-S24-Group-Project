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
  data: function() {
      return {
          stats: [],
          details: [],
          trends: [],
          search_query: '',
          search_results: [],
          selected_species: '',
      };
  },
  methods: {
      getStat(order = "recent"){
        this.selected_species = ""
          d3.select("#my_dataviz").selectAll("*").remove();
          axios.get(get_stats_url +"/"+order).then((res) => {
              this.stats = res.data.species_list;
              console.log("STATS:", this.stats);
          }).catch(err => {
              console.log("Failed at getStats in index.js", err);
          });
      },

      getSpeciesDetails(species_name){
        this.selected_species = species_name;
          axios.get(get_species_details_url + "/" + species_name).then((res) => {
              this.details = res.data.sightings_data;
              console.log("DETAILS:", this.details);
              getGraph(this.details);
          }).catch(err => {
              console.log("Failed at getSpeciesDetails in index.js", err);
          });
      },

      getTrend(){
          this.selected_species = ""
          axios.get(get_trends_url).then((res) => {
              this.trends = res.data.trend_data;
              console.log("Trend:", this.trends);
              getGraph(this.trends);
          }).catch(err => {
              console.log("Failed at getTrend in index.js", err);
          });
      },

      searchSpecies(){
          axios.get(search_species_url, {params: {query: this.search_query}}).then((res) => {
              this.search_results = res.data.species_list;
              console.log("SEARCH RESULTS:", this.search_results);
          }).catch(err => {
              console.log("Failed at searchSpecies in index.js", err);
          });
      },
  }
};

app.vue = Vue.createApp(app.data).mount("#app");

app.load_data = function () {
  axios.get(get_stats_url+"/recent").then((res) => {
      app.vue.stats = res.data.species_list;
      console.log("LOAD:", app.vue.stats);
  }).catch(err => {
      console.log("Failed at LOAD in index.js", err);
  });
}

app.load_data();

const getGraph = (data) => {
  console.log("Graph Data:", data);

  // Clear previous graph
  d3.select("#my_dataviz").selectAll("*").remove();

  // set the dimensions and margins of the graph


  // set the dimensions and margins of the graph
  var margin = {top: 30, right: 30, bottom: 70, left: 60},
      width = 460 - margin.left - margin.right,
      height = 400 - margin.top - margin.bottom;

  // append the svg object to the body of the page
  var svg = d3.select("#my_dataviz")
    .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

  

  // X axis
  var x = d3.scaleBand()
    .range([ 0, width ])
    .domain(data.map(function(d) { return d.date; }))
    .padding(0.2);
  svg.append("g")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(x))
    .selectAll("text")
      .attr("transform", "translate(-10,0)rotate(-45)")
      .style("text-anchor", "end");

  console.log("MAX VALUE:", data.map(function(d){return parseInt(d.count)}))
  // Add Y axis
  var y = d3.scaleLinear()
    .domain([0, Math.max(...data.map(function(d){return parseInt(d.count)}))+1])
    .range([ height, 0]);
  svg.append("g")
    .call(d3.axisLeft(y));

  // Bars
  svg.selectAll("mybar")
    .data(data)
    .enter()
    .append("rect")
      .attr("x", function(d) { return x(d.date); })
      .attr("y", function(d) { return y(parseInt(d.count))})
      .attr("width", x.bandwidth())
      .attr("height", function(d) { return height - y(parseInt(d.count)); })
      .attr("fill", "#69b3a2")

  }
