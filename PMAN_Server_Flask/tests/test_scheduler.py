"""
These tests are currently pretty much just looking for release-test functionality
"""
import os
import sys
sys.path.append('..')
import pytest
from random import randint, random
from website import create_app
from website.pman_blueprints.csv_utils import read_csv
os.chdir('..')

@pytest.fixture
def app():
    app = create_app('pytest_scheduler.json')
    app.config['TESTING'] = True
    tc = app.test_client()
    tc.scheduler = app.scheduler
    tc.config = app.config
    return tc

def test_init(app):
    response = app.get('/')
    assert response.status_code == 200
    assert 'OK' in response.status

def rand_list_str(n):
    a = [round(10*random(),4) for _ in range(n)]
    a.sort()
    s = str(a)[1:-1].replace(' ','')
    return s

def rand_data_row():
    """ ['Pump_Address','From_Port', 'To_Port', 'Volumes', 'Hours', 't0'] """
    n = 10
    min_port = 1
    max_port = 10
    hours = rand_list_str(n)
    volumes = rand_list_str(n)
    t0 = f'March {randint(1,15)}, 22{randint(10,99)} at 1:51:18 PM PST'
    addr = str(randint(1,30))

    from_port = randint(min_port, max_port)
    to_port = randint(min_port, max_port)
    while to_port == from_port:
        to_port = randint(min_port, max_port)

    return [addr, str(from_port), str(to_port), volumes, hours, t0]



def test_table_update_e2e(app):
    """
    Make sure that the saveTable() function works
    Test begins with a simulated POST request,
        then confirms that the csv has been updated.
        then confirms that the scheduler has been correctly updated
    """

    # this simulates the table data from the front end
    datalen = randint(1,20)
    data = [
            ['Pump_Address',	'From_Port', 'To_Port', 'Volumes', 'Hours', 't0']
        ]
    data += [rand_data_row() for _ in range(datalen)]

    expected_num_jobs = 0
    for row in data[1:]:
        hours = row[-2]
        expected_num_jobs += len(hours.split(','))

    response = app.post('/pman/release-scheduler/save-table', json={'data': data})

    updated_csv = read_csv(app.config['pman-config']['scheduler_tablepath'],'\t')

    job_list = [str(j.next_run_time) for j in app.scheduler.get_jobs()]
    assert len(job_list) == expected_num_jobs
    assert response.status_code == 302
