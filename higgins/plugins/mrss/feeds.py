from django.shortcuts import render_to_response

def feeds_front(request):
    return render_to_response('higgins.plugins.mrss.templates:front.t')
