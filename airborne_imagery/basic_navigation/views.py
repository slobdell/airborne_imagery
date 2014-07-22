from django.shortcuts import render_to_response


def home(request):
    render_data = {}
    return render_to_response("template.html", render_data)
