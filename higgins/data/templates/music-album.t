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
            $('#edit-albuminfo').click (function () {
                $('#album-editor').dialog({modal: true, title: "Album Editor"});
            });
        });
</script>
{% endblock %}

{% block title %}{{ album.name }}{% endblock %}

{% block library_content %}
<div>
    <p>
        <div id="song-albuminfo-container">
        <table id="song-albuminfo">
            <tr><td class="song-album">{{ album.name }}</td></tr>
            <tr><td>by <a href="/library/music/byartist/{{album.artist.id}}/">{{album.artist}}</a></td></tr>
            <tr><td>classified in <a href="/library/music/bygenre/{{album.genre.id}}/">{{album.genre}}</td></tr>
            <tr><td><a id="edit-albuminfo" href="#">(edit)</a></td></tr>
        </table>
        </div>
        <table class="display" id="song-listing">
            <thead>
                <th class="song-header">#</th>
                <th class="song-header">Title</th>
                <th class="song-header">Duration</th>
                <th class="song-header">Rating</th>
            </thead>
            <tbody>
        {% for song in song_list %}
            <tr>
                <td class="song-tracknumber">{{song.track_number}}</td>
                <td class="song-title"><a href="/library/music/bysong/{{song.id}}/">{{song.name}}</a></td>
                <td>{{song.print_duration}}</a></td>
                <td></td>
            </tr>
        {% endfor %}
            </tbody>
        </table>
    </p>
</div>
<div id="album-editor">
    Hello, world!
</div>
{% endblock %}
