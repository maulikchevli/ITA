function validateForm(event) {
	//Prevent form submission
	event.preventDefault(); 
	clearDisplayMessages();
	
	//For name
	var name = document.forms["myform"]["name"].value;
	if (!name) {
		document.getElementById("name").innerHTML = "Please Enter name";
		return false;
	}

	//For username
	var username = document.forms["myform"]["username"].value;
	if (!username) {
		document.getElementById("username").innerHTML = "Please Enter Username";
		return false;
	}

	//For passwords
	var password = document.forms["myform"]["password"].value;
	var password2 = document.forms["myform"]["password2"].value;
	if (!password) {
		document.getElementById("password").innerHTML = "Please Enter Password";
		return false;
	}
	else if (!password2) {
		document.getElementById("password2").innerHTML = "Please confirm password";
		return false;
	}
	else if(password != password2) {
		document.getElementById("password").innerHTML = "Passwords do not match";
		return false;
	}

	//for email
	var email = document.forms["myform"]["email"].value;

	var emailReg = /^[a-z](\w*)@([a-z]{3})$/g;
	//var emailReg = new RegExp('[a-z]','g');
	var res = email.search(emailReg);

	if (!email) {
		document.getElementById("email").innerHTML = "Enter Email";
		return false;	
	}
	if ( res == -1) {
		document.getElementById("email").innerHTML = "Enter valid email";
		return false;
	}

	var moNum = document.forms["myform"]["moNum"].value;
	if ( !moNum) {
		document.getElementById("moNum").innerHTML = "Enter Mobile Number";
		return false;
	}

	var moNumReg = /^(\d){10}$/g;
	var res2 = moNum.search( moNumReg);

	if ( res2 == -1) {
		document.getElementById("moNum").innerHTML = "Enter valid mobile number";
		return false;
	}

	document.write("Registered");
}

function clearDisplayMessages() {
	var messages = document.getElementsByClassName("message");
	for ( var i=0; i < messages.length; i++) {
		messages[i].innerHTML = "";
	}
}

