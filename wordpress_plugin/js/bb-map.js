/* Plot the data viz map */

// Fetch the data
$(function() {
	// Build the map
	if(navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(function(position, error) {
			var lat = (!error) ? position.coords.latitude: 53.4668;
			var lon = (!error) ? position.coords.longitude: -2.2339;
		
			plotMapData(lat, lon);
		});
	} else {
		plotMapData(53.4668, -2.2339);
	}	
});

function plotMapData(lat, lon) {
	// Show the loading message
	setLoader(1, 'Loading data...');

	// Set the map
	var mymap = L.map('bb-mapid');

	//var dataURL = "http://130.88.198.51/bb/api/bb.json";
	var dataURL = "testdata/bb.json";
	
	var markerCount = 0;
	
	$.getJSON(dataURL, function(data) {
		// When the data is loaded, and the map is loaded, plot the data points
		console.log(0);
		
		mymap.on('load', function(e) {
			var worker = new Worker('js/bb-plot-data.js');
			worker.postMessage(data);
			
			worker.onmessage = function(event) {
				//console.log(event.data);
				if(!event.data.complete) {
					// Plot the marker
					var marker = L.marker([event.data.latitude, event.data.longitude]).addTo(mymap);

					// Add the marker popup
					marker.bindPopup("<b>"+event.data['Time uploaded to server']+"</b><br>"+event.data['Gender']+"").openPopup();
					
					// Increase the marker count
					markerCount++;
					$('#bb-loader-count').text(markerCount);
				} else {
					// The marker plotting has finished, recenter the map and hide the loader
					mymap.setView([lat, lon], 10);
					// Hide the loading message
					setLoader(0, 'Data loaded.');
				}
			};
   		});
   		
   		mymap.setView([lat, lon], 10);
   		
   		L.tileLayer('https://api.mapbox.com/styles/v1/robdunne/ciofqs6ug005dbzmd9a6c8pwe/tiles/{z}/{x}/{y}?access_token=pk.eyJ1Ijoicm9iZHVubmUiLCJhIjoiY2lvZnBqYnZ0MDA0OHVua3hpc3J0aHZpOSJ9.CYY5Fgd8YFxH8R6mSw-TzA', {
			attribution: 'Imagery © <a href="http://mapbox.com">Mapbox</a>',
			maxZoom: 18
		}).addTo(mymap);
		
		console.log(1);
	});
}

function setLoader(on, msg) {
	// Set the loading message
	$('#bb-loader-text').text(msg);
	
	if(on) {
		$('#bb-loader').show();
	} else {
		setTimeout(function() {
			$('#bb-loader').hide();
		}, 4000);
	}
}


