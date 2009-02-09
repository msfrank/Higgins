{% extends "settings-base.t" %}

{% block title %}Settings{% endblock %}

{% block settings_content %}
    <form method="post" action="">
        <table id="higgins-settings-configurator">{{ config.as_table }}</table>
        <input type="submit" value="Save Settings"/>
    </form>
{% endblock %}
