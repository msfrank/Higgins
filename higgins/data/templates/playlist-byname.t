{% extends "templates/library-base.t" %}

{% block stylesheet %}
    <link href="/static/css/playlists.css" rel="stylesheet" type="text/css" media="screen"/>
    <link type="text/css" href="/static/css/smoothness/jquery-ui-1.7.custom.css" rel="stylesheet" />
    <script type="text/javascript" language="javascript" src="/static/js/jquery-1.3.2.min.js"></script>
    <script type="text/javascript" language="javascript" src="/static/js/jquery-ui-1.7.min.js"></script>
    <script type="text/javascript" language="javascript" src="/static/js/datatables-1.4.min.js"></script>
    <script type="text/javascript" language="javascript" src="/static/js/center-1.1.2.js"></script>

    <script type="text/javascript" charset="utf-8">
        var selectedRow = -1;

        $(document).ready(function() {
            /*
             * attach the DataTable instance to #playlist-listing
             */
            playlistsTable = $('#playlist-listing').dataTable( {
                'bPaginate': false,
                'bLengthChange': true,
                'bFilter': false,
                'bSort': true,
                'bInfo': true,
                'bAutoWidth': true,
                'aoColumns': [
                    null,
                    null,
                    { "bVisible": false },
                    { "bVisible": false },
                    { "sWidth": "3%", 'sClass': 'playlist-rename-column' },
                    { "sWidth": "3%", 'sClass': 'playlist-remove-column' }
                ]
            });
 
            /*
             * create playlist callbacks
             */
            $('#create-playlist-action').click (function () {
                $('#create-playlist-title').val('');
                $("#create-playlist-dialog").css ({
                    position: 'absolute',
                    top: ($(window).height()/2) - ($('#create-playlist-dialog').height()/2),
                    left: ($(window).width()/2) - ($('#create-playlist-dialog').width()/2),
                });
                $("#overlay").fadeIn ("fast", function () {
                    $("#create-playlist-dialog").fadeIn ("fast");
                });
            });
            $('#create-playlist-cancel').click (function () {
                $("#create-playlist-dialog").fadeOut ("fast", function () {
                    $("#overlay").fadeOut ("fast");
                });
            });
            $('#create-playlist-ok').click (function () {
                $.post("/library/playlists/",
                    { action: 'create', title: $('#create-playlist-title').val() },
                    function (retval) {
                        if (retval.status == 200) {
                            playlistsTable.fnAddData ([
                            /* title */
                            '<a href="/library/playlists/' + retval.id + '/">' + retval.title + '</a>',
                            /* nitems */
                            '0',
                            /* playlist title */
                            retval.title,
                            /* playlist id */
                            retval.id,
                            /* rename button */
                            '<a class="rename-button" href="#" value="' + retval.id + '">' +
                            '<span class="ui-state-default ui-corner-all ui-icon ui-icon-pencil" title="Rename ' + retval.title + '"></span>' +
                            '</a>',
                            /* remove button */
                            '<a class="remove-button" href="#" value="' + retval.id + '">' +
                            '<span class="ui-state-default ui-corner-all ui-icon ui-icon-trash" title="Remove ' + retval.title + '"></span>' +
                            '</a>'
                            ]);
                        }
                    },
                    "json"
                );
                $("#create-playlist-dialog").fadeOut ("fast", function () {
                    $("#overlay").fadeOut ("fast");
                });
            });

            /*
             * rename callbacks
             */
            $('.rename-button').click (function () {
                var tr = this.parentNode.parentNode;
                selectedRow = playlistsTable.fnGetPosition (tr);
                var row = playlistsTable.fnGetData(selectedRow);
                $('#rename-playlist-title').val(row[2]);
                $("#rename-playlist-dialog").css ({
                    position: 'absolute',
                    top: ($(window).height()/2) - ($('#rename-playlist-dialog').height()/2),
                    left: ($(window).width()/2) - ($('#rename-playlist-dialog').width()/2),
                });
                $("#overlay").fadeIn ("fast", function () {
                    $("#rename-playlist-dialog").fadeIn ("fast");
                });
            });
            $('#rename-playlist-cancel').click (function () {
                selectedRow = -1;
                $("#rename-playlist-dialog").fadeOut ("fast", function () {
                    $("#overlay").fadeOut ("fast");
                });
            });
            $('#rename-playlist-ok').click (function () {
                var row = playlistsTable.fnGetData (selectedRow);
                $.post("/library/playlists/",
                    { action: 'rename', id: row[3], title: $('#rename-playlist-title').val() },
                    function (retval) {
                        if (retval.status == 200) {
                            playlistsTable.fnUpdate (
                                '<a href="/library/playlists/' + row[2] + '">' + $('#rename-playlist-title').val() + '</a>',
                                selectedRow,
                                0
                            );
                            selectedRow = -1;
                            $("#rename-playlist-dialog").fadeOut ("fast", function () {
                                $("#overlay").fadeOut ("fast");
                            });
                        }
                    },
                    "json"
                );
            });

            /*
             * remove callbacks
             */
            $('.remove-button').click (function () {
                selectedRow = playlistsTable.fnGetPosition (this.parentNode.parentNode);
                $("#remove-playlist-dialog").css ({
                    position: 'absolute',
                    top: ($(window).height()/2) - ($('#remove-playlist-dialog').height()/2),
                    left: ($(window).width()/2) - ($('#remove-playlist-dialog').width()/2),
                });
                $("#overlay").fadeIn ("fast", function () {
                    $("#remove-playlist-dialog").fadeIn ("fast");
                });
            });
            $('#remove-playlist-cancel').click (function () {
                selectedRow = -1;
                $("#remove-playlist-dialog").fadeOut ("fast", function () {
                    $("#overlay").fadeOut ("fast");
                });
            });
            $('#remove-playlist-ok').click (function () {
                var row = playlistsTable.fnGetData (selectedRow);
                $.post("/library/playlists/",
                    { action: 'delete', id: row[3] },
                    function (retval) {
                        if (retval.status == 200) {
                            playlistsTable.fnDeleteRow (selectedRow);
                            selectedRow = -1;
                            $("#remove-playlist-dialog").fadeOut ("fast", function () {
                                $("#overlay").fadeOut ("fast");
                            });
                        }
                    },
                    "json"
                );
            });
        });
