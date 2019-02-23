from django.http import HttpResponse
from django.views.generic import View

from .utils import render_to_pdf #created in step 4

class GeneratePdf(View):
    def get(self, request, *args, **kwargs):

        pdf = render_to_pdf('main/administrator_dash.html',{})
        return HttpResponse(pdf, content_type='application/pdf')
