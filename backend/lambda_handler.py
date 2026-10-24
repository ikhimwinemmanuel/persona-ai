from mangum import Mangum # to help lambda function communicate with FastAPI app
from server import app
import boto3


handler = Mangum(app)
s3 = boto3.client("s3")
