{% extends "templates/library-base.t" %}

{% block stylesheet %}
    <link href="/static/css/album.css" rel="stylesheet" type="text/css" media="screen"/>
    <link type="text/css" href="/static/css/smoothness/jquery-ui-1.7.custom.css" rel="stylesheet" />
    <script type="text/javascript" language="javascript" src="/static/js/jquery-1.3.2.min.js"></script>
    <script type="text/javascript" language="javascript" src="/static/js/jquery-ui-1.7.min.js"></script>
    <script type="text/javascript" language="javascript" src="/static/js/datatables-1.4.min.js"></script>
    <script type="text/javascript" charset="utf-8">
        $(document).ready(function() {
            $('#song-listing').dataTable({
                "bPaginate": false,
                "bLengthChange": true,
                "bFilter": false,
                "bSort": true,
                "bInfo": true,
                "bAutoWidth": true,
            });
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
             * select all songs
             */
            $('#select-all-action').click (function () {
                $(".song-selector").attr('checked', true);
            });

            /*
             * unselect all songs
             */
            $('#unselect-all-action').click (function () {
                $(".song-selector").attr('checked', false);
            });

            /*
             * add to playlist callbacks
             */
            $('#add-to-playlist-action').click (function () {
                $("#add-to-playlist-dialog").css ({
                    position: 'absolute',
                    top: ($(window).height()/2) - ($('#add-to-playlist-dialog').height()/2),
                    left: ($(window).width()/2) - ($('#add-to-playlist-dialog').width()/2),
                });
                $.post("/library/playlists/",
                    { action: 'list' },
                    function (retval) {
                        if (retval.status == 200) {
                            var playlists_html = '';
                            for (var i = 0; i < retval.playlists.length; i++) {
                                playlists_html += '<option value="' + retval.playlists[i].id + '">' + retval.playlists[i].title + "</option>";
                            }
                            $("#add-to-playlist-combobox").html(playlists_html);
                            $("#overlay").fadeIn ("fast", function () {
                                $("#add-to-playlist-dialog").fadeIn ("fast");
                            });
                        }
                    },
                    "json"
                );
            });
            $('#add-to-playlist-cancel').click (function () {
                $("#add-to-playlist-dialog").fadeOut ("fast", function () {
                    $("#overlay").fadeOut ("fast");
                });
            });
            $('#add-to-playlist-ok').click (function () {
                var id = $("#add-to-playlist-combobox option:selected").val();
                var checked = $(".song-selector:checked");
                if (checked.length > 0) {
                    var selected = new Array ();
                    for (var i = 0; i < checked.length; i++) {
                        selected.push($(checked[i]).val());
                    }
                    $.post("/library/playlists/" + id + '/',
                        { action: 'add', ids: selected },
                        function (retval) {
                            $("#add-to-playlist-dialog").fadeOut ("fast", function () {
                                $("#overlay").fadeOut ("fast");
                            });
                        },
                        "json"
                    );
                }
            });
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
                <tr><td><a id="edit-album" href="#">(edit)</a></td></tr>
            </table>
            <div id="album-info-editor">
                <form id="album-editor-form" action="/library/music/byalbum/{{album.id}}/" method="post">
                    <input type="hidden" name="is-playlist" value="false" />
                    <table id="album-info-table">
                        {{ editor.as_table }}
                    </table>
                    <input id="edit-cancel" type="button" value="cancel"/><input id="edit-save" type="submit" value="save" />
                </form>
            </div>
        </div>
        <table class="display" id="song-listing">
            <thead>
                <th class="song-header">Track</th>
                <th class="song-header">Title</th>
                <th class="song-header">Duration</th>
                <th class="song-header"></th>
            </thead>
            <tbody>
            {% for song in song_list %}
                <tr>
                <td class="song-tracknumber">{{song.track_number}}</td>
                <td class="song-title"><a href="/library/music/bysong/{{song.id}}/">{{song.name}}</a></td>
                <td>{{song.print_duration}}</a></td>
                <td><input class="song-selector" type="checkbox" value="{{song.id}}"/></td>
                </tr>
            {% endfor %}
            </tbody>
        </table>
    </p>
</div>
<div id="album-actions">
    <input class="album-action" id="select-all-action" type="button" value="Select All" />
    <input class="album-action" id="unselect-all-action" type="button" value="Unselect All" />
    <input class="album-action" id="add-to-playlist-action" type="button" value="Add Selected To Playlist" />
</div>
<div id="add-to-playlist-dialog">
    <p id="add-to-playlist-form">
        Select a playlist to add these songs to:
        <p>
            <select id="add-to-playlist-combobox"></select>
        </p>
        <table id="add-to-playlist-buttons">
            <tr>
                <td><input id="add-to-playlist-cancel" type="button" value="Cancel" /></td>
                <td><input id="add-to-playlist-ok" type="button" value="OK" /></td>
            </tr>
        </table>
    </p>
</div>
<div id="overlay"></div>
{% endblock %}
