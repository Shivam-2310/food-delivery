"""Customer forms."""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
    widgets,
)
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional

class ProfileUpdateForm(FlaskForm):
    """Form for updating customer profile."""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=15)])
    address = TextAreaField('Address', validators=[Optional(), Length(max=200)])
    submit = SubmitField('UPDATE PROFILE')

class MultiCheckboxField(SelectMultipleField):
    """Custom field for multiple checkboxes."""
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class PreferencesForm(FlaskForm):
    """Form for updating customer preferences."""
    favorite_cuisines = MultiCheckboxField('Favorite Cuisines', choices=[])
    dietary_restrictions = MultiCheckboxField('Dietary Restrictions', choices=[
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('guilt_free', 'Guilt Free')
    ])
    submit = SubmitField('SAVE PREFERENCES')


class OrderFeedbackForm(FlaskForm):
    """Form for submitting order feedback after completion."""
    rating = SelectField(
        'Rating',
        choices=[(1, '★'), (2, '★★'), (3, '★★★'), (4, '★★★★'), (5, '★★★★★')],
        validators=[DataRequired()],
        coerce=int,
    )
    message = TextAreaField('Your Feedback', validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField('SUBMIT FEEDBACK')

class DishRatingForm(FlaskForm):
    """Form for rating individual dishes."""
    def __init__(self, order_items=None, *args, **kwargs):
        super(DishRatingForm, self).__init__(*args, **kwargs)
        if order_items:
            for item in order_items:
                field_name = f'dish_rating_{item.menu_item_id}'
                setattr(
                    self,
                    field_name,
                    SelectField(
                        f'Rate {item.menu_item.name}',
                        choices=[
                            (1, '★'),
                            (2, '★★'),
                            (3, '★★★'),
                            (4, '★★★★'),
                            (5, '★★★★★'),
                        ],
                        validators=[DataRequired()],
                        coerce=int,
                        default=5,
                    ),
                )
    
    submit = SubmitField('SUBMIT DISH RATINGS')

class SearchForm(FlaskForm):
    """Form for searching restaurants and menu items."""
    query = StringField('Search', validators=[Optional(), Length(max=100)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    cuisines = MultiCheckboxField('Cuisines', choices=[])
    price_min = IntegerField('Min Price', validators=[Optional(), NumberRange(min=0)])
    price_max = IntegerField('Max Price', validators=[Optional(), NumberRange(min=0)])
    apply_dietary_preferences = BooleanField('Apply My Dietary Preferences')
    submit = SubmitField('SEARCH')
