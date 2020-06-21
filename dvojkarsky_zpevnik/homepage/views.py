import os
from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import SongsForm
from .utils import produce_songs_pdf
from django.http import HttpResponse, Http404


def download(request, path):
    if os.path.exists(path):
        with open(path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path)
            return response
    raise Http404


# View part


def home(request):
    return render(request, 'homepage/home.html')


class DownloadView(TemplateView):
    template_name = 'homepage/download.html'

    def get(self, request, *args, **kwargs):
        form = SongsForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = SongsForm(request.POST)
        if form.is_valid():
            songpdf, log = produce_songs_pdf(form.checkboxes())
            if songpdf is None:
                if log is None:
                    return render(request, 'homepage/message.html', {"text": "Nejde přeložit pdfko :-("})
                return render(request, 'homepage/message.html', {"text": log})
            return download(request, songpdf)
            # return render(request, 'homepage/message.html', {"text": log})

        return render(request, self.template_name, {"form": form})
