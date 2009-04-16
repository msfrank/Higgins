{% extends "templates/library-base.t" %}

{% block title %}{{ song.name }}{% endblock %}

{% block stylesheet %}
    <link href="/static/css/song.css" rel="stylesheet" type="text/css" media="screen"/>
    <link type="text/css" href="/static/css/smoothness/jquery-ui-1.7.custom.css" rel="stylesheet" />
    <script type="text/javascript" language="javascript" src="/static/js/jquery-1.3.2.min.js"></script>
    <script type="text/javascript" language="javascript" src="/static/js/jquery-ui-1.7.min.js"></script>
    <script type="text/javascript" charset="utf-8">
        $(document).ready(function() {
            $('#edit-song').click (function () {
                $("#song-info-viewer").fadeOut("def", function () {
                    $("#song-info-editor").fadeIn("def");
                });
            });
            $('#edit-cancel').click (function () {
                $("#song-info-editor").fadeOut("def", function () {
                    $("#song-info-viewer").fadeIn("def");
                });
            });
        });
    </script>
{% endblock %}

{% block library_content %}
<div id="song-info-container">
    <table id="song-info-viewer">
        <tr><td class="song-title">{{ song.name }}</td></tr>
        <tr><td>by <a href="/library/music/byartist/{{song.artist.id}}/">{{song.artist}}</a></td></tr>
        <tr><td>from the album <a href="/library/music/byalbum/{{song.album.id}}/">{{song.album}}</a></td></tr>
        <tr><td>classified in <a href="/library/music/bygenre/{{song.album.genre.id}}/">{{song.album.genre}}</td></tr>
        <tr><td>track #{{song.track_number}}</td></tr>
        <tr><td><a id="edit-song" href="#">(edit)</a></td></tr>
    </table>
    <div id="song-info-editor">
        <form id="song-editor-form" action="/library/music/bysong/{{song.id}}/" method="post">
            <table id="song-info-table">
                {{ editor.as_table }}
            </table>
            <input id="edit-cancel" type="button" value="cancel"/><input id="edit-save" type="submit" value="save" />
        </form>
    </div>
</div>
 {% endblock %}
