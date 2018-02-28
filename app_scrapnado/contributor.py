from config.settings_corefields import *

class ContributorBaseClass : 

	def __init__(self, contrib_fields_dict ) : 

		print "\n*** initiating ContributorBaseClass / ..."

		self.contrib_fields_dict = contrib_fields_dict

		### get back basic model 
		self.contributor_base_model = CONTRIBUTOR_CORE_FIELDS

		### fill model fields
		self.fill_model_fields(self)


	def fill_model_fields (self) :
		
		print "*** ContributorBaseClass / fill_model_fields ..."
		
		### loop in self.contrib_fields_dict 
		for field, datadict in self.contrib_fields_dict.iteritems():
			
			data_content = datadict["data"]
			data_type 	 = datadict["type"]

			self.contrib_fields_dict[ data_type ] = data_content
