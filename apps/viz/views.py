# For Django
from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404
from apps.viz.models import *
# For general Use
from collections import defaultdict
import json
import time

def home(request):
	return render_to_response('index.html')

# Treemaps
def treemap_of_exports(request, country_code = None, year = None):
	import time
	s = time.time()
	c = Country.objects.get(name_3char=country_code) if country_code else Country.objects.get(name_3char='deu')
	y = year if year else 2000

	cpys = c.comtrade_cpys.filter(year=y, rca__gte=1)
	exports = defaultdict(lambda: [])
	for cpy in cpys:
		# exports[cpy.product.leamer.id].append(cpy.export_value)
		exports[cpy.product.leamer.id].append((cpy.export_value, cpy.product.leamer.color, cpy.product.name))
		
	# return HttpResponse(time.time() - s)
	# return HttpResponse(json.dumps(exports.values()))
	return render_to_response('treemap_of_exports.html', {'data': json.dumps(exports.values())})

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
	c = Country.objects.get(name_3char='deu')
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

def proximity_network(request, product_code=78, num_neighbors=5):
	# Is this an ajax request (ie did we just double click a node?)
	format = request.GET.get('format', False)
	# What is the ID of the node we're getting data for?
	try:
		if format:
			a_product = Sitc4.objects.get(pk=product_code)
		else:	
			a_product = Sitc4.objects.get(code=product_code)
	except Sitc4.DoesNotExist:
		a_product = Sitc4.objects.get(pk=78)
	# Get all products so that we can add metadata (eg color, name, size) when we return it
	products = Sitc4.objects.all()
	# Assign to default to empty lists
	product_dict_of_countries = defaultdict(lambda: [])
	# Get all CPYs for given year and RCA threshold
	cpys = Sitc4_comtrade_cpy.objects.filter(year = 2001, rca__gte = 1.2)#.values_list('product_id', 'product__name', 'product__leamer__color')
	# Loop through each item and append country_ids to list whose key is the product
	for cpy in cpys:
		product_dict_of_countries[cpy.product_id].append(cpy.country_id)
	#
	my_set_of_countries = set(product_dict_of_countries[a_product.id])
	# This will hold ALL the products with their proximities
	proximity_list = []
	# For each product's list of countries see if there is any
	# overlap (intersection) with the given product_id's list of countries, this
	# will be the numerator. Also, for each product's list of countries find
	# which has a longer length and use this as the denominator
	for product_id, country_list in product_dict_of_countries.items():
		# see if there is any intersection
		if my_set_of_countries.intersection(set(country_list)):
			# this will be the numerator i.e. the number of countries that both
			# export the given product with RCA > given threshold
			number_of_countries_in_intersection = len(my_set_of_countries.intersection(set(country_list)))
			# find the max of the length of the two sets
			# this will be the denominator in this specific proximity function
			max_countries = max(len(my_set_of_countries), len(country_list))
			# here we find the proximity
			# WARNING: need to convert at least one value to a float so python will
			# return floating point values
			proximity = number_of_countries_in_intersection / float(max_countries)
			# now add it to the dictionary EXCEPT if it is the given product
			if product_id != a_product.id:
				proximity_list.append((product_id, proximity))
				# prox_dict[product_id] = proximity
				# this_product = products.get(pk=product_id)
				# prox_dict[product_id] = [this_product.name, this_product.code, this_product.leamer.color, proximity, this_product.ps_size]
	# to be returned
	data = {}
	proximity_list.sort(key=lambda tup:-tup[1])
	while len(data) < int(num_neighbors):
		this_product = products.get(pk=proximity_list[len(data)][0])
		data[proximity_list[len(data)][0]] = [this_product.name, this_product.code, this_product.leamer.color, proximity_list[len(data)][1], this_product.ps_size]
	#
	if format:
		return HttpResponse(json.dumps(data))
	return render_to_response('proximity_network.html', {'selected_product':a_product, 'data': json.dumps(data)})

def test(request, year, path):
	return HttpResponse(year, path)