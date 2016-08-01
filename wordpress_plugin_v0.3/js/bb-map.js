/* Plot the data viz map */
var mapOptions =  { styles: 
[
    {
        "featureType": "administrative",
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "color": "#444444"
            }
        ]
    },
    {
        "featureType": "administrative.country",
        "elementType": "labels.text",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "administrative.province",
        "elementType": "labels.text",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "administrative.locality",
        "elementType": "labels.text",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "landscape",
        "elementType": "all",
        "stylers": [
            {
                "color": "#f2f2f2"
            }
        ]
    },
    {
        "featureType": "landscape.man_made",
        "elementType": "geometry",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "all",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "road",
        "elementType": "all",
        "stylers": [
            {
                "saturation": -100
            },
            {
                "lightness": 45
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "all",
        "stylers": [
            {
                "visibility": "simplified"
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "geometry",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "road.arterial",
        "elementType": "labels.icon",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "transit",
        "elementType": "all",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "all",
        "stylers": [
            {
                "color": "#46bcec"
            },
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#60baef"
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "labels.text",
        "stylers": [
            {
                "visibility": "off"
            },
            {
                "color": "#ff0000"
            }
        ]
    }
]
};

var feelingData;
var eyesData;
var noseData;
var breathingData;

function initMapData() {
	// Set the map
	nextMonday = Date.today().next().monday();
	nextMonday = nextMonday.toString('yyyy-MM-dd');
	console.log('all-2016-03-14-'+nextMonday+'.kml');
	
	var map = new google.maps.Map(document.getElementById('bb-mapid'), mapOptions);
	
	var ctaLayer = new google.maps.KmlLayer({
		url: 'http://130.88.198.51/bb/api/all-2016-03-14-'+nextMonday+'.kml?nocache='+(new Date()).getTime(),
		map: map
	});
	
	setLoader(0, 'Loading data...');
}

function initTimeline() {	
	// Set the start and end for the timeline
	dateStart = (new Date('2016-03-14').getTime() / 1000); // Week starts on the Monday before the first data was collected
	
	nextMonday = Date.today().next().monday();
	nextMonday = nextMonday.toString('yyyy-MM-dd');
	dateEnd = (new Date(nextMonday).getTime() / 1000); // Week ends next Sunday from now
	
	console.log(nextMonday);
	
	rangeStart1 = dateStart;
	rangeStart2 = dateEnd;
	
	var stepSeconds = 604800;
	
	// Set the timeline
	$( "#bb-slider" ).slider({
		range: true,
		values: [rangeStart1, rangeStart2],
		min: dateStart,
		max: dateEnd,
		step: stepSeconds,
		slide: function(event, ui) {
			var leftSlider = ui.values[0]*1000;
			var rightSlider = ui.values[1]*1000;
			
			if(rightSlider-leftSlider < 518400) {
				return false;
			} else {
				var date1 = new Date((ui.values[0])*1000);
				date1 = date1.toISOString();
				date1 = date1.split('T');
				weekStart = date1[0];
			
				var date2 = new Date((ui.values[1])*1000);
				date2 = date2.toISOString();
				date2 = date2.split('T');
				weekEnd = date2[0];
			
				showTimelineRange(weekStart, weekEnd);
			}
		}
	});
	
	// Add the legend
	nextMonday = new Date(nextMonday).toString('dd-MM-yy')
	$("#bb-slider").slider().slider("pips", {
        labels: { "first": "14-03-16", "last": nextMonday }
    });
    
	$('#bb-start-date').text(new Date('2016-03-14').toString('dd-MM-yy'));
	$('#bb-end-date').text(nextMonday);
}
	
function showTimelineRange(weekStart, weekEnd) {
	//console.log(weekStart+' - '+weekEnd);
	setLoader(1, 'Loading data...');
	
	// Update the dates
	$('#bb-start-date').text(new Date(weekStart).toString('dd-MM-yy'));
	$('#bb-end-date').text(new Date(weekEnd).toString('dd-MM-yy'));
	
	// Show data for the selected timeline and type
	var timeline = $('.bb-map-control-active').data('timeline');
	
	var dataFile = timeline+'-'+weekStart+'-'+weekEnd+'.kml';
	
	console.log(dataFile);
	
	// Set the map
	var map = new google.maps.Map(document.getElementById('bb-mapid'), mapOptions);
	
	var ctaLayer = new google.maps.KmlLayer({
		url: 'http://130.88.198.51/bb/api/'+dataFile+'?nocache='+(new Date()).getTime(),
		map: map
	});
		
	setLoader(0, 'Loading data...');
}

function selectDataType() {
	// Bind events for the view buttons
	$('.bb-map-control').click(function() {
		$('.bb-map-control').removeClass('bb-map-control-active');
		$(this).addClass('bb-map-control-active');		
	});
	
	$('.bb-map-control').click(function() {
		// Get the datafile from the selected option
		setLoader(1, 'Loading data...');
		
		// Get the timeline and date range
		var timeline = $('.bb-map-control-active').data('timeline');
		
		var date1 = new Date(($("#bb-slider").slider("values", 0))*1000);
		date1 = date1.toISOString();
		date1 = date1.split('T');
		weekStart = date1[0];
		
		var date2 = new Date(($("#bb-slider").slider("values", 1))*1000);
		date2 = date2.toISOString();
		date2 = date2.split('T');
		weekEnd = date2[0];
		
		var dataFile = timeline+'-'+weekStart+'-'+weekEnd+'.kml';
		
		console.log(dataFile);
		
		// Set the map
		var map = new google.maps.Map(document.getElementById('bb-mapid'), mapOptions);
		
		var ctaLayer = new google.maps.KmlLayer({
			url: 'http://130.88.198.51/bb/api/'+dataFile+'?nocache='+(new Date()).getTime(),
			map: map
		});
		
		setLoader(0, 'Loading data...');
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
		}, 3000);
	}
}

$(function() {
	setLoader(1, 'Loading map...');
	initMapData();
	initTimeline();
	selectDataType();
});	
