<div align="center">

# HealthFlux

*Import Apple Health data into InfluxDB*

<img src="" width="75%">

</div>

## Installing

#### Clone repository and install requirements

    git clone https://github.com/FelixKohlhas/HealthFlux
    cd HealthFlux
    pip3 install -r requirements.txt


## Usage

#### Configuring

Configure

    db_url = "..."
    db_token = "..."
    db_org = "..."
    db_bucket = "apple_health"

in `healthflux.py`


#### Running

Unpack export.zip to `data/` such as this

    .
    └── data
        └── apple_health_export
            └── export.xml

Run using

    python3 healthflux.py