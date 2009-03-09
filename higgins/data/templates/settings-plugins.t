{% extends "templates/settings-base.t" %}

{% block title %}Edit Services{% endblock %}

{% block settings_content %}
    <p id="higgins-settings-description">
        All available plugins are listed below.  Checked plugins are currently running.
        To disable a plugin, uncheck it and click the Update Plugins button.  To configure
        a specific plugin, click on its Settings link.
    </p>
    <p>
    <form id="higgins-settings-form" method="post" action="">
        <table id="higgins-settings-plugins">{% for plugin in plugins %}
            <tr>
                <td>
                    <input type="checkbox"
                           name="{{plugin.name}}"
                           value="enabled"{% if plugin.running %} checked="true"{% endif %} />
                </td>
                <td>
                    <span class="higgins-settings-plugin-name">{{plugin.pretty_name}}</span>
                    <br/>
                    <span class="higgins-settings-plugin-descripton">{{plugin.description}}<span>
                </td>
                <td>
                    {% ifnotequal plugin.configs None %}<a href="{{plugin.name}}/">Settings</a>{% endifnotequal %}
                </td>
            </tr>
        {% endfor %}</table>
        <p>
            <input id="higgins-settings-submit" type="submit" value="Update Plugins"/>
        </p>
    </form>
    </p>
{% endblock %}
