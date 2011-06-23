from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'apps.viz.views.home'),
	# Treemaps
    (r'^treemap_of_bilateralTrade/$', 'apps.viz.views.treemap_of_bilateralTrade'),
    (r'^treemap_of_countryProducts/$', 'apps.viz.views.treemap_of_countryProducts'), 
    (r'^treemap_of_exports/$', 'apps.viz.views.treemap_of_exports'),
    (r'^treemap_of_exports/(?P<country_code>\w{3})$', 'apps.viz.views.treemap_of_exports'),
    (r'^treemap_of_exports/(?P<country_code>\w{3})/(?P<year>\d{4})$', 'apps.viz.views.treemap_of_exports'),
    (r'^treemap_of_imports/$', 'apps.viz.views.treemap_of_imports'),
    (r'^treemap_of_productTraders/$', 'apps.viz.views.treemap_of_productTraders'),
    (r'^treemap_of_tradePartners/$', 'apps.viz.views.treemap_of_tradePartners'),
	# Product Space
    (r'^product_space/$', 'apps.viz.views.product_space'),
	# Stacked
    (r'^stacked_share/$', 'apps.viz.views.stacked_share'),
    (r'^stacked_value/$', 'apps.viz.views.stacked_value'),
	# Proximity
    (r'^proximity_network/$', 'apps.viz.views.proximity_network'),
    (r'^proximity_network/(?P<product_code>\d+)/$', 'apps.viz.views.proximity_network'),
    (r'^proximity_network/(?P<product_code>\d+)/(?P<num_neighbors>\d{1,2})/$', 'apps.viz.views.proximity_network'),

	(r'^test/(?P<year>\d+)/(?P<path>.*)$', 'apps.viz.views.test'),
	
	(r'^map/$', 'apps.viz.views.map'),

	# Serve static files for dev
	 (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/sarah/Documents/mit/eco_apps/media', 'show_indexes': True}),
)
