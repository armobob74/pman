"""
These tests are currently pretty much just looking for release-test functionality
"""
import os
import sys
sys.path.append('..')
sys.path.append('../..')
import pytest
from random import randint
from website import create_app
from pman_blueprints.csv_utils import read_csv

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
            ['Network_port', 'Valve_port', 'Hours', 't0'],
        ]

    data += [['1', '1', f"{str(list(range(1,randint(2,10))))[1:-1].replace(' ','')}", f'March {randint(1,15)}, 22{randint(10,99)} at 1:51:18 PM PST'] for row in range(datalen)]

    expected_num_jobs = 0
    for row in data[1:]:
        hours = row[2]
        expected_num_jobs += len(hours.split(','))

    response = app.post('/pman/release-scheduler/save-table', json={'data': data})

    updated_csv = read_csv(app.config['pman-config']['scheduler_tablepath'],'\t')

    job_list = [str(j.next_run_time) for j in app.scheduler.get_jobs()]
    assert len(job_list) == expected_num_jobs
    assert response.status_code == 302
