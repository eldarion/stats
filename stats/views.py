from datetime import datetime, timedelta

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import simplejson
from django.utils.hashcompat import sha_constructor

from django.contrib.auth.models import User


def stats():
    return {
        "user_count": User.objects.count(),
        
        "joined_last_seven_days": User.objects.filter(date_joined__gt=datetime.now() - timedelta(days=7)).count(),
        "joined_last_thirty_days": User.objects.filter(date_joined__gt=datetime.now() - timedelta(days=30)).count()
    }


def stats_json(request):
    
    checks = [request.user.is_staff]
    
    if hasattr(settings, "STATS_AUTH_KEY"):
        key = "%s-%d" % (settings.STATS_AUTH_KEY, datetime.utcnow().timetuple().tm_yday)
        header = "HTTP_X_STATS_TOKEN"
        checks.append(sha_constructor(key).hexdigest() == request.META.get(header, ""))
    
    if any(checks):
        d = stats()
        for app in getattr(settings, "STATS_APPS", []):
            m = __import__(app + ".stats", globals(), locals(), ["stats"])
            d.update(m.stats())
        
        json_data = simplejson.dumps(d, ensure_ascii=False)
        return HttpResponse(json_data, mimetype="application/json; charset=utf-8")
    else:
        return redirect("home")
