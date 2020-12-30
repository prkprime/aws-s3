from flask import Flask, render_template, url_for, flash, redirect, request
from decouple import config
from boto3.session import Session
from tabulate import tabulate
from .forms import CreateBucketForm, DeleteBucketForm
import botocore

app = Flask(__name__)
app.config['SECRET_KEY'] = config('SECRET_KEY')

def get_client():
    return Session().client(
        's3',
        aws_access_key_id=config('S3_ACCESS_KEY'),
        aws_secret_access_key=config('S3_SECRET_ACCESS_KEY'),
    )

def get_resource_client():
    return Session().resource(
        's3',
        aws_access_key_id=config('S3_ACCESS_KEY'),
        aws_secret_access_key=config('S3_SECRET_ACCESS_KEY'),
    )

response = get_client().list_buckets()
USERNAME = response.get('Owner').get('DisplayName')
REGION = config('REGION')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('create'):
            try:
                new_bucket_name = request.form.get('new_bucket_name')
                client = get_resource_client()
                client.create_bucket(Bucket=new_bucket_name, CreateBucketConfiguration={'LocationConstraint': REGION})
                flash(f'Bucket {new_bucket_name} created successfully!', 'success')
            except client.meta.client.exceptions.BucketAlreadyExists as e:
                flash('Bucket {} already exists!'.format(e.response['Error']['BucketName']), 'danger')
            except client.meta.client.exceptions.BucketAlreadyOwnedByYou as e:
                flash('Bucket {} already owned by you!'.format(e.response['Error']['BucketName']), 'danger')
            except Exception as e:
                print(e)
                flash('Something went wrong!', 'danger')
        if request.form.get('delete'):
            return redirect(url_for('delete_bucket', bucket_name=request.form.get('bucket_name')))
    form = CreateBucketForm()
    response = get_client().list_buckets()
    bucket_forms = []
    if buckets := response.get('Buckets'):
        for bucket in buckets:
            bucket_forms.append((bucket.get('Name'), DeleteBucketForm(bucket_name=bucket.get('Name'))))
    return render_template('index.html', username=USERNAME, title='S3 Buckets', buckets=bucket_forms, form=form)

@app.route('/delete_bucket/<string:bucket_name>')
def delete_bucket(bucket_name: str):
    try:
        get_client().delete_bucket(Bucket=bucket_name)
        flash(f'Bucket {bucket_name} has been deleted successfully!', 'success')
    except Exception as e:
        print(e)
        flash('Something went wrong!', 'danger')
    return redirect(url_for('index'))