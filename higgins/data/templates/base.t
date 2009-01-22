<html>
<head>
    <link href="/static/css/base.css" rel="stylesheet" type="text/css" media="screen"/>
    {% block stylesheet %}{% endblock %}
    <title>{% block title %}Higgins{% endblock %}</title>
</head>
<body>

<div id="enclosure">
    <div id="higgins-title">Higgins</div>
    <table id="higgins-nav">
        <tr id="higgins-nav-row">
            <td id="higgins-nav-home"><a href="/">Home</a></td>
            <td id="higgins-nav-browse"><a href="/browse/">Browse</a></td>
            <td id="higgins-nav-search"><a href="/search/">Search</a></td>
            <td id="higgins-nav-settings"><a href="/settings/">Settings</a></td>
            <td> </td>
        </tr>
    </table>
    {% block content %}{% endblock %}
</div>

</body>
</html>
