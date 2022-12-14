from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine, select, MetaData, Table
from flask import jsonify
import json
import eth_account
import algosdk
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only

from models import Base, Order, Log
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

#These decorators allow you to use g.session to access the database inside the request code
@app.before_request
def create_session():
    g.session = scoped_session(DBSession) #g is an "application global" https://flask.palletsprojects.com/en/1.1.x/api/#application-globals

@app.teardown_appcontext
def shutdown_session(response_or_exc):
    g.session.commit()
    g.session.remove()

"""
-------- Helper methods (feel free to add your own!) -------
"""

def log_message(d):
    l = Log(message =json.dump(m))
    g.session.addd(l)
    g.session.commit()

"""
---------------- Endpoints ----------------
"""
    
@app.route('/trade', methods=['POST'])
def trade():
    if request.method == "POST":
        content = request.get_json(silent=True)
        print( f"content = {json.dumps(content)}" )
        columns = [ "sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform" ]
        fields = [ "sig", "payload" ]

        error = False
        for field in fields:
            if not field in content.keys():
                print( f"{field} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )
        
        error = False
        for column in columns:
            if not column in content['payload'].keys():
                print( f"{column} not received by Trade" )
                error = True
        if error:
            print( json.dumps(content) )
            log_message(content)
            return jsonify( False )
            
        #Your code here
        #Note that you can access the database session using g.session
        platform = content['payload']['platform']
        sig = content['sig']
        pk = content["payload"]["sender_pk"]
        payload = json.dumps(content["payload"])

        #verify signature
        verify_flag = False
        if platform == "Ethereum":

            eth_encoded_msg = eth_account.messages.encode_defunct(text=payload)
            # eth_sig_obj = eth_account.Account.sign_message(eth_encoded_msg,signature=sk)

            if eth_account.Account.recover_message(eth_encoded_msg,signature=sig) == pk:
                print('Ethereum verified')
                verify_flag = True

        elif platform == "Algorand":
            if algosdk.util.verify_bytes(payload.encode('utf-8'),sig,pk):
                print( "Algorand verified" )
                verify_flag = True

        if verify_flag:
            order_obj = Order(sender_pk=content["payload"]['sender_pk'],receiver_pk=content["payload"]['receiver_pk'], 
                      buy_currency=content["payload"]['buy_currency'], sell_currency=content["payload"]['sell_currency'], 
                      buy_amount=content["payload"]['buy_amount'], sell_amount=content["payload"]['sell_amount'], signature=sig)
            g.session.add(order_obj)
            g.session.commit()
            print("Order to Table")
        else:
            log_message(payload)
            print("Logged")

    return jsonify(True)


@app.route('/order_book')
def order_book():
    #Your code here
    #Note that you can access the database session using g.session
    data = g.session.query(Order)
    result = []
    for d in data:
        dic = {}
        dic['sender_pk'] = d.sender_pk
        dic['receiver_pk'] = d.receiver_pk
        dic['buy_currency'] = d.buy_currency
        dic['sell_currency'] = d.sell_currency
        dic['buy_amount'] = d.buy_amount
        dic['sell_amount'] = d.sell_amount
        dic['signature'] = d.signature
        result.append(dic)
    resultDict = {'data': result}
    return resultDict
    return jsonify(result)

if __name__ == '__main__':
    app.run(port='5002')
