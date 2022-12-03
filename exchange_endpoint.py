from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask import jsonify
import json
import eth_account
import algosdk
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only
from datetime import datetime
import sys

from models import Base, Order, Log
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

@app.before_request
def create_session():
    g.session = scoped_session(DBSession)

@app.teardown_appcontext
def shutdown_session(response_or_exc):
    sys.stdout.flush()
    g.session.commit()
    g.session.remove()


""" Suggested helper methods """

def check_sig(payload,sig):
    pass

def fill_order(order,txes=[]):
    pass
  
def log_message(d):
    # Takes input dictionary d and writes it to the Log table
    # Hint: use json.dumps or str() to get it in a nice string form
    pass

""" End of helper methods """



@app.route('/trade', methods=['POST'])
def trade():
    print("In trade endpoint")
    if request.method == "POST":
        content = request.get_json(silent=True)
        print( f"content = {json.dumps(content)}" )
        columns = [ "sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform" ]
        fields = [ "sig", "payload" ]
        platform = content['payload']['platform']
        sig = content['sig']
        pk = content["payload"]["sender_pk"]
        payload = json.dumps(content["payload"])

        for field in fields:
            if not field in content.keys():
                print( f"{field} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )
        
        for column in columns:
            if not column in content['payload'].keys():
                print( f"{column} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )
            
        #Your code here
        #Note that you can access the database session using g.session

        # TODO: Check the signature
        
        # TODO: Add the order to the database
        
        # TODO: Fill the order
        
        # TODO: Be sure to return jsonify(True) or jsonify(False) depending on if the method was successful
        valid = False
        if platform == "Ethereum":
            eth_encoded_msg = eth_account.messages.encode_defunct(text=payload)
            if eth_account.Account.recover_message(eth_encoded_msg,signature=sig) == pk:
                print( "Eth sig verifies!" )
                valid = True
        if platform == "Algorand":
            print("algo###############################3", platform)
            if algosdk.util.verify_bytes(payload.encode('utf-8'),sig,pk):
                print( "Algo sig verifies!" )
                valid = True
        #if valid, store order in order table, if not store in log table
        if valid:
            order_obj = Order(sender_pk=content["payload"]['sender_pk'],receiver_pk=content["payload"]['receiver_pk'], 
                      buy_currency=content["payload"]['buy_currency'], sell_currency=content["payload"]['sell_currency'], 
                      buy_amount=content["payload"]['buy_amount'], sell_amount=content["payload"]['sell_amount'], signature=sig)
            g.session.add(order_obj)
            orders = g.session.query(Order).filter(Order.filled == None).all() 
            for e_order in orders:
            #2 Check if there are any existing orders that match
                if e_order.buy_currency == order_obj.sell_currency and e_order.sell_currency == order_obj.buy_currency:
                    if e_order.sell_amount/ e_order.buy_amount >= order_obj.buy_amount/order_obj.sell_amount:
                        #3.1 Set the filled field to be the current timestamp on both orders
                        
                        time = datetime.now()
                        order_obj.filled = time
                        e_order.filled = time
                        
                        #3.2 Set counterparty_id to be the id of the other order
                        e_order.counterparty_id = order_obj.id
                        order_obj.counterparty_id = e_order.id
                        
                        #3.3 if not completely filled
                        new_order = Order()
                        if order_obj.buy_amount > e_order.sell_amount:
                            c_by = order_obj.id
                            n_buy = order_obj.buy_amount - e_order.sell_amount
                            n_sell = n_buy * (order_obj.sell_amount/order_obj.buy_amount)
                            new_order = Order(sender_pk=order_obj.sender_pk,receiver_pk=order_obj.receiver_pk, 
                                    buy_currency=order_obj.buy_currency, sell_currency=order_obj.sell_currency, 
                                    buy_amount=n_buy, sell_amount=n_sell, creator_id=c_by )

                        elif e_order.buy_amount > order_obj.sell_amount:
                            c_by = e_order.id
                            n_buy = e_order.buy_amount - order_obj.sell_amount
                            n_sell = n_buy * (e_order.sell_amount/e_order.buy_amount)
                            new_order = Order(sender_pk=e_order.sender_pk,receiver_pk=e_order.receiver_pk, 
                                    buy_currency=e_order.buy_currency, sell_currency=e_order.sell_currency, 
                                    buy_amount=n_buy, sell_amount=n_sell, creator_id=c_by )
                        g.session.add(new_order)
                        g.session.commit()
                        break
            g.session.commit()
            print("add order to table")
        else:
            log_message(payload)
            print("add to log")

    return jsonify(True)  

@app.route('/order_book')
def order_book():
    #Your code here
    #Note that you can access the database session using g.session
    result = {}
    list = []
    orders = g.session.query(Order).filter().all()
    for order in orders:
        order_dic = {}
        order_dic['sender_pk'] = order.sender_pk
        order_dic['receiver_pk'] = order.receiver_pk
        order_dic['buy_currency'] = order.buy_currency
        order_dic['sell_currency'] = order.sell_currency
        order_dic['buy_amount'] = order.buy_amount
        order_dic['sell_amount'] = order.sell_amount
        order_dic['signature'] = order.signature
        list.append(order_dic)
    
    result['data'] = list
    return jsonify(result)


if __name__ == '__main__':
    app.run(port='5002', debug=True)