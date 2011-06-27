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

def treemap_custom(request) :

	#get country DB object based on args from the URL string
	qImp = request.GET.get('imp', False)
	if qImp :
		impObj = Country.objects.get(name_3char=qImp)

	qExp = request.GET.get('exp', False)
	if qExp :
		expObj = Country.objects.get(name_3char=qExp)

	#specify a product or a leamer but not both
	qProd = request.GET.get('prod', False)
	if qProd : 
		prodObj = Sitc4.objects.get(id=qProd)
	else :
		qLeamer = request.GET.get('leam', False)
		if qLeamer : 
			leamerObj = Sitc4_leamer_objects.get(id=qLeamer)

	qHierarchy = request.GET.get('heir', False)

	#set a threshold value for inclusion
	qThreshold = request.GET.get('thr', False)
	qYear = request.GET.get('y', False)
	

# Can be intermediate: "trade_direction (IMP vs. EXP)", "importer(country_id)", "exporter(country_id)", "region(region_id)", "continent(continent)", "income", "product(SITC4)", "leamer(1-11)", "year"

#the last value in the hierarchy is the actual value
# Can only be last: "import_value","export_value, "total_trade", "net", "market_share"

	hierarchy = ["leamer","product"]


	products = impObj.trade_ImpCountries.filter(year=qYear, exporter=expObj.id).values("product").annotate(Sum("import_value")).order_by("import_value__sum")


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
	qThreshold = float(request.GET.get('thr', False))

	#get the list of products that are traded between the 2 countries
	products = impObj.trade_ImpCountries.filter(year=qYear, exporter=expObj.id).values("product").annotate(Sum("import_value")).order_by("import_value__sum")

#for each product traded
	imports = defaultdict(lambda: [])
	for p in products:			
	#get the leamer ID & color
		productObj = Sitc4.objects.get(id=p["product"])   
		name = productObj.name
		leamerID = productObj.leamer.id
		leamerColor = productObj.leamer.color
		importValueSum = p["import_value__sum"];
		#if user has defined a threshold value, then filter by it
		if qThreshold :			
			if importValueSum < qThreshold :	
				continue

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
	# imp, exp, net
	qVal = request.GET.get('v', False)

	#get year
	qYear = request.GET.get('y', False)

	#get threshold
	qThreshold = float(request.GET.get('thr',False))

	#get all products traded by this country
	cpys = countryObj.comtrade_cpys.filter(year=qYear, rca__gte=1)

	#for each product traded
	products = defaultdict(lambda: [])
	currValue = 0
	colorParam = 0
	
	for cpy in cpys:

		#figure out whether we wanted the amount imported or exported (based on the role variable)
	
		if qVal == "net" :
			currValue = cpy.export_value
			colorVal = cpy.export_value - cpy.import_value		
		else :
			currValue = cpy.import_value if qVal == "imp" else cpy.export_value
			colorVal = cpy.rca


		#if user has defined a threshold value, then filter by it
		if qThreshold :			
			if currValue < qThreshold :	
				continue


		#add the product to the list with the correct leamer ID
		products[cpy.product.leamer.id].append((currValue, cpy.product.leamer.color, cpy.product.name,colorVal))

	
#		print "%s , %s" % (cpy.product.name, currValue)
		
	for leamer in products:
		leamerObj = Sitc4_leamer.objects.get(id=leamer)
		print leamerObj.name
		print products[leamer]
		print "\n\n"

	#generate Page title 	
	title = ""
	colorScheme = ""
	if qVal == "net" :
		title = "Net trade by %s in %s" % (countryObj.name,qYear)
		colorScheme = "net"
	else :
		title = "Products %s by %s in %s" % ( "Exported" if qVal == 'exp' else "Imported", countryObj.name,qYear)
		colorScheme = "rca"

	# return HttpResponse(time.time() - s)
	# return HttpResponse(json.dumps(exports.values()))
	return render_to_response('treemap_of_countryProducts.html', {'data': json.dumps(products.values()), 'title' : title,'coloring': colorScheme})


# Treemaps
def treemap_of_exports(request, country_code = None, year = None):
	# Is this an ajax request (ie did we just double click a node?)
	coloring = request.GET.get('coloring', 'rca')
