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
        $.post("/api/1.0/addPlaylist",
            { title: $('#create-playlist-title').val() },
            function (retval) {
                if (retval.status == 0) {
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
        $.post("/api/1.0/updatePlaylist",
            { playlistID: row[3], title: $('#rename-playlist-title').val() },
            function (retval) {
                if (retval.status == 0) {
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
        $.post("/api/1.0/deletePlaylist",
            { playlistID: row[3] },
            function (retval) {
                if (retval.status == 0) {
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
