$(document).ready(function() {
    $('#album-editor-form').validate ({
        rules: {
            title: { required: true },
            genre: { minlength: 1 },
            yearReleased: { range: [1900,2050], digits: true }
        },
        messages: {
            title: "Album Title is required",
            yearReleased: {
                digits: "Release year must be a number",
                range: "Release year is out of range"
            }
        },
        submitHandler: function(form) {
            $(form).ajaxSubmit (function () {
                /* update the page elements */
                $("#album-info-editor").fadeOut("def", function () {
                    $("#album-info-viewer").fadeIn("def");
                });
            });
        }
    });

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
            $('#album-editor-form').resetForm ();
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
        $.post("/api/1.0/listPlaylists",
            {blah: 'unused'},
            function (retval) {
                if (retval.status == 0) {
                    var playlists_html = '';
                    for (var i = 0; i < retval.nitems; i++) {
                        playlists_html += '<option value="' + 
                            retval.playlists[i].playlistID +
                            '">' +
                            retval.playlists[i].title +
                            "</option>";
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
            $.post("/api/1.0/addPlaylistItems",
                { playlistID: id, songIDs: selected },
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
