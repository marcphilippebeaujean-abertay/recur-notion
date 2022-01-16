from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name = "pages/home.html"


class Imprint(TemplateView):
    template_name = "pages/imprint.html"


class DataPolicy(TemplateView):
    template_name = "pages/data-policy.html"
