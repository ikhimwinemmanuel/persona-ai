from mangum import Mangum
from server import app
import boto3


handler = Mangum(app)
s3 = boto3.client("s3")
