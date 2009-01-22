{% extends "base.t" %}

{% block title %}Settings{% endblock %}

{% block content %}
<div>
    <form method="post" action="">
        <table>{{ config.as_table }}</table>
        <input type="submit" value="Save Settings"/>
    </form>
</div>
{% endblock %}
