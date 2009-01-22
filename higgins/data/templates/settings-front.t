{% extends "base.t" %}

{% block stylesheet %}
    <link href="/static/css/settings.css" rel="stylesheet" type="text/css" media="screen"/>
{% endblock %}

{% block title %}Settings{% endblock %}

{% block content %}
<p>
    System settings go here
</p>
<p><a href="/settings/services/">Configure Services</a></p>
{% endblock %}
