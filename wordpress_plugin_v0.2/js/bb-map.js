/* Plot the data viz map */
var map;

function plotMapData() {
	// Set the map
	map = new google.maps.Map(document.getElementById('bb-mapid'), {});
	
	var ctaLayer = new google.maps.KmlLayer({
		url: 'http://130.88.198.51/bb/api/symptom_score.kml?nocache='+(new Date()).getTime(),
		map: map
	});
	
	setLoader(0, 'Map load complete.')
}

function setControls() {
	// Bind events for the view buttons
	$('.bb-map-control').click(function() {
		$('.bb-map-control').removeClass('bb-map-control-active');
		$(this).addClass('bb-map-control-active');
		
		var dataFile = $(this).data('kml-file');
		
		setLoader(1, 'Loading data...')
		
		// Set the map
		map = new google.maps.Map(document.getElementById('bb-mapid'), {});
	
		var ctaLayer = new google.maps.KmlLayer({
			url: 'http://130.88.198.51/bb/api/'+dataFile+'?nocache='+(new Date()).getTime(),
			map: map
		});
		
		setLoader(0, 'Data load complete.')
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

$(function() {
	setLoader(1, 'Loading map...');
	plotMapData();
	setControls();
});	
