from django.shortcuts import render_to_response


def home(request):
    render_data = {}
    return render_to_response("index.html", render_data)
