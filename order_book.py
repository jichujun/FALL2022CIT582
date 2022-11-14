from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models import Base, Order
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def process_order(order):
    #Your code here
    #1. Insert the order
    newOrder = Order(receiver_pk=order['receiver_pk'], sender_pk=order['sender_pk'],
                       sell_currency=order['sell_currency'], buy_currency=order['buy_currency'],
                       sell_amount=order['sell_amount'],buy_amount=order['buy_amount'] )
    
    session.add(newOrder)
    #2. Check if there are matched order
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
                session.add(newNewOrder)
                session.commit()
                break

    session.commit()