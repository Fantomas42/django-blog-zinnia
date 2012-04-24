{% load url from future %}
$(document).ready(function() {
  mySettings["previewParserPath"] = "{% url 'admin:zinnia_entry_markitup_preview' %}";
  $("#id_content").markItUp(mySettings);
});
