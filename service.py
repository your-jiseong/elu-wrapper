# -*- coding: utf-8 -*-

import sys, re
from bottle import route, run, template, request, response, post
import urllib, urllib2
import json

def enable_cors(fn):
  def _enable_cors(*args, **kwargs):
    # set CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

    if request.method != 'OPTIONS':
      # actual request; reply with the actual response
      return fn(*args, **kwargs)
    
  return _enable_cors

def send_postrequest(url, input_string):
  opener = urllib2.build_opener()
  request = urllib2.Request(url, data=input_string, headers={'Content-Type':'application/json'})
  return opener.open(request).read()

@route(path='/entity_linking', method=['OPTIONS', 'POST'])
@enable_cors
def do_request():
  if not request.content_type.startswith('application/json'):
    return 'Content-type:application/json is required.'

  request_str = request.body.read()
  try:
    request_str = request_str.decode('utf-8')
  except:
    pass
  request_json = json.loads(request_str)

  if 'input' in request_json and 'type' in request_json:
    elu_address = 'http://143.248.135.139:2223/entity_linking'
    input_str = json.dumps({'text': request_json['input']})
    output_json = {'output': []}
    for r in json.loads(send_postrequest(elu_address, input_str)):
      namedEntity = r['text']
      start = r['start_offset'] + 1
      end = r['end_offset'] + 1
      offset = r['end_offset'] - r['start_offset']
      disambiguatedURL = r['uri']
      o = {'namedEntity': namedEntity, 'start': start, 'end': end, 'offset': offset, 'disambiguatedURL': disambiguatedURL}
      output_json['output'].append(o)
    return json.dumps(output_json, ensure_ascii=False, encoding='utf8')
  else:
    return '"input" or "type" field is required.'

run(host='143.248.135.139', port=2224)