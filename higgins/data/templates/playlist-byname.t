{% extends "templates/library-base.t" %}

{% block stylesheet %}
    <link href="/static/css/playlists.css" rel="stylesheet" type="text/css" media="screen"/>
    <link type="text/css" href="/static/css/smoothness/jquery-ui-1.7.custom.css" rel="stylesheet" />
    <script type="text/javascript" language="javascript" src="/static/js/jquery-1.3.2.min.js"></script>
    <script type="text/javascript" language="javascript" src="/static/js/jquery-ui-1.7.min.js"></script>
    <script type="text/javascript" language="javascript" src="/static/js/datatables-1.4.min.js"></script>
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
            $('#add-playlist').click (function () { $("#add-playlist-dialog").dialog () });
        });
</script>
{% endblock %}

{% block title %}Browse playlists{% endblock %}

{% block library_content %}
<div>
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
    <p>
        <a href="#" id="add-playlist">Create a new playlist</a>
    <p>
</div>
<div id="add-playlist-dialog" style="display: none" title="Add Playlist">
    Add playlist
    <form id="add-playlist-form" action="/library/playlists/" method="post">
        <table id="add-playlist-table">
            {{ creator.as_table }}
        </table>
        <input id="create-playlist" type="submit" value="create" />
    </form>
</div>
{% endblock %}
