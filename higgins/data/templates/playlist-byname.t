{% extends "templates/library-base.t" %}

{% block stylesheet %}
    <link href="/static/css/playlists.css" rel="stylesheet" type="text/css" media="screen"/>
    <link type="text/css" href="/static/css/smoothness/jquery-ui-1.7.custom.css" rel="stylesheet" />
    <script type="text/javascript" language="javascript" src="/static/js/jquery-1.3.2.min.js"></script>
    <script type="text/javascript" language="javascript" src="/static/js/jquery-ui-1.7.min.js"></script>
    <script type="text/javascript" language="javascript" src="/static/js/datatables-1.4.min.js"></script>
    <script type="text/javascript" language="javascript" src="/static/js/center-1.1.2.js"></script>
    <script type="text/javascript" charset="utf-8">
        $(document).ready(function() {
            $('#playlist-listing').dataTable( {
                'bPaginate': false,
                'bLengthChange': true,
                'bFilter': false,
                'bSort': true,
                'bInfo': true,
                'bAutoWidth': true
            });
            $('#add-playlist').click (function () {
                $("#add-playlist-dialog").css ({
                    position: 'absolute',
                    top: ($(window).height()/2) - ($('#add-playlist-dialog').height()/2),
                    left: ($(window).width()/2) - ($('#add-playlist-dialog').width()/2),
                });
                $("#overlay").fadeIn ("fast", function () {
                    $("#add-playlist-dialog").fadeIn ("fast");
                });
            });
            $('#playlist-cancel').click (function () {
                $("#add-playlist-dialog").fadeOut ("fast", function () {
                    $("#overlay").fadeOut ("fast");
                });
            });
        });
</script>
{% endblock %}

{% block title %}Browse playlists{% endblock %}

{% block library_content %}
<div id="playlists-actions">
    <input id="add-playlist" type="button" value="Create Playlist" />
</div>
<table class="display" id="playlist-listing">
    <thead>
        <th class="playlist-header">Name</th>
        <th class="playlist-header">Items</th>
    </thead>
    <tbody>
    {% for playlist in pl_list %}
        <tr>
            <td><a href="/library/playlists/{{playlist.id}}/">{{ playlist.name }}</a></td>
            <td>{{ playlist.length }}</td>
        </tr>
    {% endfor %}
    </tbody>
</table>
<div id="add-playlist-dialog">
    <form id="add-playlist-form" action="/library/playlists/" method="post">
        Enter a name for the new playlist:
        <p>
            <input id="playlist-title" type="text" name="name" value="New Playlist" maxlength="80" />
        </p>
        <table id="add-playlist-buttons">
            <tr>
                <td><input id="playlist-cancel" type="button" value="Cancel" /></td>
                <td><input id="create-playlist" type="submit" value="OK" /></td>
            </tr>
        </table>
    </form>
</div>
<div id="overlay"></div>
{% endblock %}
