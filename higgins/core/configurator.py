from django import forms

class Configurator(forms.Form):
    config_title = None
    config_description = None

    def __init__(self, settings):
        forms.Form.__init__(self, settings)

#    def as_table(self):
#        out = []
#        for f in self:
#            out.append("<tr>")
#            out.append("<th><div class='higgins-config-setting-name'>%s</div></th>" % f.label)
#            out.append("<td><div class='higgins-config-setting-value'>%s</div></td>" % str(f))
#            out.append("</tr>")
#        return ''.join(out)

class IntegerSetting(forms.IntegerField):
    def __init__(self, label, **kwds):
        forms.IntegerField.__init__(self, kwds)
        self.label = label

class StringSetting(forms.CharField):
    def __init__(self, label, **kwds):
        forms.CharField.__init__(self, kwds)
        self.label = label
