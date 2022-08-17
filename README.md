# gym-forecast-capacity
Web app with that forecasts capacity for Virgin active gym's using Phrophet. https://mygym.institute

It uses 2 cronjobs for data:
1. Collects current capacity via Virgin Active's API
2. Creates forecasts for each gym using Prophet


# Installation
1. Clone this repo

`git clone https://github.com/dartpain/gym-forecast-capacity.git`

2. Install dependencies

`pip3 install -r requirements.txt`


# Running 
1. Create 2 cronjobs
Run this on you machine
`crontab -e`

and paste this  for collecting data

`*/5 * * * * python3 /home/alex/collect_data.py`

And this to create forecasts

`0 */12 * * * python3 /home/alex/forecast.py`

2. Launch flask

`python3 application.py`
