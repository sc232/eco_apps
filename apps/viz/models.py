from django.db import models
from django.db.models import Avg, Max, Min, Count, Sum

class Country(models.Model):
	name = models.CharField(max_length=200)
	name_numeric = models.PositiveSmallIntegerField(max_length=4, null=True)
	name_2char = models.CharField(max_length=2, null=True)
	name_2char_wb = models.CharField(max_length=2, null=True)
	name_3char = models.CharField(max_length=3, null=True)
	name_3char_wb = models.CharField(max_length=3, null=True)
	continent = models.CharField(max_length=50, null=True)
	region_id = models.CharField(max_length=5, null=True)
	region = models.CharField(max_length=50, null=True)
	income_level = models.CharField(max_length=50, null=True)
	lending_type = models.CharField(max_length=50, null=True)
	capital_city = models.CharField(max_length=100, null=True)
	longitude = models.FloatField(null=True)
	latitude = models.FloatField(null=True)
	flag = models.FilePathField(null=True)
	
	def __unicode__(self):
		return self.name

###############################################################################
###############################################################################
###############################################################################

class Sitc4_leamer(models.Model):
	name = models.CharField(max_length=30)
	color = models.CharField(max_length=7)
	img = models.FilePathField(null=True)

	def __unicode__(self):
		return self.name + " color: " + self.color

###############################################################################
###############################################################################

class Sitc4(models.Model):
	name = models.CharField(max_length=255)
	code = models.CharField(max_length=4)
	leamer = models.ForeignKey(Sitc4_leamer, null=True)
	ps_x = models.FloatField(null=True)
	ps_y = models.FloatField(null=True)
	ps_size = models.FloatField(null=True)

	def __unicode__(self):
		return self.code + self.name

###########################################
###########################################

class Sitc4_feenstra_trade(models.Model):
	year = models.PositiveSmallIntegerField(max_length=4)
	icode = models.FloatField(null=True)
	importer = models.ForeignKey(Country, related_name="trade_ImpCountries")
	ecode = models.FloatField(null=True)
	exporter = models.ForeignKey(Country, related_name="trade_ExpCountries")
	product = models.ForeignKey(Sitc4, related_name="trade_products")
	import_value = models.FloatField(null=True)


###############################################################################
###############################################################################

class Sitc4_feenstra_cpy(models.Model):
	country = models.ForeignKey(Country, related_name="feenstra_cpys")
	product = models.ForeignKey(Sitc4, related_name="feenstra_product_cpys")
	year = models.PositiveSmallIntegerField(max_length=4)
	export_value = models.FloatField(null=True)
	export_share = models.FloatField(null=True)
	market_share = models.FloatField(null=True)
	import_value = models.FloatField(null=True)
	rca = models.FloatField(null=True)
	density_1 = models.FloatField(null=True)
	density_09 = models.FloatField(null=True)
	density_08 = models.FloatField(null=True)
	density_07 = models.FloatField(null=True)
	density_06 = models.FloatField(null=True)
	density_05 = models.FloatField(null=True)

###############################################################################
###############################################################################
	
class Sitc4_comtrade_cpy(models.Model):
	country = models.ForeignKey(Country, related_name="comtrade_cpys")
	product = models.ForeignKey(Sitc4, related_name="comtrade_product_cpys")
	year = models.PositiveSmallIntegerField(max_length=4)
	export_value = models.FloatField(null=True)
	export_share = models.FloatField(null=True)
	market_share = models.FloatField(null=True)
	import_value = models.FloatField(null=True)
	rca = models.FloatField(null=True)
	density_1 = models.FloatField(null=True)
	density_09 = models.FloatField(null=True)
	density_08 = models.FloatField(null=True)
	density_07 = models.FloatField(null=True)
	density_06 = models.FloatField(null=True)
	density_05 = models.FloatField(null=True)

###############################################################################
###############################################################################

class Sitc4_cy(models.Model):
	country = models.ForeignKey(Country)
	year = models.PositiveSmallIntegerField(max_length=4)
	total_export = models.FloatField(null=True)
	total_import = models.FloatField(null=True)
	hdi = models.FloatField(null=True)
	kc_0 = models.FloatField(null=True)
	kc_1 = models.FloatField(null=True)
	kc_2 = models.FloatField(null=True)
	kc_3 = models.FloatField(null=True)
	kc_4 = models.FloatField(null=True)
	kc_5 = models.FloatField(null=True)
	kc_6 = models.FloatField(null=True)
	kc_7 = models.FloatField(null=True)
	kc_8 = models.FloatField(null=True)
	kc_9 = models.FloatField(null=True)
	kc_10 = models.FloatField(null=True)
	kc_11 = models.FloatField(null=True)
	kc_12 = models.FloatField(null=True)
	kc_13 = models.FloatField(null=True)
	kc_14 = models.FloatField(null=True)
	kc_15 = models.FloatField(null=True)
	kc_16 = models.FloatField(null=True)
	kc_17 = models.FloatField(null=True)
	kc_18 = models.FloatField(null=True)
	kc_19 = models.FloatField(null=True)
	kcn_0 = models.FloatField(null=True)
	kcn_1 = models.FloatField(null=True)
	kcn_2 = models.FloatField(null=True)
	kcn_3 = models.FloatField(null=True)
	kcn_4 = models.FloatField(null=True)
	kcn_5 = models.FloatField(null=True)
	kcn_6 = models.FloatField(null=True)
	kcn_7 = models.FloatField(null=True)
	kcn_8 = models.FloatField(null=True)
	kcn_9 = models.FloatField(null=True)
	kcn_10 = models.FloatField(null=True)
	kcn_11 = models.FloatField(null=True)
	kcn_12 = models.FloatField(null=True)
	kcn_13 = models.FloatField(null=True)
	kcn_14 = models.FloatField(null=True)
	kcn_15 = models.FloatField(null=True)
	kcn_16 = models.FloatField(null=True)
	kcn_17 = models.FloatField(null=True)
	kcn_18 = models.FloatField(null=True)
	kcn_19 = models.FloatField(null=True)

	def __unicode__(self):
		return "%s - %d" % (self.country.name, self.year)
