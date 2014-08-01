import calendar
import datetime
import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render_to_response

from ..events.models import Event
from ..pictures.models import Picture
from ..pricing.models import Pricing


def add_to_cart(request):
    if 'cart' not in request.session:
        request.session['cart'] = {}
    picture_id = request.POST['pictureID']
    pricing_id = request.POST['pricingID']
    request.session['cart'][picture_id] = pricing_id
    request.session.modified = True
    return HttpResponse('', status=204)


def render_to_json(data, status=200):
    return HttpResponse(json.dumps(data), content_type="application/json", status=status)


def global_render_to_response(request, template, render_data):
    now = datetime.datetime.now()
    global_data = {
        'cart_count': len(request.session.get('cart', {})),
        'global_recent_events': Event.get_events_by_most_recent(max_count=3),
        'now_month': now.month,
        'now_year': now.year,
    }
    render_data.update(global_data)
    return render_to_response(template, render_data)


def _build_lightweight_calendar_datastructure(month, year):
    calendar_matrix = []
    num_empty_days_before_month_start = 0 if datetime.datetime.now().isoweekday() == 7 else datetime.datetime.now().isoweekday()
    week = [{"day": ""} for day in xrange(num_empty_days_before_month_start)]
    days_this_month = calendar.mdays[month]
    for day_counter in xrange(1, days_this_month + 1):
        week.append({"day": day_counter})
        if len(week) == 7:
            calendar_matrix.append(week)
            week = []
    calendar_matrix.append(week)
    return calendar_matrix


def calendar_month_year(request, month, year):
    month = int(month)
    year = int(year)
    pictures_this_month = Picture.get_pictures_in_month_and_year(month, year)
    day_to_picture = {str(picture.date_taken.day): picture for picture in pictures_this_month}
    calendar_matrix = _build_lightweight_calendar_datastructure(month, year)
    render_data = {
        'calendar_matrix': calendar_matrix,
        'day_to_picture': day_to_picture,
        'month': month,
        'year': year,
        'prev_year': year if month != 1 else year - 1,
        'prev_month': month - 1 if month != 1 else 12,
        'next_year': year if month != 12 else year + 1,
        'next_month': month + 1 if month != 12 else 1,
        'date_formatted': datetime.date(year=year, month=month, day=1).strftime("%B %Y")
    }
    return global_render_to_response(request, "basic_navigation/calendar.html", render_data)


def home(request):
    render_data = {
        'recent_events': Event.get_events_by_most_recent(max_count=4),
        'recent_pictures': Picture.get_pictures_by_most_recent(max_count=5)
    }
    return global_render_to_response(request, "basic_navigation/index.html", render_data)


def event(request, event_id):
    render_data = {}
    try:
        render_data['event'] = Event.get_by_id(event_id)
    except ObjectDoesNotExist:
        raise Http404
    render_data['pictures'] = Picture.get_pictures_from_event(render_data['event'])
    return global_render_to_response(request, "basic_navigation/event.html", render_data)


def events(request):
    render_data = {
        'events': Event.get_events_by_most_recent(),
    }
    return global_render_to_response(request, "basic_navigation/events.html", render_data)


def picture(request, picture_id):
    render_data = {}
    try:
        render_data['picture'] = Picture.get_by_id(picture_id)
    except ObjectDoesNotExist:
        raise Http404
    render_data['pricings'] = Pricing.get_all()
    return global_render_to_response(request, "basic_navigation/picture.html", render_data)


def pictures(request, month, day, year):
    render_data = {
        'pictures': Picture.get_pictures_in_month_day_year(int(month), int(day), int(year))
    }
    return global_render_to_response(request, "basic_navigation/pictures.html", render_data)


def two_columns(request):
    return global_render_to_response(request, "basic_navigation/page_2_columns_left.html", {})


def about(request):
    return global_render_to_response(request, "basic_navigation/page_about_me.html", {})


def contact(request):
    return global_render_to_response(request, "basic_navigation/page_contact2.html", {})


def invoice(request):
    return global_render_to_response(request, "basic_navigation/page_invoice.html", {})


def privacy(request):
    return global_render_to_response(request, "basic_navigation/page_privacy.html", {})


def registration(request):
    return global_render_to_response(request, "basic_navigation/page_registration.html", {})


def portfolio(request):
    return global_render_to_response(request, "basic_navigation/portfolio_text_blocks.html", {})
