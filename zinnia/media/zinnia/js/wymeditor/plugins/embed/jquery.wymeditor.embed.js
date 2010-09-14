/*
 * WYMeditor : what you see is What You Mean web-based editor
 * Copyright (c) 2005 - 2009 Jean-Francois Hovinne, http://www.wymeditor.org/
 * Dual licensed under the MIT (MIT-license.txt)
 * and GPL (GPL-license.txt) licenses.
 *
 * For further information visit:
 *        http://www.wymeditor.org/
 *
 * File Name:
 *        jquery.wymeditor.embed.js
 *        Experimental embed plugin
 *
 * File Authors:
 *        Jonatan Lundin
 *        Tobias von Klipstein (modified 20100914)
 */
(function() {
    if (WYMeditor && WYMeditor.XhtmlValidator['_tags']['param']['attributes']) {
        
        WYMeditor.XhtmlValidator['_tags']["embed"] = {
            "attributes":[
                "allowscriptaccess",
                "allowfullscreen",
                "height",
                "src",
                "type",
                "width",
                "flashvars",
                "wmode"
            ],
            "inside":"object"
        };
        
        WYMeditor.XhtmlValidator['_tags']['param'] = {
            "attributes":[
                "type",
                "value",
                "name"
            ],
            "required":[
                "name"
            ],
            "inside":"object"
        };
        
        var XhtmlSaxListener = WYMeditor.XhtmlSaxListener;
        WYMeditor.XhtmlSaxListener = function () {
            var listener = XhtmlSaxListener.call(this);
            listener.block_tags.splice(listener.block_tags.indexOf("param"), 1);
            listener.inline_tags.push('embed', 'param', 'object');
            return listener;
        };
        WYMeditor.XhtmlSaxListener.prototype = XhtmlSaxListener.prototype;
    }
})();
