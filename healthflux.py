import pandas as pd
import re
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

db_url = "..."
db_token = "..."
db_org = "..."
db_bucket = "apple_health"

export_xml_path = "data/apple_health_export/export.xml"

type_selectors = [
    'HKQuantityTypeIdentifierHeartRate', 
    'HKQuantityTypeIdentifierOxygenSaturation', 
    'HKQuantityTypeIdentifierStepCount'
]

batch_size = 10000
time_delta = "-365 days"

def select_data(data_raw, type_selector):
    data_selected = data_raw[data_raw['type'] == type_selector ].dropna(how='all', axis='columns')
    data_selected['value'] = data_selected['value'].astype(float)
    data_selected['startDate'] = pd.to_datetime(data_selected['startDate'])

    now = pd.Timestamp.now(tz='UTC')
    data_selected = data_selected[data_selected['startDate'] > now + pd.Timedelta(time_delta)]
    return data_selected

def get_parameters(input_string):
    pattern = r"name:(?P<name>.*?), manufacturer:(?P<manufacturer>.*?), model:(?P<model>.*?), hardware:(?P<hardware>.*?), software:(?P<software>.*?)>"
    match = re.search(pattern, input_string)
    
    if match:
        parameters = match.groupdict()
        return parameters
    else:
        return None

def export_data_to_influxdb(data, batch_size):
    points = []
    for _, row in data.iterrows():
        points.append({
                "measurement": type_selector, 
                "tags": get_parameters(row['device']),
                "fields": {
                    "value": row['value']
                },
                "time": row['startDate']
            })

        if batch_size and len(points) >= batch_size:
            write_api.write(bucket=db_bucket, org=db_org, record=points, time_precision='s')
            points = []
            print(".", end="", flush=True)
    if points:
        write_api.write(bucket=db_bucket, org=db_org, record=points, time_precision='s')
        print(".", end="", flush=True)

client = InfluxDBClient(url=db_url, token=db_token, org=db_org)
write_api = client.write_api(write_options=SYNCHRONOUS)

print("Reading XML ...", end="", flush=True)
data_raw = pd.read_xml(export_xml_path)
print(" done (%s)" % (len(data_raw)))

for type_selector in type_selectors:
    print("Reading \"%s\" ..." % (type_selector), end="", flush=True)
    data = select_data(data_raw, type_selector)
    print(" done (%s)" % (len(data)))

    print("Exporting \"%s\" " % (type_selector), end="", flush=True)
    export_data_to_influxdb(data, batch_size)
    print(" done")