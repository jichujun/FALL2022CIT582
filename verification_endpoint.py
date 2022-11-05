from inspect import signature
from flask import Flask, request, jsonify
from flask_restful import Api
import json
import eth_account
import algosdk

app = Flask(__name__)
api = Api(app)
app.url_map.strict_slashes = False

@app.route('/verify', methods=['GET','POST'])
def verify():
    content = request.get_json(silent=True)

    platform = content["payload"]["platform"]
    pk = content['payload']['pk']
    sk = content['sig']
    payload = json.dumps(content["payload"])
    
    result = False
    if platform == "Ethereum":

        eth_encoded_msg = eth_account.messages.encode_defunct(text=payload)
        eth_sig_obj = eth_account.Account.sign_message(eth_encoded_msg,signature=sk)

        if eth_account.Account.recover_message(eth_encoded_msg,signature=eth_sig_obj.signature.hex()) == pk:
            print('Ethereum verified')
            result = True

    elif platform == "Algorand":
        if algosdk.util.verify_bytes(payload.encode('utf-8'),sk,pk):
            print( "Algorand verified" )
            result =  True
    

    #Check if signature is valid
    # result = True #Should only be true if signature validates
    return jsonify(result)

if __name__ == '__main__':
    app.run(port='5002')
