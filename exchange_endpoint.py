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
        platform = content["payload"]["platform"]
        pk = content["payload"]["pk"]
        sk = content["sig"]
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
        result = False
        if platform == "Ethereum":

            eth_encoded_msg = eth_account.messages.encode_defunct(text=payload)
            # eth_sig_obj = eth_account.Account.sign_message(eth_encoded_msg,signature=sk)

            if eth_account.Account.recover_message(eth_encoded_msg,signature=sk) == pk:
                print('Ethereum verified')
                result = True

        elif platform == "Algorand":
            if algosdk.util.verify_bytes(payload.encode('utf-8'),sk,pk):
                print( "Algorand verified" )
                result =  True
        
        # TODO: Add the order to the database
        if result:
            order = content['payload']
            newOrder = Order(receiver_pk=order['receiver_pk'], sender_pk=order['sender_pk'],
                    sell_currency=order['sell_currency'], buy_currency=order['buy_currency'],
                    sell_amount=order['sell_amount'],buy_amount=order['buy_amount'], signature = sk)
            g.session.add(newOrder)
        
            # TODO: Fill the order
            for orderToCheck in session.query(Order).filter(Order.filled == None).all():
                if orderToCheck.buy_currency == newOrder.sell_currency and orderToCheck.sell_currency == newOrder.buy_currency:
                    if orderToCheck.sell_amount/orderToCheck.buy_amount >= newOrder.buy_amount/orderToCheck.sell_amount:
                        # set the timestamp
                        time = datetime.now()
                        newOrder.filled = time
                        orderToCheck.filled = time

                        # set the id
                        newOrder.counterparty_id = orderToCheck.id
                        orderToCheck.counterparty_id = newOrder.id

                        # if not filled
                        newNewOrder = Order()
                        if newOrder.buy_amount > orderToCheck.sell_amount:
                            creatorId = newOrder.id
                            buyAmount = newOrder.buy_amount - orderToCheck.sell_amount
                            sellAmount = buyAmount * (newOrder.sell_amount/newOrder.buy_amount)
                            newNewOrder= Order(sender_pk=newOrder.sender_pk,receiver_pk=newOrder.receiver_pk, 
                            buy_currency=newOrder.buy_currency, sell_currency=newOrder.sell_currency, 
                            buy_amount=buyAmount, sell_amount=sellAmount, creator_id=creatorId )
                        elif orderToCheck.buy_amount > newOrder.sell_amount:
                            creatorId = orderToCheck.id
                            buyAmount = orderToCheck.buy_amount - newOrder.sell_amount
                            sellAmount = buyAmount * (orderToCheck.sell_amount/orderToCheck.buy_amount)
                            newNewOrder= Order(sender_pk=orderToCheck.sender_pk,receiver_pk=orderToCheck.receiver_pk, 
                            buy_currency=orderToCheck.buy_currency, sell_currency=orderToCheck.sell_currency, 
                            buy_amount=buyAmount, sell_amount=sellAmount, creator_id=creatorId )
                        g.session.add(newNewOrder)
                        g.session.commit()
                        break

                g.session.commit()
        else:
            log_message(payload)
    return jsonify(True)
        
        # TODO: Be sure to return jsonify(True) or jsonify(False) depending on if the method was successful
        

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

if __name__ == '__main__':
    app.run(port='5002')