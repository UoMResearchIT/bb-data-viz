/* Plot the data viz map */

// Fetch the data
$(function() {
	// Build the map
	var isChrome = /Chrome/.test(navigator.userAgent) && /Google Inc/.test(navigator.vendor);

	if(navigator.geolocation && !isChrome) {
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
	var markers = new L.MarkerClusterGroup();
	
	var dataURL = "http://130.88.198.51/bb/api/bb.json";
	//var dataURL = "testdata/bb.json";
	
	var markerCount = 0;
	
	$.getJSON(dataURL, function(data) {
		// When the data is loaded, and the map is loaded, plot the data points
		mymap.on('load', function(e) {
			var hostpath = (window.location.hostname == 'britainbreathing.org') ? 'http://britainbreathing.org/wp-content/plugins/bb-data-viz/' : '';
			var worker = new Worker(hostpath+'js/bb-plot-data.js');
			//var worker = new Worker('js/bb-plot-data.js');
			worker.postMessage(data);
			
			worker.onmessage = function(event) {
				//console.log(event.data);
				if(!event.data.complete) {
					// Plot the marker
					
					var markerLat = event.data.latitude;
					//markerLat = markerLat.toFixed(2);
					//markerLat = markerLat+Math.floor(Math.random()*20)+1;
					
					var markerLon = event.data.longitude;
					//markerLon = markerLon.toFixed(2);
					//markerLon = markerLon+Math.floor(Math.random()*20)+1;
					
					var marker = L.marker([markerLat, markerLon]);//.addTo(mymap);

					// Add the marker popup
					//var howFeeling = (event.data['How feeling'] == 0)? 'Bad': 'Good';
					
					var popUp = '<strong>'+event.data['Time uploaded to server']+'</strong><br>'+
								'How feeling: '+event.data['How feeling']+'<br>'+
								'Taken meds today: '+event.data['Taken meds today']+'<br>'+
								'Nose: '+event.data['Nose']+'<br>'+
								'Eyes: '+event.data['Eyes']+'<br>'+
								'Breathing: '+event.data['Breathing']+'<br>'+
								'Hay fever: '+event.data['hay fever']+'<br>'+
								'Asthma: '+event.data['asthma']+'<br>'+
								'Other allergy: '+event.data['other allergy']+
								'';
					
					marker.bindPopup(popUp).openPopup();
					
					// Marker clustering
					markers.addLayer(marker);
					
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
		
		mymap.addLayer(markers);
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


