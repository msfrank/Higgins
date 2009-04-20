{% extends "templates/library-base.t" %}

{% block stylesheet %}
    <link href="/static/css/playlist.css" rel="stylesheet" type="text/css" media="screen"/>
    <link type="text/css" href="/static/css/smoothness/jquery-ui-1.7.custom.css" rel="stylesheet" />
    <script type="text/javascript" language="javascript" src="/static/js/jquery-1.3.2.min.js"></script>
    <script type="text/javascript" language="javascript" src="/static/js/jquery-ui-1.7.min.js"></script>
    <script type="text/javascript" language="javascript" src="/static/js/datatables-1.4.min.js"></script>
    <script type="text/javascript" charset="utf-8">
        $(document).ready(function() {
            $('#song-listing').dataTable( {
            "bPaginate": false,
            "bLengthChange": true,
            "bFilter": false,
            "bSort": false,
            "bInfo": true,
            "bAutoWidth": true } );
            $('#edit-playlist').click (function () {
                $("#playlist-info-viewer").fadeOut("def", function () {
                    $("#playlist-info-editor").fadeIn("def");
                });
            });
            $('#edit-cancel').click (function () {
                $("#playlist-info-editor").fadeOut("def", function () {
                    $("#playlist-info-viewer").fadeIn("def");
                });
            });
            /*
            $('#edit-save').click (function () {
                $("#album-info-editor").fadeOut("def", function () {
                    $("#album-info-viewer").fadeIn("def");
                });
            });
            */
        });
</script>
{% endblock %}

{% block title %}{{ playlist.name }}{% endblock %}

{% block library_content %}
<div>
    <p>
        <div id="playlist-info-container">
            <table id="playlist-info-viewer">
                <tr><td class="playlist-song">{{ playlist.name }}</td></tr>
                <tr><td><a id="edit-playlist" href="#">(edit)</a></td></tr>
            </table>
            <div id="playlist-info-editor">
                <p>
                    <table id="playlist-info-table">
                        <tr><td>Playlist Name:</td><td><input id="playlist-title" type="text"/></td></tr>
                        <tr><td>Rating:</td><td><input id="playlist-rating" type="text"/></td></tr>
                    </table>
                </p>
                <input id="edit-cancel" type="button" value="Cancel"/><input id="edit-save" type="button" value="Save"/>
            </div>
        </div>
        <table class="display" id="song-listing">
            <thead>
                <th class="song-header">#</th>
                <th class="song-header">Title</th>
                <th class="song-header">Duration</th>
            </thead>
            <tbody>
                {% for song in song_list %}<tr>
                    <td class="song-tracknumber">{{forloop.counter}}</td>
                    <td class="song-title"><a href="/library/music/bysong/{{song.id}}/">{{song.name}}</a></td>
                    <td>{{song.print_duration}}</a></td>
                </tr>{% endfor %}
            </tbody>
        </table>
    </p>
</div>
{% endblock %}
