# getMyList
# Author: Moises Marin
# Date: July 8, 2017
# Purpose: get shirt count with active filters
#
#

from __future__ import print_function
from pymongo import MongoClient
from random import randint
import random
import datetime


import json
import re
import locale
import unicodedata
import os

#Helper functions
def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n


def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None

def build_response(event,answer):
    #create json response
    thisIntent=event['currentIntent']['name']
    sessionAttributes = try_ex(lambda: event['sessionAttributes'])
    if sessionAttributes is None:
        sessionAttributes={}
    sessionAttributes["previousIntent"]=thisIntent

    data= {
                    'dialogAction': {
                                                  'type': 'Close',
                                      'fulfillmentState': 'Fulfilled',
                                               'message': {
                                                           'contentType': 'PlainText',
                                                               'content':  answer
                                                           }
                                    }

              }
    data['sessionAttributes']= sessionAttributes 
                                     
    json_data = json.dumps(data)
    print (json_data)
    return data


def find_in_collection(pin):

    db_user=os.environ['db_user']
    db_pass=":"+os.environ['db_pass']
    db_url="@"+os.environ['db_url']
    db_name=os.environ['db_name']
    db_collection=os.environ['db_collection']
    db_connect_string="mongodb://"+db_user+db_pass+db_url+"/"+db_name
    connection = MongoClient(db_connect_string)
    db_level = connection[db_name]
    db = connection[db_name][db_collection]
    
    #example of db query    
    #results_brands = db.find({}).distinct('upcMap.size')
    
    results = db.find_one({'pin': int(pin)})
    
    if results is None:
        results=''
        
    if len(results) > 0:
        data=results['savedShirts'].replace("*SKIP*","")
    else:
        data=''

    return data
    
    
def insert_in_collection(savedShirts):

    db_user=os.environ['db_user']
    db_pass=":"+os.environ['db_pass']
    db_url="@"+os.environ['db_url']
    db_name=os.environ['db_name']
    db_collection=os.environ['db_collection']
    db_connect_string="mongodb://"+db_user+db_pass+db_url+"/"+db_name
    connection = MongoClient(db_connect_string)
    db_level = connection[db_name]
    db = connection[db_name][db_collection]
    
    #example of db query    
    #results_brands = db.find({}).distinct('upcMap.size')
    
    #try up to 5 times to get a unique pin, use the pin if still not unique
    for x in range(1, 5):
        pin=random.randint(1, 9999)
        result_count = db.count({'pin': pin})
        if result_count ==0:
            break


    result = db.insert_one({
                                     'pin': pin,
                             'savedShirts': savedShirts,
                                    'date': datetime.datetime.utcnow()
                           })

    return pin


#Functions from decision tree
def LoadMyList(event):
    #Validate required input
    pin = try_ex(lambda: event['currentIntent']['slots']['List_Info'])
    if pin is None:
        pin=''
    
    if pin:
        savedShirts=find_in_collection(pin)
        if savedShirts:
            event['sessionAttributes']['savedShirts']=savedShirts
            message="Your list has been loaded!"
        else:
            message="Sorry, that pin didn't match a list!"
    else:
        message="Need a pin to find your list mate!"
    
    
    return build_response(event,message)

def SaveMyList(event):
    
    #Validate required input
    savedShirts = try_ex(lambda: event['sessionAttributes']['savedShirts'])
    if savedShirts is None:
        savedShirts=''
    
    if savedShirts:
        pin=insert_in_collection (savedShirts)
        message="Your list was saved with pin: "+str(pin)
    else:
        message="Your list is empty, add some shirts first :)"

    
    return build_response(event,message)


#MAIN FUNCTION
def lambda_handler(event, context):
    
    #Print invocation info
    currentIntentName=event['currentIntent']['name']
    print ("INFO: Current intent="+currentIntentName)
    print ("INFO: Event parameters:")
    print (event)
    print ("INFO: End-of-multi-line-info")

    #Define sessionAttributes if not defined
    sessionAttributes = try_ex(lambda: event['sessionAttributes'])
    if sessionAttributes is None:
        sessionAttributes={}    
        event['sessionAttributes']=sessionAttributes

    #Decision tree
    if currentIntentName=='LoadMyList':
        data=LoadMyList(event)
    elif currentIntentName=='SaveMyList':
        data=SaveMyList(event)
    else:
        print ("ALERT: Reached end of decision tree without action!")

    return data

