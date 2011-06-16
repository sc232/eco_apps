from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'apps.viz.views.home'),
	# Treemaps
    (r'^treemap_of_exports/$', 'apps.viz.views.treemap_of_exports'),
    (r'^treemap_of_imports/$', 'apps.viz.views.treemap_of_imports'),
	# Product Space
    (r'^product_space/$', 'apps.viz.views.product_space'),
	# Stacked
    (r'^stacked_share/$', 'apps.viz.views.stacked_share'),
    (r'^stacked_value/$', 'apps.viz.views.stacked_value'),
	# Proximity
    (r'^proximity_network/$', 'apps.viz.views.proximity_network'),
    (r'^proximity_network/(?P<product_code>\d+)$', 'apps.viz.views.proximity_network'),

	(r'^test/(?P<year>\d+)/(?P<path>.*)$', 'apps.viz.views.test'),

	# Serve static files for dev
	(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/alexandersimoes/Sites/eco_apps/media', 'show_indexes': True}),
)
