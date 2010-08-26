tinyMCE.init({
	mode: "exact",
	elements: "id_content",
	theme: "advanced",
	theme_advanced_toolbar_location : "top",
	height: "300",
	plugins: "spellchecker,directionality,paste,searchreplace",
	language: "{{ language }}",
	directionality: "{{ directionality }}",
	spellchecker_languages : "{{ spellchecker_languages }}",
	spellchecker_rpc_url : "{{ spellchecker_rpc_url }}"
	});
