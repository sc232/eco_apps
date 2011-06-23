# For Django
from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404
from apps.viz.models import *
# For general Use
from collections import defaultdict
from django.utils import simplejson as json
import time

# from django.db.models import Avg, Max, Min, Count, Sum
# x = Sitc4_feenstra_cpy.objects.values('country_id').annotate(total_exports=Sum('export_value'))

def home(request):
	return render_to_response('index.html')

"""
based on a specified importer I, exporter E, and year Y:
  creates a treemap of all products imported by the I from E in Y
"""
def treemap_of_bilateralTrade(request):
	#get country DB object based on args from the URL string
	qImp = request.GET.get('imp', False)
	impObj = Country.objects.get(name_3char=qImp)
	qExp = request.GET.get('exp', False)
	expObj = Country.objects.get(name_3char=qExp)
	qYear = request.GET.get('y', False)

	#get the list of products that are traded between the 2 countries
	products = impObj.trade_ImpCountries.filter(year=qYear).filter(exporter=expObj.id).values("product").annotate(Sum("import_value")).order_by("import_value__sum")

#for each product traded
	imports = defaultdict(lambda: [])
	for p in products:			
	#get the leamer ID & color
		productObj = Sitc4.objects.get(id=p["product"])   
		name = productObj.name
		leamerID = productObj.leamer.id
		leamerColor = productObj.leamer.color
		importValueSum = p["import_value__sum"];
	#	if importValueSum < 5 :
#			continue

		#add the product to the list which ecorresponds to its leamer ID
		imports[leamerID].append((importValueSum, leamerColor, name,1))

	title = "Exports from %s to %s in %s" % ( expObj.name, impObj.name, qYear)


# return HttpResponse(time.time() - s)
#	return HttpResponse(json.dumps(partners.values()))
	return render_to_response('treemap_of_bilateralTrade.html', {'data': json.dumps(imports.values()),'title':title, 'coloring':'rca'})


"""
based on a specified country C, its role R (as importer or exporter), and year Y:
  creates a treemap of all products that C traded in year Y. If we care about C as an importer, then create a treemap of products which C imported.
"""
def treemap_of_countryProducts(request):
	#get country object
	qCou = request.GET.get('c', False)
	countryObj = Country.objects.get(name_3char=qCou)

	#get whether we care about this country as an importer or exporter
	qRole = request.GET.get('r', False)
	#get year
	qYear = request.GET.get('y', False)

	#get all products traded by this country
	cpys = countryObj.comtrade_cpys.filter(year=qYear, rca__gte=1)

	#for each product traded
	products = defaultdict(lambda: [])
	for cpy in cpys:
		print cpy
		#figure out whether we wanted the amount imported or exported (based on the role variable)
		currValue = cpy.export_value if qRole == 'exp' else cpy.import_value
		#add the product to the list with the correct leamer ID
		products[cpy.product.leamer.id].append((currValue, cpy.product.leamer.color, cpy.product.name,1))

	#generate Page title 	
	title = "Products %s by %s in %s" % ( "Exported" if qRole == 'exp' else "Imported", countryObj.name,qYear)

	# return HttpResponse(time.time() - s)
	# return HttpResponse(json.dumps(exports.values()))
	return render_to_response('treemap_of_countryProducts.html', {'data': json.dumps(products.values()), 'title' : title,'coloring':'rca' })


# Treemaps
def treemap_of_exports(request, country_code = None, year = None):
	# Is this an ajax request (ie did we just double click a node?)
	coloring = request.GET.get('coloring', 'rca')

	import time
	s = time.time()
	c = Country.objects.get(name_3char=country_code) if country_code else Country.objects.get(name_3char='deu')
	y = year if year else 2000

	cpys = c.comtrade_cpys.filter(year=y, rca__gte=1)
	exports = defaultdict(lambda: [])
	for cpy in cpys:
		if coloring == "net":
			exports[cpy.product.leamer.id].append((cpy.export_value, cpy.product.leamer.color, cpy.product.name, cpy.export_value - cpy.import_value))
		elif coloring == "rca":
			exports[cpy.product.leamer.id].append((cpy.export_value, cpy.product.leamer.color, cpy.product.name, cpy.rca))

	# return HttpResponse(time.time() - s)
	# return HttpResponse(json.dumps(exports.values()))
	return render_to_response('treemap_of_exports.html', {'data': json.dumps(exports.values()), 'coloring': coloring})



