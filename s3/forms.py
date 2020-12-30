from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired

class CreateBucketForm(FlaskForm):
    new_bucket_name = StringField(
        'Bucket Name',
        validators = [
            DataRequired()
        ]
    )

    create = SubmitField('Create')

class DeleteBucketForm(FlaskForm):
    bucket_name = HiddenField()

    delete = SubmitField('Delete')