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

	  if (result.length > 5) {
		  do_length = 5;
	  } else {
		  do_length = result.length;
	  }

	  for (i=0; i < do_length; i++) {
        dictItem = lunrDict[result[i].ref];
		try {
			if (dictItem.subtitle != null) {
				subtitletext = dictItem.subtitle;
			} else {
				subtitletext = "";
			}
		} catch(err) {
			subtitletext = ""
		}
        final_string = final_string + "<li><a href=\"." + dictItem.url + "\"><span class='search-title'>" + dictItem.title + "</span> | <span class='search-subtitle'>" + subtitletext + "</span></a></li>";
      }

	  document.getElementById('search-output').innerHTML = final_string;
    });

  }
});
