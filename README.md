# Automated Clinical Trials Analysis
[![Build Status](https://travis-ci.com/chtka/cltr.svg?branch=master)](https://travis-ci.com/chtka/cltr) ![Build Status](https://s3-us-west-1.amazonaws.com/codefactory-us-west-1-prod-default-build-badges/passing.svg)

**cltr** is a Python module for building a primitive data lake architecture, 
using clinical trials registries, such as [ClinicalTrials.gov](https://clinicaltrials.gov/), as the data
sources.

The basic workflow of **cltr** is as follows:
1. Download raw clinical trials data from each of the clinical trials registry websites using the _searchers_ module.
2. Upload the raw data to a specified S3 bucket for persistence. 
3. Process the raw data using the _processors_ module, and upload the resultant data to a separate S3 bucket of persistence.
4. (Optional) Augment the processed data with additional metadata, if desired, and upload the resultant data to yet another S3 bucket for persistence.
5. Load the processed data into a database of choice, such as Elasticsearch, for querying and analysis.

Currently, searching capabilities are supported for the following websites: [ClinicalTrials.gov](https://clinicaltrials.gov/), the [Australian New Zealand Clinical Trials Registry](http://www.anzctr.org.au/), and the [ISRCTN Registry](http://www.isrctn.com/).

## Usage
Create a _config.json_ configuration file in the _config_ subdirectory of the root directory. An example _config.json_ file is as follows:

```javascript
{
    "bucket_names": {
        "raw_data_bucket_name": "Ct-analysis-data-raw",
        "processed_data_bucket_name": "ct-analysis-data-postprocessing"
    },
    "search_terms_file_path": "examples/search_terms_short.txt",
    "searchers": ["clinical-trials-gov"]
}
```

Then, navigate to the root directory of the project and run the desired script. For example:
```
python scripts/search_trials.py
```

The scripts upload to S3 buckets automatically, so make sure to download the AWS CLI and configure credentials before attempting to run the scripts;
if you are running these scripts from an EC2 instance, assigning a role that allows full access to S3 will also suffice.

## Configuration
The _config.json_ file has the following format:
```javascript
{
    "bucket_names": {
        "raw_data_bucket_name": "",
        "processed_data_bucket_name": ""
    },
    "search_terms_file_path": "",
    "searchers": [""]
}
```
Each parameter of the _config.json_ object is described below:
* ```bucket_names```:
  *  ```raw_data_bucket_name```: The S3 bucket to which unmodified data will be upload from each of the various clinical trials registries.
  *  ```processed_data_bucket_name```: The S3 bucket to which processed and parsed data will be uploaded.
* ```search_terms_file_path```: Can be either an absolute path or a relative path, relative to the root directory of the project.
* ```searchers```: A list of any combination of the following values, depending on which sites you wish to search: ```clinical-trials-gov```, ```anzctr```, ```isrctn```
