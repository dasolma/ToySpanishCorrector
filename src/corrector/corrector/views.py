from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
import corrector
import json

def index(request):
    return render(request, 'index.html', {})

def correct(request, word):
    word = word.encode('utf-8')
    return HttpResponse(json.dumps(corrector.correct(word)), "application/json")
