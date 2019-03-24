function sendAnalytics(fileId) {
	var file = {"file_id": fileId};

	$.ajax({
		type: "POST",
		url: '/analytics/file',
		data: file,
		dataType: 'json',
		success: function(result) {
		}
	});
}

