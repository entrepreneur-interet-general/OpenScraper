
console.log(">>> script js/modal_error.js loaded");

// function to close error modal
$(function () {

	$("#close-modal-error").click(
		function(){
		
			//alert("The error modal was clicked.");
			$("#modal-error").toggleClass("is-active");

		})
});
