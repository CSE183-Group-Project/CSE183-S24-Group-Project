document.addEventListener('DOMContentLoaded', function() {
    new Vue({
      el: '#app',
      data: {
        query: '',
        species: [],
        filteredSpecies: []
      },
      methods: {
        searchSpecies: function() {
          fetch(load_species_url + '?query=' + this.query)
            .then(response => response.json())
            .then(data => {
              this.species = data.species.map(species => ({ ...species, count: 0 }));
              this.filteredSpecies = this.species;
            });
        },
        increment: function(species) {
          species.count += 1;
        },
        submitChecklist: function() {
          const checklist = {
            sampling_event_identifier: 'event1', // Replace with dynamic value
            latitude: 0, // Replace with dynamic value
            longitude: 0, // Replace with dynamic value
            observation_date: new Date().toISOString().split('T')[0], // Replace with dynamic value
            time_observation: '12:00', // Replace with dynamic value
            observer_id: 1, // Replace with dynamic value
            duration_minute: 60, // Replace with dynamic value
            species: this.species.filter(s => s.count > 0).map(s => ({
              common_name: s.common_name,
              observation_count: s.count
            }))
          };
  
          fetch(submit_checklist_url, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(checklist)
          })
          .then(response => response.json())
          .then(data => {
            alert(data.message);
          });
        }
      }
    });
  });
  