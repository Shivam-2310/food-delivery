"""Restaurant owner forms."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    BooleanField,
    FloatField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
    widgets,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class MultiCheckboxField(SelectMultipleField):
    """Custom field for multiple checkboxes."""
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class RestaurantForm(FlaskForm):
    """Form for creating or updating restaurant."""
    name = StringField('Restaurant Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=500)])
    location = StringField('Location', validators=[DataRequired(), Length(min=5, max=200)])
    # Render cuisines as checkboxes for better UX.
    cuisines = MultiCheckboxField('Cuisines', choices=[], validators=[Optional()])
    image = FileField(
        'Restaurant Image',
        validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'IMAGES ONLY (JPG, PNG)')],
    )
    submit = SubmitField('SAVE RESTAURANT')

class MenuItemForm(FlaskForm):
    """Form for creating or updating menu item."""
    name = StringField('Item Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=300)])
    price = FloatField(
        'Price',
        validators=[DataRequired(), NumberRange(min=0.01, message='PRICE MUST BE GREATER THAN 0')],
    )
    category = SelectField(
        'Category',
        choices=[
            ('appetizer', 'Appetizer'),
            ('main_course', 'Main Course'),
            ('dessert', 'Dessert'),
            ('beverage', 'Beverage'),
            ('side', 'Side Dish'),
        ],
        validators=[DataRequired()],
    )
    is_vegetarian = BooleanField('Non-Vegetarian')
    is_vegan = BooleanField('Vegan')
    is_guilt_free = BooleanField('Guilt Free')
    is_special = BooleanField('Mark as Today\'s Special')
    is_deal_of_day = BooleanField('Mark as Deal of the Day')
    image = FileField(
        'Item Image',
        validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'IMAGES ONLY (JPG, PNG)')],
    )
    submit = SubmitField('SAVE MENU ITEM')

class OrderUpdateForm(FlaskForm):
    """Form for updating order status."""
    status = SelectField(
        'Status',
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('preparing', 'Preparing'),
            ('ready', 'Ready for Pickup'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField('UPDATE STATUS')

class FeedbackResponseForm(FlaskForm):
    """Form for restaurant owner to respond to feedback."""
    response = TextAreaField('Response', validators=[DataRequired(), Length(min=5, max=500)])
    submit = SubmitField('SUBMIT RESPONSE')
