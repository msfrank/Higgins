{% extends "templates/library-base.t" %}

{% block stylesheet %}
    <link href="/static/css/artist.css" rel="stylesheet" type="text/css" media="screen"/>
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
            $('#edit-artist').click (function () {
                $("#artist-info-viewer").fadeOut("def", function () {
                    $("#artist-info-editor").fadeIn("def");
                });
            });
            $('#edit-cancel').click (function () {
                $("#artist-info-editor").fadeOut("def", function () {
                    $("#artist-info-viewer").fadeIn("def");
                });
            });
            /*
            $('#edit-save').click (function () {
                $("#artist-info-editor").fadeOut("def", function () {
                    $("#artist-info-viewer").fadeIn("def");
                });
            });
            */
        });
</script>
{% endblock %}

{% block title %}{{ artist.name }}{% endblock %}

{% block library_content %}
<div>
    <p>
        <div id="artist-info-container">
            <table id="artist-info-viewer">
                <tr><td id="artist-name">{{ artist.name }}</td></tr>
                {% if artist.website %}<tr><td><a href="{{artist.website}}">{{artist.website}}</a></td></tr>{% endif %}
                <tr><td><a id="edit-artist" href="#">(edit)</a></td></tr>
            </table>
            <div id="artist-info-editor">
                <form id="artist-editor-form" action="/library/music/byartist/{{artist.id}}/" method="post">
                    <table id="artist-info-table">
                        {{ editor.as_table }}
                    </table>
                    <input id="edit-cancel" type="button" value="cancel"/><input id="edit-save" type="submit" value="save" />
                </form>
            </div>
        </div>
        <table class="display" id="album-listing">
            <thead>
                <th class="album-header">Released</th>
                <th class="album-header">Title</th>
                <th class="album-header">Genre</th>
            </thead>
            <tbody>
                {% for album in album_list %}<tr>
                    {% if album.release_date %}
                    <td class="album-released">{{album.release_date}}</td>
                    {% else %}
                    <td class="album-released">Unknown</td>
                    {% endif %}
                    <td class="album-title"><a href="/library/music/byalbum/{{album.id}}/">{{album.name}}</a></td>
                    <td class="album-genre"><a href="/library/music/bygenre/{{album.genre.id}}/">{{album.genre.name}}</a></td>
                </tr>{% endfor %}
            </tbody>
        </table>
    </p>
</div>
{% endblock %}
