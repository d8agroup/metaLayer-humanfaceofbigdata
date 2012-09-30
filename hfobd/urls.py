from django.conf.urls import patterns, include, url
from hfobd.solrbridge.views import push_data_one

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
from hfobd import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hfobd.views.home', name='home'),
    # url(r'^hfobd/', include('hfobd.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^push/data$', push_data_one),
    url(r'^get_graph_data$', views.get_graph_data),
    url(r'^get_graph_data2$', views.get_graph_data2),
    url(r'^get_graph_data3$', views.get_graph_data3),
    url(r'^add_a_filter$', views.add_a_filter),
    url(r'^chart_area$', views.chart_area),
#    url(r'design1', views.design1),
    url(r'^save_and_share$', views.save_and_share),
    url(r'old', views.home),
    url(r'', views.design2),
)
