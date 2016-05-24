// Loop over the data
onmessage = function(e) {
	console.log('Worker started...');
	//console.log(e.data);
	
	var i=0;
	//for(i; i<e.data.length; i++) {
	for(i; i<600; i++) {
		// Pass the message back up from this web worker
		e.data[i].complete = 0;
		postMessage(e.data[i]);
	}
	
	// Processing finished
	e.data.complete = 1;
	postMessage(e.data);
}

