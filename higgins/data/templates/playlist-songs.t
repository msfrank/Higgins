{% extends "templates/library-base.t" %}

{% block stylesheet %}
    <link href="/static/css/playlist.css" rel="stylesheet" type="text/css" media="screen"/>
    <link type="text/css" href="/static/css/smoothness/jquery-ui-1.7.custom.css" rel="stylesheet" />
    <script type="text/javascript" language="javascript" src="/static/js/jquery-1.3.2.min.js"></script>
    <script type="text/javascript" language="javascript" src="/static/js/jquery-ui-1.7.min.js"></script>
    <script type="text/javascript" language="javascript" src="/static/js/datatables-1.4.min.js"></script>
    <script type="text/javascript" charset="utf-8">
        $(document).ready(function() {
            var playlistTable = $('#song-listing').dataTable( {
            "bPaginate": false,
            "bLengthChange": true,
            "bFilter": false,
            "bSort": false,
            "bInfo": true,
            "bAutoWidth": true,
            "aoColumns": [
                null,
                null,
                { "sWidth": "15%" },
                { "sWidth": "3%" }
            ]
        });

            var playlistTitle = "{{playlist.name}}"

            $('#edit-playlist').click (function () {
                playlistTitle = $("#edit-playlist-title").val();
                $("#playlist-info-viewer").fadeOut("def", function () {
                    $("#playlist-info-editor").fadeIn("def");
                });
            });

            $('#edit-cancel').click (function () {
                $("#playlist-info-editor").fadeOut("def", function () {
                    $("#edit-playlist-title").val(playlistTitle);
                    $("#playlist-info-viewer").fadeIn("def");
                });
            });

            $('#edit-save').click (function () {
                $.post("/library/playlists/{{playlist.id}}/",
                    {
                        action: 'edit',
                        id: {{playlist.id}},
                        title: $('#edit-playlist-title').val(),
                    },
                    function (retval) {
                        if (retval.status != 200) {
                            $("#edit-playlist-failure-reason").text (retval.reason);
                            $("#edit-playlist-warning-dialog").css ({
                                position: 'absolute',
                                top: ($(window).height()/2) - ($('#edit-playlist-warning-dialog').height()/2),
                                left: ($(window).width()/2) - ($('#edit-playlist-warning-dialog').width()/2)
                            });
                            $("#overlay").fadeIn ("fast", function () {
                                $("#edit-playlist-warning-dialog").fadeIn ("fast");
                            });
                        }
                        else {
                            playlistTitle = $("#edit-playlist-title").val ();
                            document.title = playlistTitle;
                            $("#playlist-info-editor").fadeOut("def", function () {
                                $("#playlist-title").val (playlistTitle);
                                $("#playlist-info-viewer").fadeIn("def");
                            });
                        }
                    },
                    "json"
                );
            });

            $('#edit-playlist-warning-ok').click (function () {
                $("#edit-playlist-warning-dialog").fadeOut ("fast", function () {
                    $("#overlay").fadeOut ("fast");
                });
            });

            $('.remove-button').click (function () {
                selectedRow = playlistTable.fnGetPosition (this.parentNode.parentNode);
                $.post("/library/playlists/{{playlist.id}}/",
                    { action: 'delete', indices: [selectedRow] },
                    function (retval) {
                        if (retval.status == 200) {
                            playlistTable.fnDeleteRow (selectedRow);
                            selectedRow = -1;
                        }
                    },
                    "json"
                );
            });
 
        });
</script>
{% endblock %}

{% block title %}{{ playlist.name }}{% endblock %}

{% block library_content %}
<div>
    <p>
        <div id="playlist-info-container">
            <table id="playlist-info-viewer">
                <tr><td id="playlist-title">{{ playlist.name }}</td></tr>
                <tr><td><a id="edit-playlist" href="#">(edit)</a></td></tr>
            </table>
            <div id="playlist-info-editor">
                <p>
                    <table id="playlist-info-table">
                        <tr>
                            <td>Playlist Name:</td>
                            <td><input id="edit-playlist-title" type="text" value="{{playlist.name}}"/></td>
                        </tr>
                    </table>
                </p>
                <input id="edit-cancel" type="button" value="Cancel"/><input id="edit-save" type="button" value="Save"/>
            </div>
        </div>
        <table class="display" id="song-listing">
            <thead>
                <th class="song-header">Title</th>
                <th class="song-header">Artist</th>
                <th class="song-header">Duration</th>
                <th class="song-header"></th>
            </thead>
            <tbody>
                {% for song in song_list %}<tr>
                    <td class="song-title">
                        <a href="/library/music/bysong/{{song.id}}/">{{song.name}}</a>
                    </td>
                    <td class="song-artist">
                        <a href="/library/music/byartist/{{song.artist.id}}/">{{song.artist.name}}</a>
                    </td>
                    <td>{{song.print_duration}}</a></td>
                    <td>
                        <a class="remove-button" href="#" value="{{song.id}}">
                        <span class="ui-state-default ui-corner-all ui-icon ui-icon-trash" title="Remove '{{song.name}}'"></span>
                        </a>
                    </td>
                </tr>{% endfor %}
            </tbody>
        </table>
    </p>
</div>
<div id="edit-playlist-warning-dialog">
    <p id="edit-playlist-form">
        <b>Failed to change playlist:</b>
        <p id="edit-playlist-failure-reason"></p>
        <table id="edit-playlist-buttons">
            <tr>
                <td><input id="edit-playlist-warning-ok" type="button" value="OK" /></td>
            </tr>
        </table>
    </p>
</div>
<div id="overlay"></div>
{% endblock %}
