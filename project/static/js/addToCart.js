function addToCart(pid) {
    var id = "#pid"+pid;
    quantity = $(id).prop('value');

    var q = {"pid":pid,"quantity":quantity};

    $.ajax({
		type: "POST",
		url: '/cart/add',
		data: q,
		dataType: 'json',
		success: function(result) {
			if(result) {
                $('body').prepend('<div id="flash" class="alert alert-success" style="display:none"></div>');
                $('#flash').html(result['result']);
                $('#flash').slideDown('slow');
                $('#flash').click(function () { $('#flash').toggle('highlight') });
			}
		}
	});
}
