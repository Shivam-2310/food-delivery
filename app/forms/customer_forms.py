"""
CUSTOMER FORMS
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField, SelectMultipleField, widgets
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
        ('gluten_free', 'Gluten Free'),
        ('nut_free', 'Nut Free'),
        ('dairy_free', 'Dairy Free'),
        ('low_carb', 'Low Carb')
    ])
    submit = SubmitField('SAVE PREFERENCES')

class ReviewForm(FlaskForm):
    """
    FORM FOR SUBMITTING REVIEWS
    """
    rating = SelectField('Rating', 
                         choices=[(1, '★'), (2, '★★'), (3, '★★★'), (4, '★★★★'), (5, '★★★★★')],
                         validators=[DataRequired()],
                         coerce=int)
    comment = TextAreaField('Your Review', validators=[Optional(), Length(max=500)])
    submit = SubmitField('SUBMIT REVIEW')

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
    vegetarian_only = SelectField('Dietary', choices=[
        ('', 'All Foods'),
        ('vegetarian', 'Vegetarian Only')
    ], validators=[Optional()])
    submit = SubmitField('SEARCH')
