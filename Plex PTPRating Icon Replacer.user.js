// ==UserScript==
// @name         Plex PTPRating Icon Replacer
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Replaces Rotten Tomato icons with correct ones(IMDB, PTP, Rotten Tomato)
// @author       Willywillywoo697
// @include      http://10.0.0.81:32400/*
// @grant        none
// @require https://gist.github.com/raw/2625891/waitForKeyElements.js
// @require http://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js
// ==/UserScript==
/* globals jQuery, $, waitForKeyElements */

(function() {
    'use strict';

    // Your code here...
    waitForKeyElements(".CriticRating-certified-kPXY1l", removeDSclass);
    console.log("Hello, icon replacer")
    function removeDSclass(jNode) {
        console.log("removeds")
        jNode.addClass("CriticRating-imdb-23PVnW")
        jNode.removeClass("CriticRating-certified-kPXY1l")
    }
    
})();