import boto3
import os
import zipfile

from io import BytesIO, StringIO
from socket import gethostname
from urllib.request import urlretrieve

# Configure based on environment variables, or use defaults.
AWS_REGION = os.environ('ACTA_AWS_REGION', 'us-west-1')
RAW_XML_S3_BUCKET = os.environ.get('ACTA_RAW_XML_S3_BUCKET', 'acta-raw-xml')
TERMS_TO_PROCESS_QUEUE_URL = os.environ.get('ACTA_TERMS_TO_PROCESS_QUEUE_URL', 'https://sqs.us-west-1.amazonaws.com/274059113391/acta-terms-to-process')
XML_TO_PROCESS_QUEUE_URL = os.environ.get('ACTA_XML_TO_PROCESS_QUEUE_URL', 'https://sqs.us-west-1.amazonaws.com/274059113391/acta-xml-to-process')

# Link to download all ClinicalTrials.gov data
ALL_CT_GOV_TRIALS_URL = 'https://clinicaltrials.gov/AllPublicXML.zip'

# Initialize S3 resources.
s3 = boto3.client('s3', region_name=AWS_REGION)
sqs = boto3.client('sqs', region_name=AWS_REGION)

with urlopen(ALL_CT_GOV_TRIALS_URL) as resp:
  archive = zipfile.ZipFile(BytesIO(resp.read()))

  for xml_file_name in [name for name in archive.namelist() if name.endswith('.xml')]:
    
    with archive.open(xml_file_name, 'r') as xml_file:

      s3.put_object(Body=xml_file.read(), Bucket=RAW_XML_S3_BUCKET, Key=xml_file_name)