invalid_input_indicator = message => {
  // need to find out how to change the border color of all input elements on the document. it's got to be something with form-control
  invalid_input = document.getElementById('invalid_message')
  invalid_input.innerHTML = message
  invalid_input.style.visibility = "visible"
}
