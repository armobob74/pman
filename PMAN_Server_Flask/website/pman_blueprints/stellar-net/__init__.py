from flask import current_app, request, Blueprint
from stellarnet_driverLibs import stellarnet_driver3 as sn
import json
from ..utils import extract_pman_args 


stellar_net = Blueprint('stellar_net',__name__, url_prefix='/pman/stellar-net')

@stellar_net.get('/')
def index():
    return "hi"

@stellar_net.post('/params')
@extract_pman_args
def set_up(inttime, scansavg,smooth, xtiming):
    spectrometer = sn.array_get_spec_only(0) 
    sn.setParam(spectrometer, inttime, scansavg, smooth, xtiming, True)
    return{'status': "Ok", 'message': "Setting params for spectrometer"}

@stellar_net.post('/data')
def get_data():
    spectrometer = sn.array_get_spec_only(0) 
    spectX = sn.getSpectrum_X(spectrometer)
    spectY = sn.getSpectrum_Y(spectrometer)

    return{'Wavelength': spectX, 'Spectrum-Data': spectY}

