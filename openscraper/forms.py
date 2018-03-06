# -*- encoding: utf-8 -*-


### import WTForms for validation
import 	wtforms
### import field classes
# from 	wtforms import TextField, TextAreaField, PasswordField, HiddenField, FileField, RadioField, validators 
from wtforms import TextField, StringField, BooleanField, TextAreaField, \
					IntegerField, PasswordField, SubmitField, HiddenField, FileField, widgets #, Form
from wtforms.fields.html5 import URLField, EmailField
from wtforms.fields.core import SelectField, SelectMultipleField, RadioField, DateTimeField, DateField
from wtforms import validators
from wtforms.validators import DataRequired, Length, EqualTo, URL, Email, Optional, NumberRange

# from 	tornadotools.forms import Form
from 	wtforms_tornado import Form # as Form_




class LoginForm(Form):
	name = TextField('Username', [
		Length(min=4, message="Too short")
		])

	email = TextField('Email', validators = [
		Length(min=4, message="Not a valid mail address"),
		Email()
		])

class SampleForm(Form):
	name = TextField(
			'Username', 
			validators = [ Length(min=4, message="Too short")],
			render_kw  = { "class" : "input" }
	)

	email = PasswordField(
		'Email', 
		validators = [ Length(min=4, message="Not a valid mail address"), Email()], 
		render_kw  = { "class" : "input" }
	)

class EasyForm(Form):
	name 	= TextField('name', validators=[wtforms.validators.DataRequired()], default=u'test')
	email 	= TextField('email', validators=[wtforms.validators.Email(), wtforms.validators.DataRequired()])
	message = TextAreaField('message', validators=[wtforms.validators.DataRequired()])




"""
### SNIPPETS FROM SOLIDATA - based on Flask but still...



class LoginForm(FlaskForm):
	userEmail       = EmailField    ( 'user email'   , validators = [ DataRequired(), Length(min=7, max=50) ], render_kw={'class': HTMLclass_form_control, 'placeholder':u'votre email'  }  )
	# userPseudo   = StringField   ( 'user pseudo'  , validators = [ DataRequired() ], render_kw={'class': HTMLclass_form_control, 'placeholder':u"votre pseudo"  }  )
	userPassword = PasswordField ( 'user password', validators = [ DataRequired() ], render_kw={'class': HTMLclass_form_control, 'placeholder':u"votre mot de passe"  }  )
	#remember_me  = BooleanField  ( 'remember_me', default=False )


class UserRegisterForm(FlaskForm):
	# userPseudo      = StringField   ( 'user pseudo'  , validators = [ DataRequired(), Length(min=3, max=50) ], render_kw={'class': HTMLclass_form_control, 'placeholder':u"votre pseudo"  }  )
	userName        = StringField   ( 'user name'    , validators = [ DataRequired(), Length(min=3, max=50) ], render_kw={'class': HTMLclass_form_control, 'placeholder':u'votre prénom'  }  )
	userSurname     = StringField   ( 'user surname' , validators = [ DataRequired(), Length(min=3, max=50) ], render_kw={'class': HTMLclass_form_control, 'placeholder':u'votre nom'  }  )
	userSiret       = IntegerField  ( 'user siret'   ,                                                         render_kw={'class': HTMLclass_form_control, 'placeholder':u'votre numéro de SIRET'  }  )

	userEmail       = EmailField    ( 'user email'   , validators = [ DataRequired(), Length(min=7, max=50) ], render_kw={'class': HTMLclass_form_control, 'placeholder':u'votre email'  }  )
	userPassword    = PasswordField ( 'user password',
		[
		DataRequired(),
		EqualTo('confirmPassword', message=u'les deux mots de passe doivent être identiques'),
		Length(min=4, max=100)
		],
		render_kw={'class': HTMLclass_form_control, 'placeholder': u'tapez votre password'}
	)
	confirmPassword = PasswordField ('repeat Password', render_kw={'class': HTMLclass_form_control, 'placeholder':u'répéter votre mot de passe' } )
	#remember_me     = BooleanField  ( 'remember_me', default=False )

	userProfile     = SelectField   ( 'select profile', choices = choices_subscriptions , default="priv_social",
														render_kw = {   'class': HTMLclass_select,
																		'data-width' : "100%"
														 }
									)


class PwdForgotForm(FlaskForm):
	# userPseudo   = StringField   ( 'pwdforgot pseudo'  , validators = [ DataRequired() ],                        render_kw={'class': HTMLclass_form_control, 'placeholder':u"votre pseudo"  }  )
	userName     = StringField   ( 'user name'         , validators = [ DataRequired(), Length(min=3, max=50) ], render_kw={'class': HTMLclass_form_control, 'placeholder':u'votre prénom'  }  )
	userEmail    = EmailField    ( 'pwdforgot email'   , validators = [ DataRequired(), Length(min=7, max=50) ], render_kw={'class': HTMLclass_form_control, 'placeholder':u'votre email'  }  )


class NewPwdForm(FlaskForm):
	userPassword    = PasswordField ( 'user password',
		[
		DataRequired(),
		EqualTo('confirmPassword', message=u'les deux mots de passe doivent être identiques'),
		Length(min=4, max=100)
		],
		render_kw={'class': HTMLclass_form_control, 'placeholder': u'tapez votre password'}
	)
	confirmPassword = PasswordField ('repeat Password', render_kw={'class': HTMLclass_form_control, 'placeholder':u'répéter votre mot de passe' } )


class UploadFilesForm(FlaskForm):

    data_files      = FileField     ( 'data files'      ,   validators = [ FileAllowed ( ALLOWED_DATAFILES, 'data files only' ) ] ,
                                                            render_kw  = {'multiple': True, 'class': HTMLclass_form_control} )
    data_filenames  = HiddenField   ( 'data_filenames' )
    data_types      = SelectField   ( 'select data type',   choices = choices_data_type ,
                                                            render_kw = {   'class': HTMLclass_select,
                                                                            "data-width" : "100%"
                                                                        } )


class UploadOneFileForm(FlaskForm):

    data_file      = FileField     ( 'data file'       , validators = [ FileAllowed ( ALLOWED_DATAFILES, 'data files only' ) ] ,
                                                         render_kw  = { 'class': HTMLclass_form_control} )
    data_filename  = HiddenField   ( 'data_filename' )
    data_type      = SelectField   ( 'select data type', choices = choices_data_type , render_kw = {'class': HTMLclass_form_control } )


class UploadOneImageForm(FlaskForm):

    image_file     = FileField     ( 'image file'      , validators = [ FileAllowed ( ALLOWED_IMAGES, 'Image only' ) ]  )
    image_filename = HiddenField   ( 'image_filename' )


"""