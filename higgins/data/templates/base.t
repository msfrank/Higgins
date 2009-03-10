<html>
<head>
    <link href="/static/css/base.css" rel="stylesheet" type="text/css" media="screen"/>
    {% block stylesheet %}{% endblock %}
    <title>{% block title %}Higgins{% endblock %}</title>
</head>
<body>

<div id="enclosure">
    <div id="higgins-title">Higgins</div>
    <div class="higgins-content-separator" />
    <table id="higgins-nav">
        <tr id="higgins-nav-row">
            <td class="higgins-nav-item"><a href="/">Home</a></td>
            <td class="higgins-nav-item"><a href="/browse/">Browse</a></td>
            <td class="higgins-nav-item"><a href="/search/">Search</a></td>
            {% for page in toplevel_pages %}
            <td class="higgins-nav-item"><a href="/view/{{page}}/">{{page}}</td>
            {% endfor %}
            <td class="higgins-nav-item"><a href="/settings/">Settings</a></td>
        </tr>
    </table>
    <div class="higgins-separator" />
    {% block subnav %}{% endblock %}
    <div id="higgins-content">
    {% block content %}{% endblock %}
    </div>
</div>

</body>
</html>
