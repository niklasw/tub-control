#!/usr/bin/env python3

from flask import redirect, render_template, url_for, request
import flaskr
from sensors import TSensors, ds18b20
import relay
from relay.utils import *
from flask_socketio import SocketIO, emit

control = relay.init_controls()

app = flaskr.create_app()

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
def relay_toggle(action):

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
        control.sensors.active = False if control.sensors.active else True
    elif action == 'pump_temp':
        control.set_temperatures['pump'] = int(request.form['temp'])
        control.sensors.active = False if control.sensors.active else True
    else:
        return "Wrong action error "+action

    return redirect(url_for('index'))


if __name__ == '__main__':
   try:
       app.run(host="192.168.10.202", port=5000, debug=False)
   except KeyboardInterrupt:
       control.quit()



