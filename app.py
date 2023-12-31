from flask import Flask, render_template
import requests
import json
from urllib.parse import quote

app = Flask(__name__)


url_link = "https://www.iihs.org/api/driver-death-rates/get-view-model"
response = requests.post(url_link)
data = response.json()
info = data["Info"]

car_data = []

for i in info:
    vehicle = i['Vehicle'].replace(' ', '-')  # Replace spaces with hyphens (-)
    model_year_span = quote(i['ModelYearSpan'])  # Encode the model year span

    car = {
        'year': int(model_year_span.split('-')[0]),
        'make': vehicle.split('-')[0],
        'model': '-'.join(vehicle.split('-')[1:]),
        'overall_death_rate': float(i['OverallDeathRate']),
        'multi_vehicle_crash_death_rate': i['MultiVehicleDeathRate'],
        'single_vehicle_crash_death_rate': i['SingleVehicleDeathRate'],
        'rollover_death_rate': i['RolloverDeathRate']
    }
    car_data.append(car)



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/car/<int:year>/<make>/<model>/')
def car_details(year, make, model):
    
    # Convert the search terms to lowercase
    make = make.lower()
    model = model.lower()
    
    # Find the car data based on year, make, and model
    car = next((c for c in car_data if c['year'] == year and c['make'].lower() == make and c['model'].lower() == model), None)
    if car is None:
        return 'Car not found. (Kindly double check spelling or Add "-" if there are spaces)'
    
      # Determine the color-coding for each death rate category
    def get_color(death_rate):
        if death_rate == None:
            pass
        elif death_rate < 50:
            return 'bg-success'
        elif death_rate == 50:
            return 'bg-warning'
        elif death_rate > 50:
            return 'bg-danger'

        
    overall_color = get_color(car['overall_death_rate'])
    multi_vehicle_color = get_color(car['multi_vehicle_crash_death_rate'])
    single_vehicle_color = get_color(car['single_vehicle_crash_death_rate'])
    rollover_color = get_color(car['rollover_death_rate'])


    return render_template('car.html',
                           year=year,
                           make=make,
                           model=model,
                           overall_death_rate=car['overall_death_rate'],
                           multi_vehicle_death_rate=car['multi_vehicle_crash_death_rate'],
                           single_vehicle_death_rate=car['single_vehicle_crash_death_rate'],
                           rollover_death_rate=car['rollover_death_rate'],
                           overall_color=overall_color,
                           multi_vehicle_color=multi_vehicle_color,
                           single_vehicle_color=single_vehicle_color,
                           rollover_color=rollover_color)


if __name__ == '__main__':
    app.run(debug=True)
