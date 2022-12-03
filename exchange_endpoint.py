# from flask import Flask, request, g
# from flask_restful import Resource, Api
# from sqlalchemy import create_engine
# from flask import jsonify
# import json
# import eth_account
# import algosdk
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.orm import scoped_session
# from sqlalchemy.orm import load_only
# from datetime import datetime
# import math
# import sys
# import traceback

# # TODO: make sure you implement connect_to_algo, send_tokens_algo, and send_tokens_eth
# from send_tokens import connect_to_algo, connect_to_eth, send_tokens_algo, send_tokens_eth

# from models import Base, Order, TX
# engine = create_engine('sqlite:///orders.db')
# Base.metadata.bind = engine
# DBSession = sessionmaker(bind=engine)

# app = Flask(__name__)

# """ Pre-defined methods (do not need to change) """

# @app.before_request
# def create_session():
#     g.session = scoped_session(DBSession)

# @app.teardown_appcontext
# def shutdown_session(response_or_exc):
#     sys.stdout.flush()
#     g.session.commit()
#     g.session.remove()

# def connect_to_blockchains():
#     try:
#         # If g.acl has not been defined yet, then trying to query it fails
#         acl_flag = False
#         g.acl
#     except AttributeError as ae:
#         acl_flag = True
    
#     try:
#         if acl_flag or not g.acl.status():
#             # Define Algorand client for the application
#             g.acl = connect_to_algo()
#     except Exception as e:
#         print("Trying to connect to algorand client again")
#         print(traceback.format_exc())
#         g.acl = connect_to_algo()
    
#     try:
#         icl_flag = False
#         g.icl
#     except AttributeError as ae:
#         icl_flag = True
    
#     try:
#         if icl_flag or not g.icl.health():
#             # Define the index client
#             g.icl = connect_to_algo(connection_type='indexer')
#     except Exception as e:
#         print("Trying to connect to algorand indexer client again")
#         print(traceback.format_exc())
#         g.icl = connect_to_algo(connection_type='indexer')

        
#     try:
#         w3_flag = False
#         g.w3
#     except AttributeError as ae:
#         w3_flag = True
    
#     try:
#         if w3_flag or not g.w3.isConnected():
#             g.w3 = connect_to_eth()
#     except Exception as e:
#         print("Trying to connect to web3 again")
#         print(traceback.format_exc())
#         g.w3 = connect_to_eth()
        
# """ End of pre-defined methods """
        
# """ Helper Methods (skeleton code for you to implement) """

# def log_message(message_dict):
#     g.session.add(Log(message=json.dumps(d)))
#     g.session.commit()
#     return

# def check_sig(payload,sig):
#     payload_str = json.dumps(payload)
#     sender_pk = payload.get('sender_pk')
#     platform = payload.get('platform')
    
#     if platform == 'Algorand':
#         result = algosdk.util.verify_bytes(payload_str.encode('utf-8'),sig, sender_pk)
#     elif platform == 'Ethereum':
#         eth_encoded_msg = eth_account.messages.encode_defunct(text=payload_str)
#         result = eth_account.Account.recover_message(eth_encoded_msg,signature=sig) == sender_pk
#     return result

# def get_algo_keys():
#     mnemonic_secret = 'monkey'
#     algo_sk = mnemonic.to_private_key(mnemonic_secret)
#     algo_pk = mnemonic.to_public_key(mnemonic_secret)
    
#     return algo_sk, algo_pk


# def get_eth_keys(filename = "eth_mnemonic.txt"):
#     w3 = Web3()
#     with open(filename,'r') as file:
#         mnemonic = file.read().strip()
#     mnemonic = 'arrange youth please bracket gas honey matrix empower web boat hour key'
#     eth_account.Account.enable_unaudited_hdwallet_features()
#     acct = w3.eth.account.from_mnemonic(mnemonic)
#     eth_sk = acct._private_key
#     eth_pk = acct._address

#     return eth_sk, eth_pk

