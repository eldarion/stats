from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import simplejson

from django.contrib.auth.models import User


def stats():
    return {
        "user_count": User.objects.count(),
    }


def stats_json(request):
    
    if request.user.is_staff:
        d = stats()
        for app in getattr(settings, "STATS_APPS", []):
            m = __import__(app + ".stats", globals(), locals(), ["stats"])
            d.update(m.stats())
        
        json_data = simplejson.dumps(d, ensure_ascii=False)
        return HttpResponse(json_data, mimetype="application/json; charset=utf-8")
    else:
        return redirect("home")
