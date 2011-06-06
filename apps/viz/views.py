from django.shortcuts import render_to_response
from django.http import HttpResponse

from apps.viz.models import *

import json

def home(request):
	return render_to_response('index.html')

# Treemaps
def treemap_of_exports(request):
	return render_to_response('treemap_of_exports.html')

def treemap_of_imports(request):
	return render_to_response('treemap_of_imports.html')

# Product Space
def product_space(request):
	# Query DB for a specific country
	c = Country.objects.get(name_3char='chn')
	# Get all CPY (country x product x year) objects in the specifed year that have X and Y coordinates
	cpys = c.feenstra_cpys.filter(year=1995, product__ps_x__isnull=False).order_by('rca')
	# To get our result we need to find out which products are exported by our 
	# chosen country and which aren't. We do this by taking the symmetric difference
	# of the two sets (A delta B)
	#
	# Here we turn our cpy result into a list with specific fields
	cpys_products_list = cpys.values_list('product__ps_x', 'product__ps_y', 'product__ps_size', 'product__name', 'product__leamer__color', 'product__leamer__name')
	# Her we get all the products from the DB as a list with the same items
	# as in our cpy list
	ps_products_list = Sitc4.objects.filter(ps_x__isnull=False).values_list('ps_x', 'ps_y', 'ps_size', 'name', 'leamer__color', 'leamer__name')
	# subtract the products this country exports from the total exports to get JUST
	# the ones that are missing (i.e. not exported by this country)
	missing_products_list = list(set(ps_products_list) - set(cpys_products_list))
	# Now get the list of CPYs exported by this country
	all_cpys_products_list = list(cpys.values_list('product__ps_x', 'product__ps_y', 'product__ps_size', 'product__name', 'product__leamer__color', 'product__leamer__name', 'export_value', 'export_share', 'rca'))
	# Added the CPYs this country exports to those that are missing (which we determined)
	all_cpys_products_list = missing_products_list + all_cpys_products_list
	# Convert the restult to JSON for use with the JS frontend
	ps_json = json.dumps(all_cpys_products_list)
	return render_to_response('product_space.html', {'data': ps_json})
	
# Stacked Area Charts
def stacked_share(request):
	# import time
	# start = time.time()
	# Query DB for a specific country
	c = Country.objects.get(name_3char='nor')
	data = {}
	years = [x for x in range(2001, 2010, 1)]
	# Get all data for the given country in the given year
	cpys = Sitc4_comtrade_cpy.objects.filter(country = c, year__in = years, rca__gte = 1).order_by('product__leamer', 'product')
	# Get a list of all the distinct products exports in the range of years
	distinct_products = cpys.values_list('product_id', 'product__name', 'product__leamer__color').distinct()
	#
	# Loop through each of the years and loop through each product to add null
	# or 0 values to the main data object
	for y in years:
		data[y] = {}
		for product in distinct_products:
			data[y][product[0]] = [0, product[1], product[2]]
	#
	# Add the actual values
	for cpy in cpys:
		data[cpy.year][cpy.product_id][0] = cpy.export_value
	#
	# Remove dictionaries and use arrays instead so we can sort them
	for y in data:
		data[y] = data[y].values()
		data[y].sort(key=lambda x: x[2])
	#
	# raise Exception(time.time() - start)
	stacked_json = json.dumps(data)
	return render_to_response('stacked_share.html', {'data': stacked_json})

def stacked_value(request):
	return render_to_response('stacked_value.html')