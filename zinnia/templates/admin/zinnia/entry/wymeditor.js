$(document).ready(function() {
  $("#id_content").wymeditor({
	  skin: "django", lang: "{{ LANGUAGE_CODE }}",
	  stylesheet: "{{ STATIC_URL }}zinnia/css/wymeditor_styles.css",
	  updateSelector: "input:submit", updateEvent: "click",
	  postInit: function(wym) {
	      wym.hovertools();
	  }
      });
    });
