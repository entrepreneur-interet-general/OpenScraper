
from 	functools import wraps
from    config.settings_corefields import * # USER_CORE_FIELDS, etc...


########################
### DEFAULT / UTILS --- SOME STILL NOT FULLY TESTED

def create_generic_custom_fields():
	"""create default custom fields in DB """
	
	default_fields_list = []

	for default_field in DATAMODEL_DEFAULT_CUSTOM_FIELDS :
		new_field = {
			"field_name" 	: default_field["field_name"],
			"field_type" 	: default_field["field_type"],
			"added_by" 		: "admin",
			"field_class" 	: "custom",
		}
		default_fields_list.append(new_field)
	
	self.application.coll_model.insert_many(default_fields_list)

def reset_fields_to_default():
	"""reset datamodel to default : core fields and default custom fields"""

	self.application.coll_model.remove({ "field_class" : "custom" })
	create_generic_custom_fields()

### DECORATORS / UTILS 
# cf : https://www.saltycrane.com/blog/2010/03/simple-python-decorator-examples/
# cf : https://www.codementor.io/sheena/advanced-use-python-decorators-class-function-du107nxsv
# cf : for requests : https://mrcoles.com/blog/3-decorator-examples-and-awesome-python/
# cf : https://stackoverflow.com/questions/6394511/python-functools-wraps-equivalent-for-classes

def print_separate(debug) :
	
	def print_sep(f):
		"""big up and self-high-five ! it's the first real decorator I wrote my self, wuuuh !!! """
		
		@wraps(f)
		def wrapped(*args, **kwargs):
			if debug == True :
				print "\n{}".format("---"*10)
			r = f(*args, **kwargs)
			return r
		return wrapped
	
	return print_sep



#### DECORATORS NOT WORKING FOR NOW

def time_this(original_function):
	print "decorating"
	def new_function(*args,**kwargs):
		print "starting decoration"
		x = original_function(*args,**kwargs)
		return x
	return new_function  

def time_all_class_methods(Cls):
	class NewCls(object):
		def __init__(self, *args, **kwargs):
			print args
			print kwargs
			self.oInstance = Cls(*args,**kwargs)
		def __getattribute__(self,s):
			"""
			this is called whenever any attribute of a NewCls object is accessed. This function first tries to 
			get the attribute off NewCls. If it fails then it tries to fetch the attribute from self.oInstance (an
			instance of the decorated class). If it manages to fetch the attribute from self.oInstance, and 
			the attribute is an instance method then `time_this` is applied.
			"""
			try:    
				x = super(NewCls,self).__getattribute__(s)
			except AttributeError:
				pass
			else:
				return x
			x = self.oInstance.__getattribute__(s)
			if type(x) == type(self.__init__): 	# it is an instance method
				return time_this(x)				# this is equivalent of just decorating the method with time_this
			else:
				return x
	return NewCls


