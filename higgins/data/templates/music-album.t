{% extends "templates/library-base.t" %}

{% block stylesheet %}
    <link href="/static/css/album.css" rel="stylesheet" type="text/css" media="screen"/>
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
            "bSort": true,
            "bInfo": true,
            "bAutoWidth": true } );
            $('#edit-album').click (function () {
                $("#album-info-viewer").fadeOut("def", function () {
                    $("#album-info-editor").fadeIn("def");
                });
            });
            $('#edit-cancel').click (function () {
                $("#album-info-editor").fadeOut("def", function () {
                    $("#album-info-viewer").fadeIn("def");
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

{% block title %}{{ album.name }}{% endblock %}

{% block library_content %}
<div>
    <p>
        <div id="album-info-container">
            <table id="album-info-viewer">
                <tr><td class="song-album">{{ album.name }}</td></tr>
                <tr><td>by <a href="/library/music/byartist/{{album.artist.id}}/">{{album.artist}}</a></td></tr>
                <tr><td>classified in <a href="/library/music/bygenre/{{album.genre.id}}/">{{album.genre}}</td></tr>
                <tr><td><a id="edit-album" href="#">(edit)</a></td></tr>
            </table>
            <div id="album-info-editor">
                <form id="album-editor-form" action="/library/music/byalbum/{{album.id}}/" method="post">
                    <table id="album-info-table">
                        {{ editor.as_table }}
                    </table>
                    <input id="edit-cancel" type="button" value="cancel"/><input id="edit-save" type="submit" value="save" />
                </form>
            </div>
        </div>
        <table class="display" id="song-listing">
            <thead>
                <th class="song-header">#</th>
                <th class="song-header">Title</th>
                <th class="song-header">Duration</th>
            </thead>
            <tbody>
        {% for song in song_list %}
            <tr>
                <td class="song-tracknumber">{{song.track_number}}</td>
                <td class="song-title"><a href="/library/music/bysong/{{song.id}}/">{{song.name}}</a></td>
                <td>{{song.print_duration}}</a></td>
            </tr>
        {% endfor %}
            </tbody>
        </table>
    </p>
</div>
{% endblock %}
