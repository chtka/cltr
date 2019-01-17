import boto3
import os
import zipfile

from io import BytesIO, StringIO
from socket import gethostname
from urllib.request import urlopen

# Configure based on environment variables, or use defaults.
AWS_REGION = os.environ.get('ACTA_AWS_REGION', 'us-west-1')
RAW_XML_S3_BUCKET = os.environ.get('ACTA_RAW_XML_S3_BUCKET', 'acta-raw-xml')

# Link to download all ClinicalTrials.gov data
ALL_CT_GOV_TRIALS_URL = 'https://clinicaltrials.gov/AllPublicXML.zip'

# Initialize S3 resources.
s3 = boto3.client('s3', region_name=AWS_REGION)
print("Downloading zip archive...")
with urlopen(ALL_CT_GOV_TRIALS_URL) as resp:
  archive = zipfile.ZipFile(BytesIO(resp.read()))

  for xml_file_name in [name for name in archive.namelist() if name.endswith('.xml')]:
    
    with archive.open(xml_file_name, 'r') as xml_file:
      print("Uploading %s.xml" % xml_file_name)
      s3.put_object(Body=xml_file.read(), Bucket=RAW_XML_S3_BUCKET, Key=xml_file_name)

