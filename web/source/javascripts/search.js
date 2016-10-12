var lunrIndex = null;

// Download index data
$.ajax({
  url: './search.json',
  cache: true,
  method: 'GET',
  success: function(data) {
    lunrIndex = lunr.Index.load(data['index']);
	lunrDict = data['docs'];
	console.log(lunrDict);


	document.getElementById('search-input').addEventListener('keydown', function() {
	  result = lunrIndex.search(document.getElementById('search-input').value);

	  final_string = "";

	  for (i=0; i < result.length; i++) {
        dictItem = lunrDict[result[i].ref];
		try {
			if (dictItem.subtitle != null) {
				subtitletext = "<h3>" + dictItem.subtitle + "</h3>";
			} else {
				subtitletext = "";
			}
		} catch(err) {
			subtitletext = ""
		}
        final_string = final_string + "<div class='search-result'><a href=\"." + dictItem.url + "\"><h2>" + dictItem.title + "</h2>" + subtitletext + "</a></div>";
      }

	  document.getElementById('search-results').innerHTML = final_string;
    });

  }
});
