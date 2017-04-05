# -*- coding: utf-8 -*-
import sys, json
import urllib, urllib2

from bottle import route, run, template, request, response, post
import ipfinder

host_ip = ipfinder.get_ip_address('eth0')
port = '2224'

def service(i_json, conf):
	o_json = None

	# Service routine -------------------------------------

	elu_address = 'http://qamel.kaist.ac.kr:2223/entity_linking'

	i_text = json.dumps({'text': i_json['input']})
	o_json = {'output': []}

	for r in json.loads(send_postrequest(elu_address, i_text)):
		namedEntity = r['text']
		start = r['start_offset'] + 1
		end = r['end_offset'] + 1
		offset = r['end_offset'] - r['start_offset']
		disambiguatedURL = r['uri']

		o = {'namedEntity': namedEntity, 'start': start, 'end': end, 'offset': offset, 'disambiguatedURL': disambiguatedURL}
		o_json['output'].append(o)

	o_json = json.dumps(o_json, ensure_ascii=False, encoding='utf8')
	o_json = json.loads(o_json)

	# /Service routine -------------------------------------

	return o_json

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
	
def set_conf(new_conf):
	# default configuration
	i_file = open('conf.json', 'r')
	sInput = i_file.read()
	i_file.close()
	conf = json.loads(sInput)

	# updated configuration
	conf.update(new_conf)
	
	return conf

@route(path='/entity_linking', method=['OPTIONS', 'POST'])
@enable_cors
def do_request():
	if not request.content_type.startswith('application/json'):
		return 'Content-type:application/json is required.'

	# input reading
	i_text = request.body.read()
	try:
		i_text = i_text.decode('utf-8')
	except:
		pass
	i_json = json.loads(i_text)

	# configuration setting
	try:
		conf = set_conf(i_json['conf'])
	except:
		conf = set_conf({})

	# request processing
	o_json = service(i_json, conf)
	o_text = json.dumps(o_json, indent=5, separators=(',', ': '), sort_keys=True) 

	return o_text

run(server='cherrypy', host=host_ip, port=port)