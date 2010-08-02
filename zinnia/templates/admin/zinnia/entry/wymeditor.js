$(document).ready(function() {
  $("#id_content").wymeditor({
                   skin: "django", lang: "{{ LANGUAGE_CODE }}",
                   stylesheet: "{{ ZINNIA_MEDIA_URL }}css/wymeditor_styles.css",
                   updateSelector: "input:submit", updateEvent: "click"});
});