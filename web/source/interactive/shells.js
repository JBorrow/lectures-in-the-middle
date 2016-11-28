var svg;
var numberOfProtons = 92;
var numberOfNeutrons = 92;

var protonStructure = {
	p1s1 : 2,
	p1p3 : 4,
	p1p1 : 2,
	p1d5 : 6,
	p2s1 : 2,
	p1d3 : 4,
	p1f7 : 8,
	p2p3 : 4,
	p1f5 : 6,
	p2p1 : 2,
	p1g9 : 10,
	p1g7 : 8,
	p2d5 : 6,
	p1h11 : 12,
	p2d3 : 4,
	p3s1 : 2,
	p1h9 : 10,
};	

var neutronStructure = {
	n1s1 : 2,
	n1p3 : 4,
	n1p1 : 2,
	n1d5 : 6,
	n2s1 : 2,
	n1d3 : 4,
	n1f7 : 8,
	n2p3 : 4,
	n1f5 : 6,
	n2p1 : 2,
	n1g9 : 10,
	n2d5 : 6,
	n1g7 : 8,
	n1h11 : 12,
	n2d3 : 4,
	n3s1 : 2,
	n1h9 : 10,
};	

function getSVGById(id) {
	try {
		container = document.getElementById(id);
	} catch(e) {
		console.log("Failed to get element " + id);
	};

	return container.contentDocument;
};

function changeItem(thisSVG, id, color, subId) {
	try {
		thisItem = thisSVG.getElementById(subId + id);
		thisItem.style.fill = color;
	} catch(err) {
		// do nothing - we've probably run out of protons/neutrons
	}
}

function highlight(thisSVG, id, allTheRest, color='red', otherColor='black') {
	// ensures all those that are not highlighted are 'otherColor'.
	for (key in allTheRest) {
		if (key != id) {
			text = thisSVG.getElementById(key.substring(0, 3));
			line = thisSVG.getElementById(key + 'l');
			box = thisSVG.getElementById(key);
			text.style.fill = otherColor;
			line.style.stroke = otherColor;
			box.style['stroke-opacity'] = 0;
		} else {
			text = thisSVG.getElementById(id.substring(0, 3));
			line = thisSVG.getElementById(id + 'l');
			box = thisSVG.getElementById(id);
			text.style.fill = color;
			line.style.stroke = color;
			box.style['stroke-opacity'] = 1;
		}
	}
};

function changeItems(thisSVG, numToChange, maxNum, subId, color='red', emptyColor='white') {
	for (i = 1; i <= maxNum; i++) {
		if (i <= numToChange) {
			changeItem(thisSVG, i, color, subId);
		} else {
			changeItem(thisSVG, i, emptyColor, subId);
		}
	}

	return;
};

function findWhere(n, structure) {
	// Where is the final nucleon?
	var soFar = 0;
	for (key in structure) {
		if (n > soFar + structure[key]) {
			soFar = soFar + structure[key];
		} else {
			return key;
		}
	}
	return "Sorry, out of range!";
};


//initially, we must wait for the SVG to load NOT the document.
$('#neutrons').on('load', function () {
	$('#protons').on('load', function () {
		protonSVG = getSVGById('protons');
		neutronSVG = getSVGById('neutrons');
		changeItems(protonSVG, 0, numberOfProtons, 'p');
		changeItems(neutronSVG, 0, numberOfNeutrons, 'n');
		highlight(protonSVG, 'none', protonStructure);
		highlight(neutronSVG, 'none', neutronStructure);
	});
});

$('#numProtons').on('input', function () {
	numProtons = $('#numProtons').val();
	if (numProtons > numberOfProtons) {
		numProtons = numberOfProtons; // so we don't crash
	} else {
		// all ok
	}
	changeItems(protonSVG, numProtons, numberOfProtons, 'p');
	maxLevel = findWhere(numProtons, protonStructure);
	highlight(protonSVG, maxLevel, protonStructure);
});


$('#numNeutrons').on('input', function () {
	numNeutrons= $('#numNeutrons').val();
	if (numNeutrons > numberOfNeutrons) {
		numNeutrons = numberOfNeutrons; // so we don't crash
	} else {
		// all ok
	}
	changeItems(neutronSVG, numNeutrons, numberOfNeutrons, 'n', color='black');
	maxLevel = findWhere(numNeutrons, neutronStructure);
	highlight(neutronSVG, maxLevel, neutronStructure);
});
