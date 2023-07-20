from flask import Flask, render_template
import requests

app = Flask(__name__)

def get_car_data():
    url_link = "https://www.iihs.org/api/driver-death-rates/get-view-model"
    response = requests.post(url_link)
    data = response.json()
    info = data["Info"]

    car_data = []

    overall_death_rates = []
    multi_vehicle_crash_death_rates = []
    single_vehicle_crash_death_rates = []
    rollover_death_rates = []

    for i in info:
        model_year_span = i['ModelYearSpan']
        start_year_str, end_year_str = model_year_span.split('-')
        
        # Add the missing digits to the start year if it's shorter
        if len(start_year_str) < 4:
            start_year_str = "20" + start_year_str
        
        # Add the missing digits to the end year if it's shorter
        if len(end_year_str) < 4:
            end_year_str = "20" + end_year_str
        
        start_year, end_year = int(start_year_str), int(end_year_str)

        for year in range(start_year, end_year + 1):
            car = {
                'year': year,
                'make': i['Vehicle'].split(' ')[0],
                'model': '-'.join(i['Vehicle'].split(' ')[1:]),  # Replace spaces with hyphens in the model name
                'overall_death_rate': float(i['OverallDeathRate']) if i['OverallDeathRate'] else 0,
                'multi_vehicle_crash_death_rate': float(i['MultiVehicleDeathRate']) if i['MultiVehicleDeathRate'] else 0,
                'single_vehicle_crash_death_rate': float(i['SingleVehicleDeathRate']) if i['SingleVehicleDeathRate'] else 0,
                'rollover_death_rate': float(i['RolloverDeathRate']) if i['RolloverDeathRate'] else 0
            }
            car_data.append(car)

            # Collect individual death rates for each car
            overall_death_rates.append(car['overall_death_rate'])
            multi_vehicle_crash_death_rates.append(car['multi_vehicle_crash_death_rate'])
            single_vehicle_crash_death_rates.append(car['single_vehicle_crash_death_rate'])
            rollover_death_rates.append(car['rollover_death_rate'])

    # Calculate 50th percentile for each death rate type
    overall_percentile = sorted(overall_death_rates)[len(overall_death_rates) // 2]
    multi_percentile = sorted(multi_vehicle_crash_death_rates)[len(multi_vehicle_crash_death_rates) // 2]
    single_percentile = sorted(single_vehicle_crash_death_rates)[len(single_vehicle_crash_death_rates) // 2]
    rollover_percentile = sorted(rollover_death_rates)[len(rollover_death_rates) // 2]

    # Calculate maximum and minimum for each death rate type
    max_overall = max(overall_death_rates)
    min_overall = min(overall_death_rates)
    max_multi = max(multi_vehicle_crash_death_rates)
    min_multi = min(multi_vehicle_crash_death_rates)
    max_single = max(single_vehicle_crash_death_rates)
    min_single = min(single_vehicle_crash_death_rates)
    max_rollover = max(rollover_death_rates)
    min_rollover = min(rollover_death_rates)

    return car_data, overall_percentile, multi_percentile, single_percentile, rollover_percentile, max_overall, min_overall, max_multi, min_multi, max_single, min_single, max_rollover, min_rollover

def get_color_class(rate, percentile, minimum, maximum):
    if rate == minimum:
        return "bg-success"  # Green (Minimum value)
    
    elif rate == maximum:
        return "bg-danger" 
    
    elif rate > percentile:
        return "bg-danger"  # Red (Above 50th percentile)
    
    elif rate == percentile:
        return 'bg-warning'
    
    else:
        return "bg-success"  # Green (Below 50th percentile)

@app.route('/')
def index():
    (
        car_data, overall_percentile, multi_percentile, single_percentile, rollover_percentile,
        max_overall, min_overall, max_multi, min_multi, max_single, min_single, max_rollover, min_rollover
    ) = get_car_data()
    return render_template('index.html', cars=car_data, max_overall=max_overall, min_overall=min_overall,
                           max_multi=max_multi, min_multi=min_multi, max_single=max_single, min_single=min_single,
                           max_rollover=max_rollover, min_rollover=min_rollover)

@app.route('/car/<int:year>/<make>/<model>/')
def car(year, make, model):
    (
        car_data, overall_percentile, multi_percentile, single_percentile, rollover_percentile,
        max_overall, min_overall, max_multi, min_multi, max_single, min_single, max_rollover, min_rollover
    ) = get_car_data()
    search_make = make.lower()  # Convert the search make to lowercase
    search_model = model.lower()  # Convert the search model to lowercase

    selected_car = None

    for car in car_data:
        if year == car['year'] and search_make == car['make'].lower() and search_model == car['model'].lower():
            selected_car = car
            break

    if selected_car is None:
        return "Car not found", 404

    return render_template('car.html', car=selected_car, overall_percentile=overall_percentile,
                           multi_percentile=multi_percentile, single_percentile=single_percentile,
                           rollover_percentile=rollover_percentile, max_overall=max_overall, min_overall=min_overall,
                           max_multi=max_multi, min_multi=min_multi, max_single=max_single, min_single=min_single,
                           max_rollover=max_rollover, min_rollover=min_rollover, get_color_class=get_color_class)

if __name__ == "__main__":
    app.run(debug=True)
