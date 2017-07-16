# coding: utf-8 
# setParameter
# Author: Moises Marin
# Date: June 20, 2017
# Purpose: Set a search parameter
#
#


from __future__ import print_function
from pymongo import MongoClient
from random import randint


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


def lambda_handler(event, context):
   
    
    print(context)
    print('texty text')
    print(event)
    
    intentName=event['currentIntent']['name']
    setColor=''
    setBrand=''
    setSize=''
    setPrice=''
    setQuantifier=''
    previousShirt=''
    thisBrand=''
    
    

    sessionAttributes = try_ex(lambda: event['sessionAttributes'])
    if sessionAttributes is None:
        sessionAttributes={}
    if len(sessionAttributes) >=1:
        previousColor = try_ex(lambda: event['sessionAttributes']['previousColor'])
        if previousColor is None:
            previousColor=''
        previousPrice = try_ex(lambda: event['sessionAttributes']['previousPrice'])
        if previousPrice is None:
            previousPrice=''
        previousSize = try_ex(lambda: event['sessionAttributes']['previousSize'])
        if previousSize is None:
            previousSize=''
        previousBrand = try_ex(lambda: event['sessionAttributes']['previousBrand'])
        if previousBrand is None:
            previousBrand=''
        previousStore = try_ex(lambda: event['sessionAttributes']['previousStore'])
        if previousStore is None:
            previousStore=''
    else:
        previousColor=''
        previousPrice=''
        previousSize=''
        previousBrand=''
        previousStore=''

    data={}
    slot_to_elicit='Color_Info'
    message={
      'contentType': 'PlainText',
      'content': 'We\'ll hello there! What can I do for you?'
    }

     
    nextAction='ElicitIntent'
    session_attributes={}
        

    json_data = json.dumps(data)
    print (data)
    

    locale.setlocale(locale.LC_ALL, 'en_US')

    db_user=os.environ['db_user']
    db_pass=":"+os.environ['db_pass']
    db_url="@"+os.environ['db_url']
    db_name=os.environ['db_name']
    db_collection=os.environ['db_collection']
    db_connect_string="mongodb://"+db_user+db_pass+db_url+"/"+db_name
    



    search_value={}
    previousSize_tag='upcMap.size'
    previousBrand_tag='brand.name'
    previousColor_tag='upcMap.color'
    previousPrice_tag='upcMap.retailPrice'
    #used to get color from colorway
    regx=previousColor

    print (event['currentIntent']['name'])
    if event['currentIntent']['name'] == 'setBrand':
        regx_brand = re.compile(event['currentIntent']['slots']['Set_Brand'], re.IGNORECASE)
        regx_color = re.compile(previousColor, re.IGNORECASE)
        regx_size = re.compile(previousSize, re.IGNORECASE)

        search_value[previousBrand_tag]= regx_brand
        if previousPrice:
            regx_price = float(previousPrice)
            search_value[previousPrice_tag]= regx_price
        if previousColor:
            search_value[previousColor_tag]= regx_color
        if previousSize:
            search_value[previousSize_tag]= regx_size
        
        setBrand=event['currentIntent']['slots']['Set_Brand']

        
    if event['currentIntent']['name'] == 'SetPrice':
        regx_brand = re.compile(previousBrand, re.IGNORECASE)
        regx_price = float(event['currentIntent']['slots']['Set_Price'])
        regx_color = re.compile(previousColor, re.IGNORECASE)
        regx_size = re.compile(previousSize, re.IGNORECASE)

        if previousBrand:
            search_value[previousBrand_tag]= regx_brand
        search_value[previousPrice_tag]= regx_price
        if previousColor:
           search_value[previousColor_tag]= regx_color
        if previousSize:
            search_value[previousSize_tag]= regx_size
        
        setPrice=event['currentIntent']['slots']['Set_Price']

    if event['currentIntent']['name'] == 'SetSize':
        regx_brand = re.compile(previousBrand, re.IGNORECASE)
        regx_color = re.compile(previousColor, re.IGNORECASE)
        regx_size = re.compile(event['currentIntent']['slots']['Set_Size'].replace("(","\(").replace(")","\)")
                               , re.IGNORECASE)

        if previousBrand:
            search_value[previousBrand_tag]= regx_brand
        if previousPrice:
            regx_price = float(previousPrice)
            search_value[previousPrice_tag]= regx_price
        if previousColor:
            search_value[previousColor_tag]= regx_color
        search_value[previousSize_tag]= regx_size

        setSize=event['currentIntent']['slots']['Set_Size']


    if event['currentIntent']['name'] == 'SetColor':
        regx_brand = re.compile(previousBrand, re.IGNORECASE)
        regx_color = re.compile(event['currentIntent']['slots']['Set_Color'], re.IGNORECASE)
        regx_size = re.compile(previousSize, re.IGNORECASE)
        regx=regx_color

        if previousBrand:
            search_value[previousBrand_tag]= regx_brand
        if previousPrice:
            search_value[previousPrice_tag]= regx_price
            regx_price = float(previousPrice)
        search_value[previousColor_tag]= regx_color
        if previousSize:
            search_value[previousSize_tag]= regx_size
        
        setColor= event['currentIntent']['slots']['Set_Color']

    if event['currentIntent']['name'] == 'SetStore':
        intent_store = try_ex(lambda: event['currentIntent']['slots']['Set_Store'])
        if intent_store is None:
            intent_store=''
            regx_intent_store=''
        else:
            regx_intent_store=re.compile(intent_store, re.IGNORECASE)
        
        if regx_intent_store:
            if re.search(regx_intent_store, 'Macys') is not None or re.search(regx_intent_store, 'Nordstrom') is not None or re.search(regx_intent_store, 'Decathlon') is not None or re.search(regx_intent_store, 'Palacio') or re.search(regx_intent_store, 'Zalando') is not None:
                db_collection=intent_store+'_shirts'
        regx=previousColor
        previousStore=db_collection
    elif previousStore:
        db_collection=previousStore+'_shirts'
        previousStore=db_collection
        
        
    connection = MongoClient(db_connect_string)
    db = connection[db_name][db_collection]
    
    print (search_value)
    print (db_collection)

    all_results = db.find(search_value)

    result_count = all_results.count()

    print ("results="+str(result_count))
    

    if result_count > 0:
        print (result_count)
        random_number=randint(0,result_count-1)
        print (random_number)
        #results = db.find(search_value)[random_number]
        results=all_results[random_number]
        
        currency=results['currency']
        if currency == 'MXN':
            currency_suffix=' MXN'
            currency_prefix='$'
        elif currency == 'USD':
            currency_suffix=''
            currency_prefix='$'
        elif currency == '€':
            currency_suffix='€'
            currency_prefix=''
        else:
            currency_suffix=''
            currency_prefix='$'
            
        link2shirt=results['url']
        imageshirt=results['default_image']
        imageBaseUrl=results['image_base_url']
        thisBrand=results['brand']['name']

        subtitle=''
        print (results['colorwayPrimaryImages'])
        fulfillmentState='Fulfilled'

        message2=results['name']

        print (results['upcMap'])
        flag=0
        
        #fetch first price as sample price of item
        for offer in results['upcMap']:
            print(offer)
            print (offer['retailPrice'])
            thisPrice=currency_prefix+ str(locale.format("%d", float(offer['retailPrice']), grouping=True))+currency_suffix
            #define default color
            if not regx:
                regx =  offer['color']

            break
        for offer in results['upcMap']:
            print('checking')
            print (offer['color'])
            thisColor=offer['color']
            if (re.search(regx, offer['color']) is not None):
                thisColor=offer['color']
                previousShirt=offer['upc']
                print('color found')
                map_color=''
                try:
                    map_color=results['colorwayPrimaryImages'][thisColor]
                    thisColorUrl=imageBaseUrl+map_color
                except KeyError:
                    thisColorUrl=imageshirt

                imageshirt=thisColorUrl
                break
            
        print (imageshirt)
        
        
    else:
        print ('No results')
        link2shirt='No results with those conditions'
        message2='No results with those conditions'
        fulfillmentState='Failed'
        thisPrice='T-shirt'
        titleText=''
        imageshirt=''
    
    connection.close()

    #create json response
    data = {}
    leaf2 = {}
    leaf3 = {}
    
    if result_count > 0:
        previousShirtDetails=thisBrand+":"+thisColor

        leaf3['contentType'] = 'PlainText'

        leaf3['content'] = message2

        #this lines removes the link sent with the responseCard
        leaf2['message'] = leaf3
        leaf2['type']='Close'
        leaf2['fulfillmentState']=fulfillmentState
        leaf2['responseCard']={
                               "version": 1,
                           "contentType": "application/vnd.amazonaws.card.generic",
                    "genericAttachments": [
                                            {
                                                 "title":thisPrice,
                                              "imageUrl":imageshirt,
                                              "subTitle":thisColor,
                                     "attachmentLinkUrl":link2shirt,
                                     "buttons":[ 
                                                {
                                                  "text":"next",
                                                 "value":"next"
                                                }
                                               ]
                                            } 
                                           ] 
                                }
        
     
        data['dialogAction'] = leaf2
        
        data['sessionAttributes']=event['sessionAttributes']

        data['sessionAttributes']['setBrand']= setBrand
        data['sessionAttributes']['setColor']= setColor
        data['sessionAttributes']['setSize']= setSize
        data['sessionAttributes']['setPrice']= setPrice
        data['sessionAttributes']['setQuantifier']= setQuantifier
        data['sessionAttributes']['previousStore']= previousStore.replace("_shirts","")
                                    
        data['sessionAttributes']['previousColor']=thisColor
        data['sessionAttributes']['previousBrand']=thisBrand
        data['sessionAttributes']['previousIntent']=intentName
        data['sessionAttributes']['previousShirt']=previousShirt
        data['sessionAttributes']['previousShirtDetails']=previousShirtDetails



    else:
        data= {
                    'dialogAction': {
                                                  'type': 'Close',
                                      'fulfillmentState': 'Failed',
                                               'message': {
                                                           'contentType': 'PlainText',
                                                               'content': 'No results with those conditions'
                                                          }
                                    }
              }
        print (data)

    
    json_data = json.dumps(data)
    print (json_data)
    
    
    
    
    
    return data 