#	country_code = "mex"

	import time
	s = time.time()
	c = Country.objects.get(name_3char=country_code) if country_code else Country.objects.get(name_3char='deu')
	y = year if year else 2000

	cpys = c.comtrade_cpys.filter(year=y, rca__gte=1).order_by('-export_value')
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

	#get threshold
	qThreshold = float(request.GET.get('thr',False))

	
	cpys = prodObj.comtrade_product_cpys.filter(year=qYear, rca__gte=1)

	traders = defaultdict(lambda: [])
	for cpy in cpys:
		currTrader = cpy.country 
		if currTrader.name == "World": 
			continue
		regionID = currTrader.region_id
		currColor = regionColor.get(regionID,"#000000")

		value = cpy.export_value if qRole == 'exp' else cpy.import_value

		#if user has defined a threshold value, then filter by it
		if qThreshold :			
			if value < qThreshold :	
				continue


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


def map(request):
	data = [(251,100), (251,100), (251,100), (251,100), (251,99), (251,99), (251,99), (251,99), (251,99), (251,99), (250,96), (250,96), (250,95), (249,95), (249,96), (248,95), (248,95), (247,95), (244,100), (242,100), (242,101), (235,100), (231,102), (230,103), (230,103), (226,104), (225,104), (225,104), (225,105), (218,108), (217,108), (216,107), (216,107), (217,106,218,104), (217,100), (215,99), (215,98), (215,98), (214,98), (214,98), (213,97), (213,97), (213,97), (212,97), (212,96), (204,93), (202,94), (201,94), (200,94), (199,94), (199,94), (199,93), (197,94), (197,94), (196,93), (196,93), (196,93), (195,93), (195,93), (195,93), (194,93), (194,93), (193,92), (193,93), (190,90), (190,91), (190,91), (128,91), (127,91), (127,91), (127,90), (126,90), (126,90,126,90), (125,89), (125,89), (125,90), (124,90), (123,89), (123,88), (122,88), (120,88), (120,87), (120,87), (119,87), (118,87), (118,87), (117,87), (117,87), (117,86), (118,86), (118,85), (116,85), (117,85), (118,84), (118,84), (117,84), (116,84), (116,83), (115,83), (114,82), (114,82), (115,81), (114,81), (113,82), (112,81), (111,80), (111,79), (112,78), (111,77), (112,76), (108,75), (100,68), (99,68,99,68), (97,69), (96,69), (96,70), (92,67), (92,67), (92,67), (88,67), (88,66), (87,46), (99,48), (100,48), (99,47), (99,47), (98,46), (100,46), (101,46), (101,46), (109,45), (110,45), (112,45), (112,45), (107,46), (106,47), (104,47), (104,47), (106,48), (106,48), (106,47), (107,47), (108,47), (117,44), (117,44), (115,43), (117,44), (118,44), (119,45), (122,46), (122,46), (123,46), (122,46), (122,45,124,45), (124,45), (124,46), (124,46), (126,46), (127,46), (127,45), (147,48), (147,49), (144,49), (144,50), (161,51), (161,51), (160,51), (160,51), (162,53), (162,52), (162,52), (163,52), (163,51), (162,51), (161,50), (162,49), (165,49), (165,49), (165,49), (171,49), (171,50), (182,49), (184,50), (185,50), (185,50), (185,49), (182,49), (182,49), (187,49), (187,49), (187,49), (187,50), (187,51), (189,51,189,51), (189,50), (189,49), (189,49), (190,49), (192,48), (193,48), (193,48), (193,48), (193,47), (191,47), (191,47), (192,47), (192,47), (193,47), (194,47), (194,47), (194,46), (187,45), (186,45), (186,44), (188,44), (186,43), (186,43), (187,42), (187,42), (188,42), (189,42), (189,42), (189,42), (188,41), (188,41), (188,41), (189,41), (192,41), (194,41), (194,42), (194,42), (194,43), (197,44), (197,45,196,45), (195,45), (195,45), (197,46), (198,46), (200,46), (199,46), (199,47), (199,47), (200,47), (200,48), (200,49), (201,49), (201,48), (202,47), (203,47), (203,47), (205,48), (206,48), (206,49), (204,49), (204,49), (204,49), (207,51), (209,51), (209,50), (210,49), (211,48), (211,48), (213,48), (213,47), (211,46), (211,46), (212,45), (217,46), (218,47), (219,46), (220,47), (220,48), (219,48), (219,48,219,48), (218,48), (218,48), (217,48), (217,49), (220,50), (220,51), (220,51), (218,52), (217,52), (216,53), (213,51), (213,51), (212,52), (215,53), (212,53), (212,53), (211,52), (208,53), (208,53), (210,53), (210,54), (207,55), (206,55), (201,54), (199,54), (207,56), (206,57), (204,58), (203,58), (201,58), (201,58), (201,59), (201,59), (193,58), (199,60), (199,60), (199,60), (199,61), (196,61), (195,61,197,61), (196,62), (193,63), (193,64), (193,64), (192,64), (191,65), (190,67), (190,68), (190,68), (190,70), (191,70), (191,70), (191,70), (194,70), (194,70), (195,73), (195,74), (200,73), (205,75), (206,76), (218,78), (218,78), (218,80), (218,80), (218,81), (218,82), (218,82), (218,83), (219,83), (219,84), (219,84), (219,85), (220,85), (222,86), (222,86), (223,86), (224,87), (224,87), (224,86), (225,86,225,86), (226,87), (226,86), (226,85), (226,85), (226,84), (226,84), (226,83), (226,83), (226,82), (225,81), (226,81), (226,81), (225,80), (225,80), (224,80), (224,79), (229,77), (231,75), (231,74), (230,73), (227,70), (226,70), (226,70), (227,69), (228,68), (228,68), (229,68), (229,68), (229,67), (229,66), (229,66), (229,66), (229,66), (227,65), (229,64), (229,64), (228,63), (227,63), (227,62), (228,62,229,62), (237,62), (237,62), (241,64), (241,64), (246,65), (246,65), (247,65), (247,66), (246,66), (246,66), (247,69), (247,69), (246,69), (246,69), (245,70), (246,70), (248,70), (249,70), (249,70), (249,71), (249,71), (250,71), (252,71), (253,70), (253,70), (253,70), (254,71), (254,71), (254,70), (255,69), (256,69), (255,68), (255,68), (255,68), (256,68), (257,67), (257,67), (259,68), (260,69), (261,70,261,70), (261,70), (261,71), (261,71), (262,71), (262,72), (263,72), (263,72), (263,73), (263,73), (263,73), (264,74), (264,74), (264,74), (264,74), (264,74), (263,74), (262,74), (262,74), (263,75), (263,75), (264,76), (264,76), (266,77), (267,77), (267,77), (266,78), (267,78), (268,78), (273,79), (273,79), (267,81), (267,81), (267,82), (267,82), (273,80), (274,80), (274,81), (273,81), (274,81), (274,82,275,81), (277,82), (277,82), (277,82), (277,83), (276,83), (276,84), (277,84), (277,85), (274,86), (271,86), (268,88), (253,89), (252,89), (252,90), (251,90), (251,91), (248,92), (244,95), (243,97), (247,94), (256,91), (257,91), (258,92), (258,92), (258,92), (258,93), (256,94), (255,94), (254,93), (253,94), (254,94), (255,94), (255,95), (256,94), (256,94), (257,94), (257,94), (257,95), (257,95), (256,95,256,95), (255,96), (257,96), (257,96), (257,96), (257,97), (257,97), (257,97), (257,97), (257,97), (257,97), (257,98), (258,98), (258,98), (258,98), (259,98), (259,98), (258,98), (258,98), (259,98), (259,98), (260,98), (260,99), (260,99), (260,99), (261,99), (261,99), (261,99), (262,99), (261,99), (262,99), (262,99), (263,98), (263,99), (264,99), (264,99), (265,99), (264,99), (264,100), (265,100,265,100), (265,100), (265,100), (264,100), (264,100), (264,100), (264,100), (263,100), (263,100), (263,100), (263,100), (262,100), (262,101), (262,101), (261,101), (261,101), (261,101), (261,101), (260,101), (260,101), (260,101), (260,101), (260,101), (260,102), (259,102), (259,101), (259,101), (259,101), (259,101), (258,102), (258,101), (258,101), (258,102), (258,102), (258,102), (258,102,258,102), (258,102), (257,102), (257,103), (257,103), (257,103), (257,103), (257,103), (256,103), (256,103), (256,103), (256,103), (256,103), (256,103), (256,103), (256,103), (255,103), (255,104), (255,104), (255,104), (254,103), (254,103), (254,102), (254,102), (254,101), (254,101), (254,101), (254,102), (254,102), (255,101), (255,101), (255,101), (255,101), (258,100), (258,100), (258,100,258,100), (258,100), (258,100), (260,100), (260,100), (260,100), (260,99), (257,100), (257,99), (258,99), (258,99), (258,99), (258,98), (257,99), (257,99), (257,98), (257,98), (257,99), (257,99), (254,100), (254,100), (254,100), (253,100), (253,100), (252,100), (252,100), (251,100), (251,100), (251,100)]
	return render_to_response('map.html', {"data":json.dumps(data)})

