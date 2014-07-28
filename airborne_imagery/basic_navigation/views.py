from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render_to_response

from ..events.models import Event
from ..pictures.models import Picture


def home(request):
    render_data = {
        'recent_events': Event.get_events_by_most_recent(max_count=4),
        'recent_pictures': Picture.get_pictures_by_most_recent(max_count=5)
    }
    return render_to_response("basic_navigation/index.html", render_data)


def event(request, event_id):
    render_data = {}
    try:
        render_data['event'] = Event.get_by_id(event_id)
    except ObjectDoesNotExist:
        raise Http404
    render_data['pictures'] = Picture.get_pictures_from_event(render_data['event'])
    return render_to_response("basic_navigation/event.html", render_data)


def events(request):
    render_data = {
        'events': Event.get_events_by_most_recent(),
    }
    return render_to_response("basic_navigation/events.html", render_data)


def two_columns(request):
    return render_to_response("basic_navigation/page_2_columns_left.html", {})


def about(request):
    return render_to_response("basic_navigation/page_about_me.html", {})


def contact(request):
    return render_to_response("basic_navigation/page_contact2.html", {})


def invoice(request):
    return render_to_response("basic_navigation/page_invoice.html", {})


def privacy(request):
    return render_to_response("basic_navigation/page_privacy.html", {})


def registration(request):
    return render_to_response("basic_navigation/page_registration.html", {})


def portfolio(request):
    return render_to_response("basic_navigation/portfolio_text_blocks.html", {})
