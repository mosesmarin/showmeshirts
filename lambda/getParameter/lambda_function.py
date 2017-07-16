# getParameter
# Author: Moises Marin
# Date: June 20, 2017
# Purpose: Fetch brands, colors, sizes, prices
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


def more_shirts(event, context):
    print(event)
    

    
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
    previousShirt = try_ex(lambda: event['sessionAttributes']['previousShirt'])
    if previousShirt is None:
        previousShirt=''
    previousIntent = try_ex(lambda: event['sessionAttributes']['previousIntent'])
    if previousIntent is None:
        previousIntent=''
    previousStore = try_ex(lambda: event['sessionAttributes']['previousStore'])
    if previousStore is None:
        previousStore=''
    savedShirts = try_ex(lambda: event['sessionAttributes']['savedShirts'])
    if savedShirts is None:
        savedShirts=''
        
    intentName=event['currentIntent']['name']
    if intentName=='ShowSavedShirts':
        print ('INFO: Showing current list!')
        print ("INFO: saved list="+savedShirts)
        shirt_list=savedShirts.split(",")
        for shirt in shirt_list:
            print ('INFO: Looking at shirt='+shirt)
            if shirt.strip() and re.search("\*SKIP\*",shirt.strip() ) is None:
                saved_shirt=shirt.strip().split(":")
                shirt_store=saved_shirt[0].replace("DEFAULT", "macys")
                shirt_brand=saved_shirt[1]
                shirt_color=saved_shirt[2]
                shirt_upc  =saved_shirt[3]
                slots={'Color_Info':shirt_color, 'Brand_Info':shirt_brand, 'Upc_Info': shirt_upc, 'Store_Info': shirt_store}
                #Mark shirt to be skipped next time
                savedShirts=savedShirts.replace(shirt.strip(), "*SKIP*"+shirt.strip())
                event['sessionAttributes']['savedShirts']=savedShirts
                break
            else:
                slots={'Color_Info':previousColor, 'Brand_Info':previousBrand, 'Price_Info': previousPrice.replace("expensive","").replace("inexpensive",""), 'Store_Info': previousStore}
    
    else:
        #Normal flow
        slots={'Color_Info':previousColor, 'Brand_Info':previousBrand, 'Price_Info': previousPrice.replace("expensive","").replace("inexpensive",""), 'Store_Info': previousStore}
        
    data={}
    slot_to_elicit='Color_Info'
    message={
      'contentType': 'PlainText',
      'content': 'We\'ll hello there! What can I do for you?'
    }

     
    #If calling after showing shirt, show shirt 
    session_attributes = {     'previousColor': previousColor, 
                               'previousBrand': previousBrand,
                               'previousPrice': previousPrice,
                               'previousSize': previousSize,
                               'previousStore': previousStore.replace("_shirt",""),
                               'previousIntent': previousIntent,
                               'previousShirt': previousShirt


                         }
        
    data={
           # 'sessionAttributes': session_attributes,
           'sessionAttributes': event['sessionAttributes'],
            'dialogAction': {
                 'type': 'Delegate',
                'slots': slots
   
            }
        }

    json_data = json.dumps(data)
    print (json_data)
    return data


