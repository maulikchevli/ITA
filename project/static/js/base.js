function starRequest() {
    q = {"request":"true"}
    $.ajax({
		type: "POST",
		url: '/star/request',
		data: q,
		dataType: 'json',
		success: function(result) {
			if(result) {
                $('body').prepend('<div id="flash" class="alert alert-success" style="display:none"></div>');
                $('#flash').html(result['result']);
                $('#flash').slideDown('slow');
                $('#flash').click(function () { $('#flash').toggle('highlight') });
			}
        },
        error: function() {
            $('body').prepend('<div id="flash" class="alert alert-danger" style="display:none"></div>');
            $('#flash').html("Could not send request");
            $('#flash').slideDown('slow');
            $('#flash').click(function () { $('#flash').toggle('highlight') });
        }
	});
}

function acceptStar(username) {
    usernameId = "#"+username;

    q = {"username":username};
    $.ajax({
		type: "POST",
		url: '/admin/star/accept',
		data: q,
		dataType: 'json',
		success: function(result) {
			if(result) {
                $('body').prepend('<div id="flash" class="alert alert-success" style="display:none"></div>');
                $('#flash').html(result['result']);
                $('#flash').slideDown('slow', function() {
                    $(usernameId).css('display','none');
                });
                $('#flash').click(function () { $('#flash').toggle('highlight') });
			}
        },
        error: function() {
            $('body').prepend('<div id="flash" class="alert alert-danger" style="display:none"></div>');
            $('#flash').html("Could not send request");
            $('#flash').slideDown('slow');
            $('#flash').click(function () { $('#flash').toggle('highlight') });
        }
	});
}