def treemap_of_imports(request):
	return render_to_response('treemap_of_imports.html')

	# return HttpResponse(json.dumps(exports.values()))
	return render_to_response('treemap_of_countryProducts.html', {'data': json.dumps(products.values()), 'title' : title })

"""
based on a specified product P, the traders' role of interest R (as importers or exporters), and year Y:
  creates a treemap of all importers(or exporters depending on R) of P in year Y. 
"""
def treemap_of_productTraders(request):
	regionColor = { "LCN": "#00FF00", "ECS": "#CC0099", "SAS":"#0000FF", "SSF" : "#FFFF00", "MEA":"#CC9900", "EAS" : "#FF0000", "NAC": "#00FFFF", "NA" : "#660000", "" : "#FFFFFF"}

	qProd = request.GET.get('p', False)
	prodObj = Sitc4.objects.get(id=qProd)
	#get whether we care about the importers or exporters
	qRole = request.GET.get('r', False)
	#get year
	qYear = request.GET.get('y', False)
	
	cpys = prodObj.comtrade_product_cpys.filter(year=qYear, rca__gte=1)

	traders = defaultdict(lambda: [])
	for cpy in cpys:
		currTrader = cpy.country 
		if currTrader.name == "World": 
			continue
		regionID = currTrader.region_id
		currColor = regionColor.get(regionID,"#000000")

		value = cpy.export_value if qRole == 'exp' else cpy.import_value

		#add this trade partner to the correct list depending on their region
		traders[regionID].append((value, currColor, currTrader.name, 0))

	title = "%s of '%s' in %s" % ( "Exporters" if qRole == 'exp' else "Importer", prodObj.name, qYear)

	return render_to_response('treemap_of_productTraders.html', {'data': json.dumps(traders.values()), 'title':title, 'coloring': 'rca'})



"""
based on a specified country C, its role R (as importer or exporter), and year Y:
  creates a treemap of all trade partners of C in year Y. If we care about C as an importer, then create a treemap of countries which exported to C.
"""
def treemap_of_tradePartners(request):
	#determines the color associated with a particular region in the world
	regionColor = { "LCN": "#00FF00", "ECS": "#CC0099", "SAS":"#0000FF", "SSF" : "#FFFF00", "MEA":"#CC9900", "EAS" : "#FF0000", "NAC": "#00FFFF", "NA" : "#660000", "" : "#FFFFFF"}

	#get country object
	qCou = request.GET.get('c', False)
	countryObj = Country.objects.get(name_3char=qCou)
	#get whether we care about this country as an importer or exporter
	qRole = request.GET.get('r', False)
	#get year
	qYear = request.GET.get('y', '1999')


	#look at different rows depending on whether we are interested in this country as an importer or exporter
	relevantRows = countryObj.trade_ImpCountries if qRole == 'exp' else countryObj.trade_ExpCountries
	partnerField = "exporter" if qRole == 'exp' else "importer"
	#gets a dictionary of trade partners and how much was imported from them
 	partnerRows = relevantRows.filter(year=qYear)

	#   filter by product ID
	qProd = request.GET.get('p', False)
	if qProd :
		partnerRows = partnerRows.filter(product=qProd)

	partnerRows = partnerRows.values(partnerField).annotate(Sum("import_value")).order_by("import_value__sum")

	#for each trade partner
	partners = defaultdict(lambda: [])
	for p in partnerRows:		
		print p
		#figure out which region they are part of
		partnerObj = Country.objects.get(id=p[partnerField])
		name = partnerObj.name
		if name == "World": 
			continue
		
		regionID = partnerObj.region_id
		currColor = regionColor.get(regionID,"#000000")
		#add this trade partner to the correct list depending on their region
		partners[regionID].append((p["import_value__sum"], currColor,name,0))

	title = "%s Partners of %s in %s" % ("Export" if qRole == 'exp' else "Import", countryObj.name, qYear)


	#	print "%s\t%s" %( Country.objects.get(id=p[partnerField]), p['import_value__sum'] )

	# return HttpResponse(time.time() - s)
	return render_to_response('treemap_of_tradePartners.html', {'data': json.dumps(partners.values()), 'title':title, 'coloring': 'rca'})








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