def tell_me_options(event, context):

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
        if re.search(regx_intent_store, 'Macys') is not None or re.search(regx_intent_store, 'Nordstrom') is not None or re.search(regx_intent_store, 'Decathlon') is not None or re.search(regx_intent_store, 'Palacio') is not None or re.search(regx_intent_store, 'Zalando') is not None or re.search(regx_intent_store, 'palacio_blusas') is not None:
            db_collection=intent_store+'_shirts'
    
    db = connection[db_name][db_collection]


    print (event['currentIntent']['name'])
    thisIntent=event['currentIntent']['name']
    if event['currentIntent']['name'] == 'TellMeBrands':
        #Fetch unique brands
        results_brands = db.find({}).distinct('brand.name')
        value_tag='brands'
        sort_key=str.lower
    elif event['currentIntent']['name'] == 'TellMeColors':
        results_brands = db.find({}).distinct('upcMap.color')
        value_tag='colors'
        sort_key=str.lower
    elif event['currentIntent']['name'] == 'TellMePrices':
        results_brands = db.find({}).distinct('upcMap.retailPrice')
        value_tag='prices'
        sort_key=float
    elif event['currentIntent']['name'] == 'TellMeStores':
        collection_suffix='_shirts'
        regx_suffix  = re.compile(collection_suffix, re.IGNORECASE) 
        results = db_level.collection_names()
        print (results)
        store_list=[]
        for store in results:
            if re.search(regx_suffix, store) is not None and len(store)>len(collection_suffix)+1:
                store_list.append(str(store).replace(collection_suffix,""))
        print (store_list)

        sort_key=str.lower


    else:
        results_brands = db.find({}).distinct('upcMap.size')
        value_tag='sizes'
        sort_key=str.lower

    if event['currentIntent']['name'] == 'TellMeStores':
        brand_count=1
        #build message with sorted list 
        list_stores=''
        for value in sorted(store_list, key=sort_key):
            if not list_stores:
                list_stores=str(value)
            else:
                list_stores=list_stores+'\n'+str(value)

        answer='I have shirts from:\n'+list_stores
    else:
        brand_count=len(results_brands)
        numbers_list=range(brand_count)
        if numbers_list>=5:
            sample_index= random.sample(numbers_list,  5) 
        else:
            sample_index= random.sample(numbers_list,  numbers_list)
        list_brands=''
        pre_list_brands=[]
        #get list of brands to be sorted
        for value in sample_index:
            pre_list_brands.append(str(results_brands[value]))
            
        #build message with sorted list 
        for value in sorted(pre_list_brands, key=sort_key):
            if not list_brands:
                list_brands=str(value)
            else:
                list_brands=list_brands+'\n'+str(value)

        answer='From '+db_collection.replace("_shirts","").title()+' I have '+str(brand_count)+' '+value_tag+' like:\n'+list_brands
        answer_message='From '+db_collection.replace("_shirts","").title()
        answer_title=' I have '+str(brand_count)+' '+value_tag+' like:'
        answer_subtitle=list_brands
    
    
    
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

def empty_saved_list(event, context):
    print ("INFO: executing empty_saved_list")
    #create json response
    thisIntent=event['currentIntent']['name']
    sessionAttributes = try_ex(lambda: event['sessionAttributes'])
    if sessionAttributes is None:
        sessionAttributes={}
    sessionAttributes["previousIntent"]=thisIntent
    
    data= {
                    'dialogAction': {
                                                  'type': 'Close',
                                      'fulfillmentState': 'Failed',
                                               'message': {
                                                           'contentType': 'PlainText',
                                                               'content': 'Your list is empty!'
                                                          }
                                    }
              }
    data['sessionAttributes']= sessionAttributes 

    print (data)
    json_data = json.dumps(data)
    print (json_data)
    return data

    
def lambda_handler(event, context):
    print (event['currentIntent']['name'])
    print (event)
    currentIntentName=event['currentIntent']['name']
    session_attributes = try_ex(lambda: event['sessionAttributes'])
    if session_attributes is None:
        session_attributes={'previousIntent' : None}    
        event['sessionAttributes']=session_attributes
    previousIntent = try_ex(lambda: event['sessionAttributes']['previousIntent'])
    if previousIntent is None:
        previousIntent=''
    savedShirts = try_ex(lambda: event['sessionAttributes']['savedShirts'])
    if savedShirts is None:
        savedShirts=''

    if re.search('Tell', currentIntentName ) is not None:
        print ("INFO: Condition1")
        data=tell_me_options(event, context)
    elif re.search('Tell', previousIntent ) is not None and re.search('HowMany', previousIntent ) is None and re.search('HowMany', previousIntent ) is None and currentIntentName!='ShowSavedShirts':
        print ("INFO: Condition2")
        #it's ShowMeAnother intent after TellMeSomething
        event['currentIntent']['name']=previousIntent
        data=tell_me_options(event, context)
    elif not savedShirts.strip() and currentIntentName=='ShowSavedShirts':
        print ("INFO: Condition3")
        data=empty_saved_list(event, context)
    else:
        #show more options
        print ("INFO: Condition4")
        data=more_shirts(event, context)
        
    return data

