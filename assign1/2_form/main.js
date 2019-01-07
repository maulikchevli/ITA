function validateForm(event) {

  event.preventDefault(); //Prevets form submission
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
  var email2 = document.forms["myform"]["email2"].value;
  if (!email) {
    document.getElementById("email").innerHTML = "Enter Email";
    return false;
  }
  else if (!email2) {
    document.getElementById("email2").innerHTML = "Confirm email";
    return false;
  }
  else if (email != email2) {
    document.getElementById("email").innerHTML = "Emails do not match";
    return false;
  }
}

function validate() {
  document.getElementById("cap").innerHTML = "HEY there !!! ";
}

