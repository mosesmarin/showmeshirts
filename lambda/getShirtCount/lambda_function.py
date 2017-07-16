# getShirtCount
# Author: Moises Marin
# Date: July 8, 2017
# Purpose: get shirt count with active filters
#
#

from __future__ import print_function
from pymongo import MongoClient
from random import randint
import random


import json
import re
import locale
import unicodedata
import os


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


print('Loading function')



def tell_me_how_many(event, context):

    locale.setlocale(locale.LC_ALL, 'en_US')

    db_user=os.environ['db_user']
    db_pass=":"+os.environ['db_pass']
    db_url="@"+os.environ['db_url']
    db_name=os.environ['db_name']
    db_collection=os.environ['db_collection']
    db_connect_string="mongodb://"+db_user+db_pass+db_url+"/"+db_name
    
    connection = MongoClient(db_connect_string)
    db_level = connection[db_name]
    
    previousStore = try_ex(lambda: event['sessionAttributes']['previousStore'])
    if previousStore is None:
        previousStore=''    
    
    #set store if present
    intent_store = try_ex(lambda: event['currentIntent']['slots']['Store_Info'])
    if intent_store is None:
        intent_store=''
        regx_intent_store=''
    else:
        regx_intent_store=re.compile(intent_store, re.IGNORECASE)

    print ('intent store is:' +intent_store +'--previous store is:')
    
    #re-use previous store check
    if not intent_store and previousStore:
        intent_store=previousStore
        regx_intent_store=re.compile(intent_store, re.IGNORECASE)

    #override default store if needed    
    if regx_intent_store:
        if re.search(regx_intent_store, 'Macys') is not None or re.search(regx_intent_store, 'Nordstrom') is not None or re.search(regx_intent_store, 'Decathlon') is not None or re.search(regx_intent_store, 'Palacio') is not None or re.search(regx_intent_store, 'Zalando') is not None  or re.search(regx_intent_store, 'palacio_blusas') is not None:
            db_collection=intent_store+'_shirts'
    
    db = connection[db_name][db_collection]


    print (event['currentIntent']['name'])
    thisIntent=event['currentIntent']['name']
    if event['currentIntent']['name'] == 'TellMeHowMany':
        search_value={}
        previousSize_tag='upcMap.size'
        previousBrand_tag='brand.name'
        previousColor_tag='upcMap.color'
        previousPrice_tag='upcMap.retailPrice'
        previousPriceUSD_tag='upcMap.retailPriceUSD'
        previousPrice = try_ex(lambda: event['sessionAttributes']['previousPrice'])
        if previousPrice is None:
            previousPrice=''
        previousSize = try_ex(lambda: event['sessionAttributes']['previousSize'])
        if previousSize is None:
            previousSize=''
        previousColor = try_ex(lambda: event['sessionAttributes']['previousColor'])
        if previousColor is None:
            previousColor=''
        previousBrand = try_ex(lambda: event['sessionAttributes']['previousBrand'])
        if previousBrand is None:
            previousBrand=''
        previousQuantifier = try_ex(lambda: event['sessionAttributes']['previousQuantifier'])
        if previousQuantifier is None:
            previousQuantifier=''

        if previousPrice:
            if previousQuantifier:
                regx_intent_price = float(previousPrice)
                if re.search("great",previousQuantifier) is not None:
                    print ("INFO: Adding search value:"+previousPriceUSD_tag)
                    print ("INFO: Adding search value:"+previousPrice)
                    search_value[previousPriceUSD_tag]={"$gt": regx_intent_price}
                else:
                    print ("INFO: Adding search value:"+previousPriceUSD_tag)
                    print ("INFO: Adding search value:"+previousPrice)
                    search_value[previousPriceUSD_tag]={"$lt": regx_intent_price}
            else:
                expensive_flag=previousPrice
                if re.search(previousPrice, "expensive") is not None or re.search(previousPrice, "inexpensive") is not None:
                    expensive_flag=previousPrice
                print ("INFO: Adding search value:"+previousPrice_tag)
                print ("INFO: Adding search value:"+previousPrice.replace("inexpensive","").replace("expensive",""))
                if previousPrice.replace("inexpensive","").replace("expensive","").strip():
                    regx_price = float(previousPrice.replace("inexpensive","").replace("expensive",""))
                    search_value[previousPrice_tag]=regx_price
                elif expensive_flag:
                    if re.search(expensive_flag,"expensive") is not None:
                        regx_price = float(99)
                        search_value[previousPriceUSD_tag]={"$gt": regx_price}
                        previousPrice='expensive'
                    elif re.search(expensive_flag,"inexpensive") is not None:
                        regx_price = float(49)
                        search_value[previousPriceUSD_tag]={"$lt": regx_price}
                        previousPrice='inexpensive'
                else:
                    regx_price=''
        if previousSize:
            print ("INFO: Adding search value:"+previousSize_tag)
            print ("INFO: Adding search value:"+previousSize)
            regx_size  = re.compile(previousSize, re.IGNORECASE) 
            search_value[previousSize_tag]=regx_size        
        if previousBrand:
            print ("INFO: Adding search value:"+previousBrand_tag)
            print ("INFO: Adding search value:"+previousBrand)
            regx_brand = re.compile(previousBrand, re.IGNORECASE) 
            search_value[previousBrand_tag]=regx_brand        
        if previousColor:
            print ("INFO: Adding search value:"+previousColor_tag)
            print ("INFO: Adding search value:"+previousColor)
            regx_color = re.compile(previousColor, re.IGNORECASE) 
            search_value[previousColor_tag]=regx_color
            regx_intent_color=regx_color
        
        if len(search_value) > 0:
            print ("INFO: Counting with search value:")
            print(search_value)
            print("INFO: End-of-multi-line-info")
            result_distinct_upc=db.find(search_value).distinct('_id')
            print ("INFO: Counting distinct _id")
            print (result_distinct_upc)
            print ("INFO: End-of-mul-line-info")
            #result_count = str(db.count(search_value))
            result_count = str(len(result_distinct_upc))
            print ("INFO: result_count="+result_count)

        else:
            result_count = str(db.count(search_value))
            print ("INFO: Count is entire store="+result_count)



        value_tag='sizes'
        sort_key=str.lower
    
    else:
        results_brands = db.find({}).distinct('upcMap.size')
        value_tag='sizes'
        sort_key=str.lower

    if event['currentIntent']['name'] == 'TellMeHowMany':
        answer='I count: '+result_count
        brand_count=1
    
    

    connection.close()

    #create json response
    sessionAttributes = try_ex(lambda: event['sessionAttributes'])
    if sessionAttributes is None:
        sessionAttributes={}
    sessionAttributes["previousIntent"]=thisIntent
    
    if intent_store:
       sessionAttributes["previousStore"]=db_collection.replace("_shirts","")


    if brand_count > 0:

   
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
                                     


    else:
        data= {
                    'dialogAction': {
                                                  'type': 'Close',
                                      'fulfillmentState': 'Failed',
                                               'message': {
                                                           'contentType': 'PlainText',
                                                               'content': 'No brands to show!'
                                                          }
                                    }
              }
    
        print (data)

    
    json_data = json.dumps(data)
    print (json_data)
    return data

def tell_me_size_my_list(event, context):
    print ("INFO: executing tell_me_size_my_list")

    savedShirts = try_ex(lambda: event['sessionAttributes']['savedShirts'])
    if savedShirts is None:
        savedShirts=''
    
    if savedShirts:
        result_count=len(savedShirts.split(","))-1
        answer='I count in your list: '+str(result_count)
    else:
        answer='Your list is empty my friend.'



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
    if currentIntentName=='TellMeHowMany':
        data=tell_me_how_many(event, context)
    elif currentIntentName=='HowBigMyList':
        data=tell_me_size_my_list(event, context) 
    else:
        print ("ALERT: Reached end of decision tree without action!")

    return data

