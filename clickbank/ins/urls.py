from django.conf.urls.defaults import *

urlpatterns = patterns('clickbank.ins.views',
    url(r'^$', 'ins', name="clickbank-ins"),
    )
