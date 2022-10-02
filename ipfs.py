import requests
import json

def pin_to_ipfs(data):
	assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
	#YOUR CODE HERE
	files = {'file':json.dumps(data)}
	response = requests.post('https://ipfs.infura.io:5001/api/v0/add', files = files, auth =  ('2FbCGzje6KR95vrKJQt9CQADJWU', '1013db1372f0197c6612c26b1413fc0b'))
	cid = response.json()['Hash']
	return cid

def get_from_ipfs(cid,content_type="json"):
	assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
	#YOUR CODE HERE	
	params = (('arg', cid),)

	response = requests.post('https://ipfs.infura.io:5001/api/v0/cat', params=params, auth =  ('2FbCGzje6KR95vrKJQt9CQADJWU', '1013db1372f0197c6612c26b1413fc0b'))
	data = json.loads(response.text)
	assert isinstance(data,dict), f"get_from_ipfs should return a dict"
	return data