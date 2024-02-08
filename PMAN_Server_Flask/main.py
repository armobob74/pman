from website import create_app
from flask import render_template

app = create_app()

pman_config = app.config['pman-config']
if 'port' in pman_config: 
    app_port = pman_config['port']
else:
    app_port = 5000

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=app_port)
