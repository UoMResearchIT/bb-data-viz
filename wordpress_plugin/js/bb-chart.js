/* Plot the charts for the bb data */
var dataURL = "http://130.88.198.51/bb/api/bb.json";

$.getJSON(dataURL, function(data) {
	// When the data is loaded, and the map is loaded, plot the data points
	console.log('Chart data loaded...');
	
	Chart.defaults.global.legend = {
		'display': false
	};
	
	//// Do the processing for the gender donut
	var worker = new Worker('http://britainbreathing.org/wp-content/plugins/bb-data-viz/js/bb-gender-data.js');
	//var worker = new Worker('js/bb-gender-data.js');
	worker.postMessage(data);
	
	worker.onmessage = function(event) {
		//console.log(event.data);
		
		var ctx = document.getElementById("bb-gender-chart");
		var myChart = new Chart(ctx, {
			type: 'doughnut',
			data: {
				labels: ["Male: "+event.data.male+"%", "Female: "+event.data.female+"%"],
				datasets: [{
					label: 'Percentage of entries',
					data: [event.data.male, event.data.female],
					backgroundColor: [
						"#6fb961",
						"#315b9d"
					]
				}]
			},
			options: {}
		});	
		
		document.getElementById('bb-gender-legend').innerHTML = myChart.generateLegend();
	};
	
	//// Do the processing for the age donut
	var worker = new Worker('http://britainbreathing.org/wp-content/plugins/bb-data-viz/js/bb-age-data.js');
	worker.postMessage(data);
	
	worker.onmessage = function(event) {
		console.log(event.data);
		
		var ctx = document.getElementById("bb-age-chart");
		var myChart = new Chart(ctx, {
			type: 'doughnut',
			data: {
				labels: [
						"Under 18: "+event.data.ageunder18+"%",
						"18-30: "+event.data.age1830+"%",
						"31-40: "+event.data.age3140+"%",
						"41-50: "+event.data.age4150+"%",
						"51-60: "+event.data.age5160+"%",
						"61-70: "+event.data.age6170+"%",
						"Over 70: "+event.data.ageover70+"%"
						],
				datasets: [{
					label: 'Percentage of entries',
					data: [
							event.data.ageunder18,
							event.data.age1830,
							event.data.age3140,
							event.data.age4150,
							event.data.age5160,
							event.data.age6170,
							event.data.ageover70
						],
					backgroundColor: [
						"#6fb961",
						"#315b9d",
						"#3D319B",
						"#72319B",
						"#9B318F",
						"#318F9B",
						"#4576C4"
					]
				}]
			},
			options: {}
		});
		
		document.getElementById('bb-age-legend').innerHTML = myChart.generateLegend();
	};

});
