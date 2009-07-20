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