# def valid_order(new_order, old_order):
#     c1 = new_order.filled == None
#     c2 = new_order.sell_currency == old_order.buy_currency
#     c3 = new_order.buy_currency == old_order.sell_currency
#     c4 = ((new_order.sell_amount * old_order.sell_amount) >= (new_order.buy_amount * old_order.buy_amount))
#     return (c1 & c2 & c3 & c4) 
  
# def fill_order(order, txes=[]):
#     buy_currency = order['buy_currency']
#     sell_currency = order['sell_currency']
#     buy_amount = order['buy_amount']
#     sell_amount = order['sell_amount']
#     sender_pk = order['sender_pk']
#     receiver_pk = order['receiver_pk']
#     tx_id = order['tx_id']
    
#     if order.get('creator_id') == None:
#         new_order = Order(buy_currency = buy_currency,
#                       sell_currency = sell_currency,
#                       buy_amount = buy_amount,
#                       sell_amount = sell_amount,
#                       sender_pk = sender_pk,
#                       receiver_pk = receiver_pk,
#                       tx_id = tx_id)
#     else: 
#         new_order = Order(buy_currency = buy_currency,
#                       sell_currency = sell_currency,
#                       buy_amount = buy_amount,
#                       sell_amount = sell_amount,
#                       sender_pk = sender_pk,
#                       receiver_pk = receiver_pk,
#                       tx_id = tx_id,
#                       creator_id = order.get('creator_id'))
        
#     g.session.add(new_order)
#     g.session.commit()
    
#     unfilled_orders = g.session.query(Order).filter(Order.filled == None).all()
    
#     for old_order in unfilled_orders:
#         if valid_order(new_order, old_order):
            
#             old_order.filled = datetime.now()
#             new_order.filled = datetime.now()
#             old_order.counterparty_id = new_order.id
#             new_order.counterparty_id = old_order.id
#             g.session.commit()
            
#             if new_order.buy_amount == old_order.sell_amount:
#                 tx1 = []
#             else:
#                 child_order = {}
#                 if new_order.buy_amount > old_order.sell_amount:
#                     child_order['buy_currency'] = new_order.buy_currency
#                     child_order['sell_currency'] = new_order.sell_currency
#                     child_order['buy_amount'] = new_order.buy_amount - old_order.sell_amount
#                     child_order['sell_amount'] = child_order['buy_amount']*(new_order.sell_amount/new_order.buy_amount)*1.01
#                     child_order['sender_pk'] = new_order.sender_pk
#                     child_order['receiver_pk'] = new_order.receiver_pk
#                     child_order['creator_id'] = new_order.id
                    
#                 elif new_order.buy_amount < old_order.sell_amount:
#                     child_order['buy_currency'] = old_order.buy_currency
#                     child_order['sell_currency'] = old_order.sell_currency
#                     child_order['sell_amount'] = old_order.sell_amount - new_order.buy_amount
#                     child_order['buy_amount'] = child_order['sell_amount']*(old_order.buy_amount/old_order.sell_amount)*0.99
#                     child_order['sender_pk'] = old_order.sender_pk
#                     child_order['receiver_pk'] = old_order.receiver_pk
#                     child_order['creator_id'] = old_order.id
                    
#                 fill_order(child_order)
  
# def execute_txes(txes):
#     if txes is None:
#         return True
#     if len(txes) == 0:
#         return True
#     print( f"Trying to execute {len(txes)} transactions" )
#     print( f"IDs = {[tx['order_id'] for tx in txes]}" )
#     eth_sk, eth_pk = get_eth_keys()
#     algo_sk, algo_pk = get_algo_keys()
    
#     if not all( tx['platform'] in ["Algorand","Ethereum"] for tx in txes ):
#         print( "Error: execute_txes got an invalid platform!" )
#         print( tx['platform'] for tx in txes )

#     algo_txes = [tx for tx in txes if tx['platform'] == "Algorand" ]
#     eth_txes = [tx for tx in txes if tx['platform'] == "Ethereum" ]

#     # TODO: 
#     #       1. Send tokens on the Algorand and eth testnets, appropriately
#     #          We've provided the send_tokens_algo and send_tokens_eth skeleton methods in send_tokens.py
#     #       2. Add all transactions to the TX table

