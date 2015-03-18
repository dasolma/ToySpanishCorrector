from django.conf.urls import patterns, include, url
from django.contrib import admin
import views, settings
from django.conf.urls.static import static
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'corrector.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^correct/(?P<word>\w+)$', views.correct, name='correct'),
    url(r'^$', views.index, name='index'),

) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
