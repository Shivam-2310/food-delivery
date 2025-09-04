"""
CUSTOMER FORMS
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField, SelectMultipleField, BooleanField, widgets
from wtforms.validators import DataRequired, Length, Email, NumberRange, Optional

class ProfileUpdateForm(FlaskForm):
    """
    FORM FOR UPDATING CUSTOMER PROFILE
    """
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=15)])
    address = TextAreaField('Address', validators=[Optional(), Length(max=200)])
    submit = SubmitField('UPDATE PROFILE')

class MultiCheckboxField(SelectMultipleField):
    """
    CUSTOM FIELD FOR MULTIPLE CHECKBOXES
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class PreferencesForm(FlaskForm):
    """
    FORM FOR UPDATING CUSTOMER PREFERENCES
    """
    favorite_cuisines = MultiCheckboxField('Favorite Cuisines', choices=[])
    dietary_restrictions = MultiCheckboxField('Dietary Restrictions', choices=[
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('guilt_free', 'Guilt Free')
    ])
    submit = SubmitField('SAVE PREFERENCES')


class OrderFeedbackForm(FlaskForm):
    """
    FORM FOR SUBMITTING ORDER FEEDBACK AFTER COMPLETION
    """
    rating = SelectField('Rating', 
                        choices=[(1, '★'), (2, '★★'), (3, '★★★'), (4, '★★★★'), (5, '★★★★★')],
                        validators=[DataRequired()],
                        coerce=int)
    message = TextAreaField('Your Feedback', validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField('SUBMIT FEEDBACK')

class SearchForm(FlaskForm):
    """
    FORM FOR SEARCHING RESTAURANTS AND MENU ITEMS
    """
    query = StringField('Search', validators=[Optional(), Length(max=100)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    cuisines = MultiCheckboxField('Cuisines', choices=[])
    price_min = IntegerField('Min Price', validators=[Optional(), NumberRange(min=0)])
    price_max = IntegerField('Max Price', validators=[Optional(), NumberRange(min=0)])
    apply_dietary_preferences = BooleanField('Apply My Dietary Preferences')
    submit = SubmitField('SEARCH')
