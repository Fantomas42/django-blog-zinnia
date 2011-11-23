{% load tagging_tags %}
$(document).ready(function() {
  {% tags_for_model zinnia.Entry as entry_tags %}
  var data = "{{ entry_tags|join:',' }}".split(",");
  $("#id_tags").autocomplete(data, {
                width: 150, max: 10,
                multiple: true, multipleSeparator: ", ",
                scroll: true, scrollHeight: 300,
                matchContains: true, autoFill: true,});
});
