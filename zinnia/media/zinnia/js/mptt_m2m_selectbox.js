/*
 * This is based on the SelectBox.js that comes with Django admin media
 * 
 */

var SelectBox = {
    cache: new Object(),
    init: function(id) {
        var box = document.getElementById(id);
        var node;
        SelectBox.cache[id] = new Array();
        var cache = SelectBox.cache[id];
        for (var i = 0; (node = box.options[i]); i++) {
            cache.push({value: node.value, text: node.text, displayed: 1, tree_id: node.getAttribute('data-tree-id'), left_val: node.getAttribute('data-left-value')});
        }
    },
    redisplay: function(id) {
        // Repopulate HTML select box from cache
        var box = document.getElementById(id);
        
        // for some reason both these steps are neccessary to get browsers to work properly...
        for (i = 0; i < box.options.length; i++) {
            box.options[0] = null;
        }
        box.options.length = 0;
        
        SelectBox.sort(id);
        for (var i = 0, j = SelectBox.cache[id].length; i < j; i++) {
            var node = SelectBox.cache[id][i];
            if (node.displayed) {
                newOpt = new Option(node.text, node.value, false, false);
                newOpt.setAttribute('data-tree-id', node.tree_id);
                newOpt.setAttribute('data-left-value', node.left_val);
                box.options[box.options.length] = newOpt;
            }
        }
    },
    filter: function(id, text) {
        // Redisplay the HTML select box, displaying only the choices containing ALL
        // the words in text. (It's an AND search.)
        var tokens = text.toLowerCase().split(/\s+/);
        var node, token;
        for (var i = 0; (node = SelectBox.cache[id][i]); i++) {
            node.displayed = 1;
            for (var j = 0; (token = tokens[j]); j++) {
                if (node.text.toLowerCase().indexOf(token) == -1) {
                    node.displayed = 0;
                }
            }
        }
        SelectBox.redisplay(id);
    },
    delete_from_cache: function(id, value) {
        var node, delete_index = null;
        for (var i = 0; (node = SelectBox.cache[id][i]); i++) {
            if (node.value == value) {
                delete_index = i;
                break;
            }
        }
        var j = SelectBox.cache[id].length - 1;
        for (var i = delete_index; i < j; i++) {
            SelectBox.cache[id][i] = SelectBox.cache[id][i+1];
        }
        SelectBox.cache[id].length--;
    },
    add_to_cache: function(id, option) {
        // in this case option is an anonymous object, not an html element
        SelectBox.cache[id].push({value: option.value, text: option.text, displayed: 1, tree_id: option.tree_id, left_val: option.left_val});
    },
    cache_contains: function(id, value) {
        // Check if an item is contained in the cache
        var node;
        for (var i = 0; (node = SelectBox.cache[id][i]); i++) {
            if (node.value == value) {
                return true;
            }
        }
        return false;
    },
    move: function(from, to) {
        var from_box = document.getElementById(from);
        var to_box = document.getElementById(to);
        var option;
        for (var i = 0; (option = from_box.options[i]); i++) {
            if (option.selected && SelectBox.cache_contains(from, option.value)) {
                SelectBox.add_to_cache(to, {value: option.value, text: option.text, displayed: 1, tree_id: option.getAttribute('data-tree-id'), left_val: option.getAttribute('data-left-value')});
                SelectBox.delete_from_cache(from, option.value);
            }
        }
        SelectBox.redisplay(from);
        SelectBox.redisplay(to);
    },
    move_all: function(from, to) {
        var from_box = document.getElementById(from);
        var to_box = document.getElementById(to);
        var option;
        for (var i = 0; (option = from_box.options[i]); i++) {
            if (SelectBox.cache_contains(from, option.value)) {
                SelectBox.add_to_cache(to, {value: option.value, text: option.text, displayed: 1, tree_id: option.getAttribute('data-tree-id'), left_val: option.getAttribute('data-left-value')});
                SelectBox.delete_from_cache(from, option.value);
            }
        }
        SelectBox.redisplay(from);
        SelectBox.redisplay(to);
    },
    sort: function(id) {
        SelectBox.cache[id].sort( function(a, b) {
            a_tree_id = parseInt(a.tree_id);
            b_tree_id = parseInt(b.tree_id);
            a_left_val = parseInt(a.left_val);
            b_left_val = parseInt(b.left_val);
            try {
                if (a_tree_id > b_tree_id) return 1;
                if (a_tree_id < b_tree_id) return -1;
                if (a_tree_id == b_tree_id) {
                    if (a_left_val > b_left_val) return 1;
                    if (a_left_val < b_left_val) return -1;
                }
            }
            catch (e) {
                // silently fail on IE 'unknown' exception
            }
            return 0;
        } );
    },
    select_all: function(id) {
        var box = document.getElementById(id);
        for (var i = 0; i < box.options.length; i++) {
            box.options[i].selected = 'selected';
        }
    }
}
