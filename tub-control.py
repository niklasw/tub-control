#!/usr/bin/env python3

from flask import redirect, render_template, url_for, request, Response
import flaskr
import os
from sensors import TSensors, ds18b20
import relay
from relay.utils import *
from plotter import Plotter
from flask_socketio import SocketIO, emit

control = relay.init_controls()
app, htpasswd = flaskr.create_app()

plotter = Plotter(control)

@app.route('/')
@app.route('/index')
def index():
    control.buttons.get_status()

    temps = control.sensors.values

    import threading
    for thread in threading.enumerate():
        Debug(f'Thread running: {thread.name}')

    error_status = 'error' if not control.sensors.ok else ''

    return render_template('main.html',
                           aux_status='on' if control.buttons.aux_on else 'off',
                           pump_status='on' if control.buttons.pump_on else 'off',
                           heat_status='on' if control.buttons.heat_on else 'off',
                           error_status = error_status,
                           duration = control.timer.duration,
                           interval = control.timer.interval,
                           intervals = control.timer.intervals,
                           durations = control.timer.durations,
                           pool_temp = '{0:0.2f}'.format(temps['pool']),
                           pump_temp = '{0:0.2f}'.format(temps['pump']),
                           set_pump_temp = '{0:d}'.format(control.set_temperatures['pump']),
                           set_pool_temp = '{0:d}'.format(control.set_temperatures['pool']),
                           climate_temp = '{0:0.1f}'.format(control.remote_sensor.temp),
                           house_temp = '{0:0.1f}'.format(control.house_sensor.temp),
                           timer_status = 'timer_on' \
                                   if control.timer.active else 'timer_off',
                           timer_remain = control.timer.remaining(),
                           sensors_status = 'sensors_on' \
                                   if control.sensors.active else 'sensors_off')

@app.route('/control/<action>', methods=['GET', 'POST'])
@htpasswd.required
def relay_toggle(action, user):

    if user == 'guest':
        return redirect(url_for('index', _external=True, _scheme='https'))

    if action == 'pump':
        control.buttons.pump()
        control.timer.stop()
        control.sensors.active = False
    elif action == 'aux':
        control.buttons.aux()
    elif action == 'heat':
        control.buttons.heat()
        control.timer.stop()
        control.sensors.active = False
    elif action == 'timer':
        interval = request.form['timer_interval']
        duration = request.form['timer_duration']
        control.timer.set(int(interval),int(duration))
    elif action == 'pool_temp':
        control.set_temperatures['pool'] = int(request.form['temp'])
        control.sensors.active = not control.sensors.active
    elif action == 'pump_temp':
        control.set_temperatures['pump'] = int(request.form['temp'])
        control.sensors.active = not control.sensors.active
    else:
        return "Wrong action error "+action

    return redirect(url_for('index', _external=True, _scheme='https'))

@app.route('/plot.png')
def plot_png():
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    import io
    output = io.BytesIO()
    FigureCanvas(plotter.figure).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/plot/<interval>')
def plot(interval):
    from matplotlib.figure import Figure
    from datetime import datetime
    from numpy import average

    plotter.columns = control.logger.column_names
    plotter.set_time_range(interval, end_time=datetime.now())
    plotter.get_data()
    data = plotter.array_data
    Info('Plotter data shape =', data.shape)
    plotter.create_figure()

    img_url = '/plot.png'

    try:
        dTdt = plotter.ddt('pool')
        if len(dTdt) > 2:
            avg_length = min(10, len(dTdt))
            dTdt = average(dTdt[-avg_length:])
        else:
            dTdt = 0
        pool_volume = 3500
        Cp = 4200
        rho =1.15
        W = dTdt*pool_volume*rho*Cp
    except:
        Warning('Charge calculaion failed')
        W = 0
        dTdt = 0
    
    return render_template('plotter.html', \
                            charge_rate = round(W),
                            deg_per_hour = round(dTdt*3600,1),
                            image = img_url)
                            
if __name__ == '__main__':
    print(f'PID: {os.getpid()}')

    host = os.getenv('TUB_SERVER')
    port = os.getenv('TUB_PORT')
    host_ip = host if host else "192.168.10.210"
    host_port = int(port) if port else 5000

    app.run(host=host_ip, port=host_port, debug=False)

    control.quit()



