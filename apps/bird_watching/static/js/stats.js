"use strict";

let app = new Vue({
    el: '#app',
    data: {
        stats: [],
        details: [],
        trends: [],
        search_query: '',
        search_results: [],
        selected_species: '',
    },
    methods: {
        getStat(order = "recent") {
            this.selected_species = "";
            d3.select("#my_dataviz").selectAll("*").remove();
            axios.get(`${window.get_stats_url}/${order}`).then((res) => {
                this.stats = res.data.species_list;
                console.log("STATS:", this.stats);
            }).catch(err => {
                console.log("Failed at getStat", err);
            });
        },

        getSpeciesDetails(species_name) {
            this.selected_species = species_name;
            axios.get(`${window.get_species_details_url}/${species_name}`).then((res) => {
                this.details = res.data.sightings_data;
                console.log("DETAILS:", this.details);
                getGraph(this.details);
            }).catch(err => {
                console.log("Failed at getSpeciesDetails", err);
            });
        },

        getTrend() {
            this.selected_species = "";
            axios.get(window.get_trends_url).then((res) => {
                this.trends = res.data.trend_data;
                console.log("Trend:", this.trends);
                getGraph(this.trends);
            }).catch(err => {
                console.log("Failed at getTrend", err);
            });
        },

        searchSpecies() {
            axios.get(window.search_species_url, { params: { query: this.search_query } }).then((res) => {
                this.search_results = res.data.species_list;
                console.log("SEARCH RESULTS:", this.search_results);
            }).catch(err => {
                console.log("Failed at searchSpecies", err);
            });
        },
    },
    created() {
        this.getStat('recent');
    }
});

const getGraph = (data) => {
    console.log("Graph Data:", data);

    d3.select("#my_dataviz").selectAll("*").remove();

    var margin = { top: 30, right: 30, bottom: 70, left: 60 },
        width = 460 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;

    var svg = d3.select("#my_dataviz")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var x = d3.scaleBand()
        .range([0, width])
        .domain(data.map(function (d) { return d.date; }))
        .padding(0.2);
    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("transform", "translate(-10,0)rotate(-45)")
        .style("text-anchor", "end");

    var y = d3.scaleLinear()
        .domain([0, Math.max(...data.map(function (d) { return parseInt(d.count); })) + 1])
        .range([height, 0]);
    svg.append("g")
        .call(d3.axisLeft(y));

    svg.selectAll("mybar")
        .data(data)
        .enter()
        .append("rect")
        .attr("x", function (d) { return x(d.date); })
        .attr("y", function (d) { return y(parseInt(d.count)); })
        .attr("width", x.bandwidth())
        .attr("height", function (d) { return height - y(parseInt(d.count)); })
        .attr("fill", "#69b3a2");
}