#     send_tokens_algo(g.acl, algo_sk, algo_txes)
#     send_tokens_eth(g.w3, eth_sk, eth_txes)
    
#     g.session.add_all(algo_txes)
#     g.session.add_all(eth_txes)
#     g.session.commit()  

# """ End of Helper methods"""
  
# @app.route('/address', methods=['POST'])
# def address():
#     if request.method == "POST":
#         content = request.get_json(silent=True)
#         if 'platform' not in content.keys():
#             print( f"Error: no platform provided" )
#             return jsonify( "Error: no platform provided" )
#         if not content['platform'] in ["Ethereum", "Algorand"]:
#             print( f"Error: {content['platform']} is an invalid platform" )
#             return jsonify( f"Error: invalid platform provided: {content['platform']}"  )
        
#         if content['platform'] == "Ethereum":
#             #Your code here
#             return jsonify( eth_pk )
#         if content['platform'] == "Algorand":
#             #Your code here
#             return jsonify( algo_pk )

# @app.route('/trade', methods=['POST'])
# def trade():
#     print( "In trade", file=sys.stderr )
#     connect_to_blockchains()
#     # get_keys()
#     if request.method == "POST":
#         content = request.get_json(silent=True)
#         columns = [ "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform", "tx_id", "receiver_pk"]
#         fields = [ "sig", "payload" ]
#         error = False
#         for field in fields:
#             if not field in content.keys():
#                 print( f"{field} not received by Trade" )
#                 error = True
#         if error:
#             print( json.dumps(content) )
#             return jsonify( False )
        
#         error = False
#         for column in columns:
#             if not column in content['payload'].keys():
#                 print( f"{column} not received by Trade" )
#                 error = True
#         if error:
#             print( json.dumps(content) )
#             return jsonify( False )
        
#         # Your code here
        
#         # 1. Check the 
#         sig = content.get('sig')
#         payload = content.get('payload')
        
#         # 2. Add the order to the table
#         if check_sig(payload, sig):
#             order_dict = {'sender_pk': payload.get('sender_pk'),
#                 'receiver_pk': payload.get('receiver_pk'),
#                 'buy_currency':payload.get('buy_currency'),
#                 'sell_currency':payload.get('sell_currency'),
#                 'buy_amount':payload.get('buy_amount'),
#                 'sell_amount':payload.get('sell_amount'),
#                 'tx_id':payload.get('tx_id')}
        
#             # 3a. Check if the order is backed by a transaction equal to the sell_amount (this is new)
#             if order_dict['sell_currency'] == 'Algorand':
#                 tx = g.icl.search_transactions(txid = order_dict['tx_id'])
#                 assert tx.amount == order_dict['sell_amount']
#                 tx_amount = tx.amount
#             elif order_dict['sell_currency'] == 'Ethereum':
#                 tx = g.w3.eth.get_transaction(order_dict['tx_id'])
#                 assert tx.value == order_dict['sell_amount']
#                 tx_amount = tx.value

#             if (tx_amount == order_dict['sell_amount']):
#                 try:
#                     fill_order(order_dict)
#                     return jsonify( True)
#                 except Exception as e:
#                     import traceback
#                     print(traceback.format_exc())
#                     print(e)
#             else:
#                 return jsonify(False)

#         # 3b. Fill the order (as in Exchange Server II) if the order is valid
        
#         # 4. Execute the transactions
        
#         # If all goes well, return jsonify(True). else return jsonify(False)
#         else:
#             return jsonify(True)

# @app.route('/order_book')
# def order_book():
#     orders = g.session.query(Order).all()
#     orders_list = []
    
#     for order in orders:
#         orders_list.append({'sender_pk': order.sender_pk,
#                             'receiver_pk':order.receiver_pk,
#                             'buy_currency':order.buy_currency,
#                             'sell_currency':order.sell_currency,
#                             'buy_amount':order.buy_amount,
#                             'sell_amount':order.sell_amount,
#                             'signature':order.signature,
#                             'tx_id':order.tx_id})
    
#     return json.dumps({'data':orders_list})

# if __name__ == '__main__':
#     app.run(port='5002')

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