</script>

{% endblock %}

{% block title %}Browse playlists{% endblock %}

{% block library_content %}
<div id="playlists-actions">
    <input id="create-playlist-action" type="button" value="Create Playlist" />
</div>
<table class="display" id="playlist-listing">
    <thead>
        <th class="playlist-header">Name</th>
        <th class="playlist-header">Items</th>
        <th></th>
        <th></th>
        <th></th>
        <th></th>
    </thead>
    <tbody>
    {% for playlist in pl_list %}
        <tr>
            <td><a href="/library/playlists/{{playlist.id}}/">{{ playlist.name }}</a></td>
            <td>{{ playlist.length }}</td>
            <td>{{ playlist.name }}</td>
            <td>{{ playlist.id }}</td>
            <td>
                <a class="rename-button" href="#" value="{{playlist.id}}">
                <span class="ui-state-default ui-corner-all ui-icon ui-icon-pencil" title="Rename '{{playlist}}'"></span>
                </a>
            </td>
            <td>
                <a class="remove-button" href="#" value="{{playlist.id}}">
                <span class="ui-state-default ui-corner-all ui-icon ui-icon-trash" title="Remove '{{playlist.name}}'"></span>
                </a>
            </td>
        </tr>
    {% endfor %}
    </tbody>
</table>

<div id="create-playlist-dialog">
    <p id="create-playlist-form">
        Enter a name for the new playlist:
        <p>
            <input id="create-playlist-title" type="text" name="name" value="New Playlist" maxlength="80" />
        </p>
        <table id="create-playlist-buttons">
            <tr>
                <td><input id="create-playlist-cancel" type="button" value="Cancel" /></td>
                <td><input id="create-playlist-ok" type="button" value="OK" /></td>
            </tr>
        </table>
    </p>
</div>

<div id="rename-playlist-dialog">
    <p id="rename-playlist-form">
        Enter a new name for the playlist:
        <p>
            <input id="rename-playlist-title" type="text" name="name" value="" maxlength="80" />
        </p>
        <table id="rename-playlist-buttons">
            <tr>
                <td><input id="rename-playlist-cancel" type="button" value="Cancel" /></td>
                <td><input id="rename-playlist-ok" type="button" value="OK" /></td>
            </tr>
        </table>
    </p>
</div>

<div id="remove-playlist-dialog">
    <p id="remove-playlist-form">
        <p>
            Are you sure you want to delete this playlist?
        </p>
        <table id="remove-playlist-buttons">
            <tr>
                <td><input id="remove-playlist-cancel" type="button" value="Cancel" /></td>
                <td><input id="remove-playlist-ok" type="button" value="OK" /></td>
            </tr>
        </table>
    </p>
</div>


<div id="overlay"></div>
{% endblock %}
