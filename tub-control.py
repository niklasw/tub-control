#!/usr/bin/env python3

from flask import redirect, render_template, url_for, request
import flaskr
from sensors import TSensors, ds18b20
import relay
from relay.utils import *
from plotter import Plotter
from flask_socketio import SocketIO, emit

control = relay.init_controls()
app, htpasswd = flaskr.create_app()

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
                           timer_status = 'timer_on' \
                                   if control.timer.active else 'timer_off',
                           timer_remain = control.timer.remaining(),
                           sensors_status = 'sensors_on' \
                                   if control.sensors.active else 'sensors_off')

@app.route('/control/<action>', methods=['GET', 'POST'])
@htpasswd.required
def relay_toggle(action, user):

    if user == 'guest':
        return redirect(url_for('index'))

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

    return redirect(url_for('index'))

@app.route('/plot/<interval>')
def plot(interval):
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from datetime import datetime

    plotter = Plotter(control)

    columns = list(control.sensors.log_data())
    columns+= list(control.log_data())
    columns+= list(control.timer.log_data())
    columns+= list(control.relay.log_data())

    plotter.columns = columns
    data = plotter.get_data(interval)
    print('Plotter data shape =', data.shape)
    img_url = plotter.simple_plot(data)

    plotter.quit()

    reload_thing = '?'+str(int(datetime.now().timestamp()))

    return render_template('plotter.html', \
                            plot_data = data,
                            image = img_url+reload_thing)
                            

#def shutdown_server():
#    func = request.environ.get('werkzeug.server.shutdown')
#    if func is None:
#        raise RuntimeError('Not running with the Werkzeug Server')
#    Warning('Shutting server down')
#    func()

if __name__ == '__main__':
    app.run(host="192.168.10.202", port=5000, debug=False)



