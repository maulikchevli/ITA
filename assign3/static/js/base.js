function suggest(input) {
	var query = {"query": input};

	$.ajax({
		type: "POST",
		url: '/search',
		data: query,
		dataType: 'json',
		success: function(result) {
			if(result) {
				var posts = result["posts"];
				var users = result["users"];

				var p = "";
				for (i in posts) {
					p += "<li>"+posts[i]+"</li>";
				}

				for (i in users) {
					p += "<li>"+users[i]+"</li>";
				}

				$("#searchSuggestions").html(p);
			}
		}
	});
}
