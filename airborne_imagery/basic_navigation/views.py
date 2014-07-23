from django.shortcuts import render_to_response


def home(request):
    render_data = {}
    return render_to_response("basic_navigation/index.html", render_data)


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
