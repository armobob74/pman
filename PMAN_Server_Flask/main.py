from website import create_app
from flask import render_template
import sys, os


args = sys.argv
if len(args) > 1:
    pman_config_name = args[1]
else:
    pman_config_name = 'aurora_pump_test_windows.json'
if not pman_config_name.endswith('.json'):
    pman_config_name += '.json'

app = create_app(pman_config_name)

pman_config = app.config['pman-config']
if 'port' in pman_config: 
    app_port = pman_config['port']
else:
    app_port = 5000

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False, port=app_port)
