# Runner
## Intro
The primary purpose of the runner is to operate in CSV mode. An example of the csv structure is shown below:
<table>
    <thead>
        <th>Port</th>
        <th>Endpoint</th>
        <th>Arg 1</th>
        <th>Arg 2</th>
        <th>Arg 3</th>
    </thead>
    <tbody>
        <tr>
            <td>5001</td>
            <td>move-to-well</td>
            <td>0</td>
            <td>0</td>
            <td></td>
        </tr>
        <tr>
            <td>5000</td>
            <td>transfer</td>
            <td>0</td>
            <td>5</td>
            <td>0.3</td>
        </tr>
        <tr>
            <td>5001</td>
            <td>move-to-well</td>
            <td>0</td>
            <td>1</td>
            <td></td>
        </tr>
        <tr>
            <td>5000</td>
            <td>transfer</td>
            <td>0</td>
            <td>5</td>
            <td>0.2</td>
        </tr>
        <tr>
            <td>5002</td>
            <td>transfer</td>
            <td>3</td>
            <td>5</td>
            <td>0.1</td>
        </tr>
        <tr>
            <td>5001</td>
            <td>move-to-well</td>
            <td>0</td>
            <td>2</td>
            <td></td>
        </tr>
        <tr>
            <td>5000</td>
            <td>transfer</td>
            <td>0</td>
            <td>5</td>
            <td>0.1</td>
        </tr>
        <tr>
            <td>5002</td>
            <td>transfer</td>
            <td>3</td>
            <td>5</td>
            <td>0.2</td>
        </tr>
        <tr>
            <td>5001</td>
            <td>move-to-well</td>
            <td>0</td>
            <td>3</td>
            <td></td>
        </tr>
        <tr>
            <td>5002</td>
            <td>transfer</td>
            <td>3</td>
            <td>5</td>
            <td>0.3</td>
        </tr>
    </tbody>
</table>

This can be transpiled into requests to be sent to the various components connected to the runner. The columns are described as follows:
 - The `Port` column tells the runner what the address of the desired instrument's server is. 
 - The `Endpoint` column tells the runner what endpoint to send its request to
 - The `Arg` columns tell the runner what arguments to include in its request

The first line of the CSV above would be transpiled into something like this:
```javascript
    fetch('http://localhost:5000/pman/move', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(
                {'args':["0","0"]}
            )
    });
```

## Persist Modular Automation Network (PMAN) API
### Overview
PMAN provides a standardized way for Automation Modules to talk to each other. A PMAN request is a post request with a body component that looks like this:
```json
{
    "args":[
        "arg1",
        "arg2",
        "etc"
    ],
}
```
This structure exists so that it's easy for the front-end to turn a CSV row into an API call.

The standard response looks like this:
```json
{
    "status":"No Error",
    "message":"Have a nice day"
}
```
The `status` field is not for the HTTP status, it's for communicating whether anything is wrong with the instrument.
The `message` field is for any information that the instrument may wish to commuicate to the operator -- things like "initiating transfer from port 0 to port 3". This structure is so that it's easy to display something like this to the user in an embedded terminal:
```
localhost:5000 -- No Error -- initiating transfer from port 0 to port 3
```
## PMAN Endpoints
All PMAN endpoints begin with `/pman`. This makes them easy to find and identify.
For a Flask API implementation, it is recommended to put PMAN endpoints in their own Blueprint.
The standard endpoints are:
    - `/pman/` -- must respond to a GET request. Used by runner to check to see if a server is running.

Most PMAN endpoints will accept a request, start an action, and return a response when the action is complete.

## PMAN Runner Config
PMAN runners can make use of configuration files to abstract away technical details of PMAN setups. An example config is shown below:
```json
{
    "instruments": {
        "SmartStageXY": [
            {
                "network-port": 5001
            }
        ],
        "SPM": [
            {
                "network-port": 5000,
                "valve-map": {
                    "1":"air",
                    "2":"dihydrogen monoxide",
                    "12":"waste"
                }
            },
            {
                "network-port": 5003,
                "valve-map": {
                    "1":"air",
                    "2":"Toluene",
                    "12":"waste"
                }
            }
        ]
    }
}
```
This config describes a setup with two SPM pumps and one SmartStageXY. The SPM servers are running on localhost:5000 and localhost:5003, while the SmartStageXY is running on localhost:5001. The SPMs are configured with valve maps to tell the runner where various liquids are.