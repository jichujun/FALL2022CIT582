import requests
import json

def pin_to_ipfs(data):
    assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
    files = {'file': json.dumps(data)}

    response = requests.post('https://ipfs.infura.io:5001/api/v0/add', files=files)
    p = response.json()
    cid = p['Hash']

    return cid

def get_from_ipfs(cid,content_type="json"):
    assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
    #YOUR CODE HERE	
    params = (
   ('arg', 'QmSioQ78VA8hS6DZnrWWReX8MLWvSzcZobtjK322Wottz'),
)
    response = requests.post('https://ipfs.infura.io:5001/api/v0/block/get', params=params)
    data = json.load(response.text)
    assert isinstance(data,dict), f"get_from_ipfs should return a dict"
    return data
