

### import WTForms for validation
import wtforms
from wtforms import TextField, PasswordField, HiddenField, FileField, RadioField, validators 
from tornadotools.forms import Form


from wtforms_tornado import Form as Form_


class LoginForm(Form):
	username = TextField('Username', [
		validators.Length(min=4, message="Too short")
		])

	email = TextField('Email', [
		validators.Length(min=4, message="Not a valid mail address"),
		validators.Email()
		])


class EasyForm(Form_):
	name 	= wtforms.TextField('name', validators=[wtforms.validators.DataRequired()], default=u'test')
	email 	= wtforms.TextField('email', validators=[wtforms.validators.Email(), wtforms.validators.DataRequired()])
	message = wtforms.TextAreaField('message', validators=[wtforms.validators.DataRequired()])
