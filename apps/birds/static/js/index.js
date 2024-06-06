"use strict";
let app = {};

app.data = {
    data: function() {
        return {
            stats: [],
            details: [],
            trends: [],
        };
    },
    methods: {
        getStat(){
            axios.get(get_stats_url).then((res) => {
                this.stats = res.data.species_list;
                console.log("STATS:", this.stats);
            }).catch(err => {
                console.log("Failed at getStats in index.js", err);
            });
        },

        getSpeciesDetails(species_name){
            axios.get(get_species_details_url + "/" + species_name).then((res) => {
                this.details = res.data.sightings_data;
                console.log("DETAILS:", this.details);
                getGraph(this.details);
            }).catch(err => {
                console.log("Failed at getSpeciesDetails in index.js", err);
            });
        },

        getTrend(){
            axios.get(get_trends_url).then((res) => {
                this.trends = res.data.trend_data;
                console.log("Trend:", this.trends);
                getGraph(this.trends);
            }).catch(err => {
                console.log("Failed at getTrend in index.js", err);
            });
        },
    }
};

app.vue = Vue.createApp(app.data).mount("#app");

app.load_data = function () {
    axios.get(get_stats_url).then((res) => {
        app.vue.stats = res.data.species_list;
        console.log("LOAD:", app.vue.stats);
    }).catch(err => {
        console.log("Failed at LOAD in index.js", err);
    });
}

app.load_data();

const getGraph = (data) => {
    console.log("Graph Data:", data);

    // Clear previous graph IDK IF THIS IS NESSESSARY
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