$(document).ready(function() {
    $('#artist-editor-form').validate ({
        rules: {
            name: { required: true },
        },
        messages: {
            name: "Artist name is required",
        },
        submitHandler: function(form) {
            $(form).ajaxSubmit (function () {
                /* update the page elements */
                $("#artist-info-editor").fadeOut("def", function () {
                    $("#artist-info-viewer").fadeIn("def");
                });
            });
        }
    });

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
