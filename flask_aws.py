# an object of WSGI application 
from flask import Flask, request
import os
import boto3
from werkzeug.utils import secure_filename
import configparser

app = Flask(__name__) # Flask constructor 
cf_port = os.getenv("PORT")


def connect_to_aws(region,key,secret):
    sts = boto3.client('sts',
                  region_name=region, 
                  aws_access_key_id=key, 
                  aws_secret_access_key=secret)
    try:
        sts.get_caller_identity()
        return 1
    except Exception as e:
        print("Credentials are NOT valid.")
        return 0


def connect_to_s3(region,key,secret):
    s3 = boto3.client("s3", 
                  region_name=region, 
                  aws_access_key_id=key, 
                  aws_secret_access_key=secret)
    return s3


def download_from_s3(s3_client,file_name):
    #return s3_client.download_file(Filename=file_name, Bucket='samplesubam', Key=file_name)
    return s3_client.generate_presigned_url('get_object',
                                     Params={'Bucket': 'samplesubam', 'Key': file_name},
                                     ExpiresIn=60) 
  

def uplod_to_s3(s3_client,file_name):
    s3_client.upload_file(Filename=file_name, Bucket='samplesubam', Key=file_name)



@app.route('/')	 
def hello2():
    return 'Helo Inside Intel'


@app.route('/get_file')	 
def hello():
    data = request.form.get("data")
    print(data)
    ES_Env = configparser.ConfigParser()
    ES_Env.read('db.cfg')
    key = ES_Env.get('aws', "key").strip('"')
    secret = ES_Env.get('aws', "secret").strip('"')
    region = ES_Env.get('aws', "region").strip('"')

    validation = connect_to_aws(region,key,secret)
    if validation:
        s3_client = connect_to_s3(region,key,secret)
        return download_from_s3(s3_client,data)
        

@app.route('/put_file', methods=['GET', 'POST'])	 
def put_file():
    if 'file' not in request.files:
        return 'no file'
    else:
        file = request.files['file']
        
        filename = secure_filename(file.filename)
        file.save(filename)
        ES_Env = configparser.ConfigParser()
        ES_Env.read('db.cfg')
        key = ES_Env.get('aws', "key").strip('"')
        secret = ES_Env.get('aws', "secret").strip('"')
        region = ES_Env.get('aws', "region").strip('"')
        s3_client = connect_to_s3(region,key,secret)
        uplod_to_s3(s3_client,filename)
        print(file)
        ES_Env = configparser.ConfigParser()
        print('hi')
        return str(file)


if __name__=='__main__':
    print(cf_port)
    if cf_port is None:
        app.run(host = '0.0.0.0', port = 5000)
    else:
        app.run( host='0.0.0.0', port=int(cf_port))