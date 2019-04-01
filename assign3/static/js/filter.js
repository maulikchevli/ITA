function filterValues() {
	var filterSelect = $("#filterSelect").val();

	if (filterSelect == "hashtag") {
		toAdd = "<form onsubmit='applyFilterTag(event)'>";
		toAdd += "<input type='text' id='filterTag'>";
		toAdd += "<input type='submit' class='btn btn-primary' value='apply'>";
		$("#filter").html(toAdd);
	}

	if (filterSelect == "time") {
		toAdd = "<form onsubmit='applyFilterTime(event)'>";
		toAdd += "<input type='text' id='filterFrom'>";
		toAdd += "<input type='text' id='filterTo'>";
		toAdd += "<input type='submit' class='btn btn-primary' value='apply'>";

		$("#filter").html(toAdd);
	}
}

function applyFilterTag(event) {
	event.preventDefault();
	var username = $("#username").html();
	var tag=$("#filterTag").val();
	url = "http://localhost:5000/profile/" + username + "/filter/hashtag," + tag;

	//alert(url);
	window.location.href = url;
}

function applyFilterTime(event) {
	event.preventDefault();
	var username = $("#username").html();
	var from = $("#filterFrom").val();
	var to = $("#filterTo").val();
	url = "http://localhost:5000/profile/" + username + "/filter/time," + from + "," + to;

//	alert(url);
	window.location.href = url;
}

