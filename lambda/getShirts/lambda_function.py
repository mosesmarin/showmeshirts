# coding: utf-8 
# getShirts
# Author: Moises Marin
# Date: June 20, 2017
# Purpose: Fetch a shirt from DB
#
#

from __future__ import print_function
from pymongo import MongoClient
from random import randint
from bson.objectid import ObjectId



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

def validate_slot_info(event):
    print ("INFO: executing validate_slot_info")

    on_sale_flag=False

    intent_brand = try_ex(lambda: event['currentIntent']['slots']['Brand_Info'])
    if intent_brand is  None:
            intent_brand=''  
    intent_color = try_ex(lambda: event['currentIntent']['slots']['Color_Info'])
    if intent_color is  None:
            intent_color=''  
    inputTranscript = try_ex(lambda: event['inputTranscript'])
    if inputTranscript is  None:
            inputTranscript='' 
    if inputTranscript:
        inputTranscript=inputTranscript.lower()
        if re.search('on sale',inputTranscript) is not None:
            on_sale_flag=True
            event['currentIntent']['slots']['Sale_Info']=on_sale_flag
            inputTranscript=inputTranscript.replace('on sale', '').replace('  ', ' ')

    if inputTranscript:
        if re.search('me',inputTranscript) is not None and re.search('shirts',inputTranscript) is not None:
            color_check=inputTranscript.split('shirts')[0].split(' me')[1].strip()
            if color_check and color_check!=intent_color:
                event['currentIntent']['slots']['Color_Info']=color_check
                print ("ALERT: Override slot value:"+intent_color+"<>"+color_check)
        if re.search(' by ',inputTranscript) is not None:
            words=inputTranscript.split(' by ')[1]
            brand_check=''
            for word in words.split(' '):
                if word!='with' and word!='from':
                    brand_check=brand_check+word+' '
                if word=='with' or word=='from':
                    brand_check=brand_check
                    break
            brand_check=brand_check.strip()
            if brand_check and brand_check!=intent_brand:
                event['currentIntent']['slots']['Brand_Info']=brand_check
                print ("ALERT: Override slot value:"+intent_brand+"<>"+brand_check)
    return event
  

def show_me_shirts(event):

    locale.setlocale(locale.LC_ALL, 'en_US')

    event=validate_slot_info(event)
    print (event)

    db_user=os.environ['db_user']
    db_pass=":"+os.environ['db_pass']
    db_url="@"+os.environ['db_url']
    db_name=os.environ['db_name']
    db_default_collection=os.environ['db_default_collection']
    db_collection=db_default_collection
    db_connect_string="mongodb://"+db_user+db_pass+db_url+"/"+db_name
    connection = MongoClient(db_connect_string)

    #From lex input
    intentName = event['currentIntent']['name']
    expensive_flag=''
    previousQuantifier=''
    intent_sale=''

    sessionAttributes = event['sessionAttributes']

    if len(sessionAttributes) >=1:
        previousColor = try_ex(lambda: event['sessionAttributes']['previousColor'])
        if previousColor is None:
            previousColor=''
        previousQuantifier = try_ex(lambda: event['sessionAttributes']['previousQuantifier'])
        if previousQuantifier is None:
            previousQuantifier=''
        previousPrice = try_ex(lambda: event['sessionAttributes']['previousPrice'])
        if previousPrice is None:
            previousPrice=''
        if previousPrice:
            if re.search(previousPrice, "expensive") is not None or re.search(previousPrice, "inexpensive") is not None:
                expensive_flag=previousPrice
                previousPrice=previousPrice.replace("inexpensive","").replace("expensive","")
                print (previousPrice)
        previousSize = try_ex(lambda: event['sessionAttributes']['previousSize'])
        if previousSize is None:
            previousSize=''
        previousBrand = try_ex(lambda: event['sessionAttributes']['previousBrand'])
        if previousBrand is None:
            previousBrand=''   
        previousStore = try_ex(lambda: event['sessionAttributes']['previousStore'])
        if previousStore is None:
            previousStore=''
        previousShirt = try_ex(lambda: event['sessionAttributes']['previousShirt'])
        if previousShirt is None:
            previousShirt=''
        savedShirts = try_ex(lambda: event['sessionAttributes']['savedShirts'])
        if savedShirts is None:
            savedShirts=''
        previousOnSale = try_ex(lambda: event['sessionAttributes']['previousOnSale'])
        if previousOnSale is None:
            previousOnSale=''

    else:
        previousColor=''
        previousPrice=''
        previousSize=''
        previousBrand=''
        previousStore=''
        previousShirt=''
        savedShirts=''
        previousOnSale=''

    print ("INFO: Vars defnied:")
    print (previousColor)
    print (previousPrice)
    print (previousSize)
    print (previousBrand)
    print (previousStore)
    print (previousShirt)
    if intentName=='GetShirtInfo':
        print ("Intent is get shirt, make sure you cleanup previous vars!!!")
        previousColor=''
        previousPrice=''
        previousSize=''
        previousBrand=''
        previousQuantifier=''
        previousShirt=''
        previousOnSale=''

    print ("-----------------------------------------------------------------")

    #set store if one has been used
    intent_store = try_ex(lambda: event['currentIntent']['slots']['Store_Info'])
    if intent_store is None:
        if previousStore:
            intent_store=previousStore
        else:
            intent_store=''
    if intent_store:
        intent_store=intent_store.replace('on sale', '').strip()

    #set price if one has been used
    intent_price = try_ex(lambda: event['currentIntent']['slots']['Price_Info'])
    if intent_price is None:
        if previousPrice:
            intent_price=previousPrice
        else:
            intent_price=''

    #set brand if one has been used
    intent_brand = try_ex(lambda: event['currentIntent']['slots']['Brand_Info'])
    if intent_brand is  None:
        intent_brand=''    

    #set upc if one has been used
    intent_upc = try_ex(lambda: event['currentIntent']['slots']['Upc_Info'])
    if intent_upc is  None:
        intent_upc=''    
    
    #set sale info
    intent_sale = try_ex(lambda: event['currentIntent']['slots']['Sale_Info'])
    if intent_sale is  None:
        intent_sale='' 
    print ("INFO:")
    print (intent_sale)
    
    intent_color = try_ex(lambda: event['currentIntent']['slots']['Color_Info'])
    if intent_color is None:
        intent_color=''    
    print ("INFO: intent_color"+intent_color)
    intent_quantifier=try_ex(lambda: event['currentIntent']['slots']['Quantifier_Info'])
    if intent_quantifier is None:
        intent_quantifier=''
    intent_expensive_flag= try_ex(lambda: event['currentIntent']['slots']['Expensive_Info'])
    if intent_expensive_flag is None:
        intent_expensive_flag=''    
    print ("INFO: intent_expensive_flag"+intent_expensive_flag)
        
    #override environment store if one was specified
    if not intent_store:
        intent_store=''
        regx_intent_store=''
    else:
        regx_intent_store=re.compile(intent_store, re.IGNORECASE)
        previousStore=intent_store
        
    if regx_intent_store:
        if re.search(regx_intent_store, 'Macys') is not None or re.search(regx_intent_store, 'Nordstrom') is not None or re.search(regx_intent_store, 'Decathlon') is not None or re.search(regx_intent_store, 'Palacio') is not None or re.search(regx_intent_store, 'Zalando') is not None:
                db_collection=intent_store+'_shirts'
                print ("INFO: using db_collection="+db_collection)
    
    previousSize_tag='upcMap.size'
    previousBrand_tag='brand.name'
    previousColor_tag='upcMap.color'
    previousPrice_tag='upcMap.retailPrice'
    previousPriceUSD_tag='upcMap.retailPriceUSD'
    intent_color_tag='upcMap.color'
    intent_price_tag='upcMap.retailPrice'
    intent_brand_tag='brand.name'
    intent_upc_tag='_id'#'upcMap.upc'
    intent_onSale_tag='upcMap.onSale'


    
    search_value={}
    regx_intent_color=''

    if intentName == 'ShowMeAnother':
        print ("INFO: Executing line 164")
        print ("INFO: previousQuantifier="+previousQuantifier)

        if previousPrice:
            if previousQuantifier:
                regx_intent_price = float(previousPrice)
                if re.search("great",previousQuantifier) is not None:
                    search_value[previousPriceUSD_tag]={"$gt": regx_intent_price}
                else:
                    search_value[previousPriceUSD_tag]={"$lt": regx_intent_price}
            else:
                regx_price = float(previousPrice)
                search_value[previousPrice_tag]=regx_price
                print ("a)regx_price="+str(regx_price))

        if not previousPrice and not previousQuantifier and intent_price:
            regx_price = float(intent_price)
            search_value[previousPrice_tag]=regx_price
            print ("b)regx_price="+str(regx_price))

        if previousOnSale:
            search_value[intent_onSale_tag]=True  
        if previousSize:
            regx_size  = re.compile(previousSize, re.IGNORECASE) 
            search_value[previousSize_tag]=regx_size        
        if previousBrand:
            regx_brand = re.compile(previousBrand, re.IGNORECASE) 
            search_value[previousBrand_tag]=regx_brand
        if previousColor:
            regx_color = re.compile(previousColor, re.IGNORECASE) 
            search_value[previousColor_tag]=regx_color
            regx_intent_color=regx_color
        
            intent_store = previousStore.split("_")[0]

            regx_color = re.compile(previousColor, re.IGNORECASE) 
            search_value[previousColor_tag]=regx_color
            regx_intent_color=regx_color
        if expensive_flag:
            if re.search(expensive_flag,"expensive") is not None:
                regx_price = float(99)
                search_value[previousPriceUSD_tag]={"$gt": regx_price}
                previousPrice='expensive'
            elif re.search(expensive_flag,"inexpensive") is not None:
                regx_price = float(49)
                search_value[previousPriceUSD_tag]={"$lt": regx_price}
                previousPrice='inexpensive'
    elif intentName == 'ShowMeMostExpensive' or intentName == 'ShowMeLeastExpensive':
        previousShirt=''
        previousOnSale=''

        #set collection to use
        db = connection[db_name][db_collection]
        if intentName == 'ShowMeMostExpensive':
            pipe = [{ '$group' : { '_id': None, 'm': { '$max' : "$upcMap.retailPrice" }}}]
        if intentName == 'ShowMeLeastExpensive':
            pipe = [{ '$group' : { '_id': None, 'm': { '$min' : "$upcMap.retailPrice" }}}]
        results_m=db.aggregate(pipeline=pipe)
        for doc in results_m:
            m_price=doc['m'][0]
            print('Maximum current price:',m_price)
            search_value[intent_price_tag]=m_price
            break

    else:
        #Show me shirt intent, clean previous shirt filter
        previousShirt=''
        previousColor=''
        previousBrand=''
        previousPrice=''
        previousOnSale=''

        
        if  intent_expensive_flag:
            intent_color=intent_expensive_flag
            print ('INFO: using intent_color as intent_expensive_flag' +intent_color)

        if intent_color:
            regx_intent_color_2_price = re.compile(intent_color, re.IGNORECASE)
            if re.search(regx_intent_color_2_price,"expensive") is not None:
                regx_price = float(99)
                search_value[previousPriceUSD_tag]={"$gt": regx_price}
                previousPrice='expensive'
            elif re.search(regx_intent_color_2_price,"inexpensive") is not None:
                regx_price = float(49)
                search_value[previousPriceUSD_tag]={"$lt": regx_price}
                previousPrice='inexpensive'
            else:
                regx_intent_color = re.compile(intent_color, re.IGNORECASE)
                search_value[intent_color_tag]=regx_intent_color      
                
                if intentName=='ShowSavedShirts':
                    previousColor=''
                else:
                    previousColor=intent_color
        if intent_brand:

            regx_intent_brand = re.compile(intent_brand, re.IGNORECASE)
            search_value[intent_brand_tag]=regx_intent_brand      
            
            if intentName=='ShowSavedShirts':
                previousBrand=''
            else:
                previousBrand=intent_brand
            
        if intent_price:

            regx_intent_price = float(intent_price)
            if intent_quantifier:
                previousQuantifier=intent_quantifier
                if re.search("great",intent_quantifier) is not None:
                    search_value[previousPriceUSD_tag]={"$gt": regx_intent_price}
                else:
                    search_value[previousPriceUSD_tag]={"$lt": regx_intent_price}
            else:
                search_value[intent_price_tag]=regx_intent_price      
            previousPrice=intent_price
        
        if intent_sale:
            search_value[intent_onSale_tag]=True 
            previousOnSale=intent_sale

    upc_list=[]
    if previousShirt:
        for upc in previousShirt.split(","):
            if upc=='StartOver':
                previousShirt=''
                break
            if upc.strip():
                upc_list.append(ObjectId(upc.strip()))
        if len(upc_list) >0:
            search_value[intent_upc_tag]={ '$nin': upc_list } #upc_list }
    
    if intent_upc:
        search_value[intent_upc_tag]=ObjectId(intent_upc)#intent_upc

    print (search_value)
    print (db_collection)

    #set collection to use
    db = connection[db_name][db_collection]

    all_results = db.find(search_value)

    result_count = all_results.count()
    button_text='next'
    button_value='next'
    button_remove_text=''
    button_remove_value=''

    if result_count > 0:
        print (result_count)
        if result_count == 1 and intentName!='ShowSavedShirts':
            button_text='>Start over<'
            button_value='next'
        elif intentName=='ShowSavedShirts':
            counter=0
            for shirt in savedShirts.split(","):
                if shirt.strip() and re.search("\*SKIP\*",shirt.strip()) is None:
                    counter=counter+1

            if counter >0: 
                #there are more shirts to check
                button_text='next in my list >>'
                button_value='what\'s on my list' 
                button_remove_text='[x]remove'
                button_remove_value='eliminate'
            else:
                #this was the last shirt
                button_text='>Check list again<'
                button_value='what\'s on my list'
                button_remove_text='[x]remove'
                button_remove_value='eliminate'
                savedShirts=savedShirts.replace("*SKIP*","")

            
        random_number=randint(0,result_count-1)
        print (random_number)
        #results = db.find(search_value)[random_number]
        results=all_results[random_number]

        print (results)

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
        
        flag=0
        
        for offer in results['upcMap']:
            thisPrice=currency_prefix+ str(locale.format("%d", float(offer['retailPrice']), grouping=True))+currency_suffix
            onSaleInfo=''
            if intent_sale or previousOnSale:
                onSaleInfo="\n(previous price:"+currency_prefix+ str(locale.format("%d", float(offer['originalPrice']), grouping=True))+currency_suffix+")"
            break
        for offer in results['upcMap']:
            if not regx_intent_color:
                regx_intent_color=offer['color']
                print ("default to this color")
            thisColor=offer['color']
            if (re.search(regx_intent_color, offer['color']) is not None):
                print ('INFO: printing previous shirt='+previousShirt)
                previousShirt=previousShirt+', '+str(results['_id'])
                #previousShirt.append(offer['upc'])
                thisColor=offer['color']
                map_color=''
                try:
                    print('INFO: This Color:'+thisColor)
                    print('INFO: Try in :')
                    print(results['colorwayPrimaryImages'])
                    print('INFO: End-of-multi-line-info')
                    map_color=results['colorwayPrimaryImages'][thisColor]
                    thisColorUrl=imageBaseUrl+map_color
                except KeyError:
                    print ('ALERT: Using default image shirt'+imageshirt)
                    thisColorUrl=imageshirt
                imageshirt=thisColorUrl
                break
        
    else:
        print ('No results')
        link2shirt='No results with those conditions'
        message2='I couldn\'t find any shirt , please try other search criteria :-o'
        fulfillmentState='Failed'
        thisPrice='T-shirt'
        titleText=''
        imageshirt=''
    
    connection.close()
    
    #Add marker to clear previous shirts if starting over
    if button_text=='>Start over<':
        previousShirt='StartOver,'+previousShirt

    #create json response
    data = {}
    leaf2 = {}
    leaf3 = {}
    
    if result_count > 0:
        
        previousShirtDetails=thisBrand+":"+thisColor

        leaf3['contentType'] = 'PlainText'

        leaf3['content'] = message2+onSaleInfo

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
                                              "subTitle":thisColor.lower(),
                                     "attachmentLinkUrl":link2shirt
                                            } 
                                           ] 
                                }
        
        #disable buttons if most or least expensive or only 1 shirt in result
        one_shirt_in_StartOver=False
        count_shirts_in_StartOver=0
        for shirt in previousShirt.split(","):
            if shirt.replace("StartOver","").strip() and re.search("StartOver",previousShirt) is not None:
                count_shirts_in_StartOver=count_shirts_in_StartOver+1
        if count_shirts_in_StartOver==1:
            one_shirt_in_StartOver=True

        if intentName != 'ShowMeMostExpensive' and intentName != 'ShowMeLeastExpensive' and not one_shirt_in_StartOver:
            if button_remove_text and savedShirts.count(",") >1:
                button_remove_value='eliminate '+previousShirt.replace(",", "").strip()
                leaf2['responseCard']['genericAttachments'][0]['buttons']=[ 
                                                                    {
                                                                     "text":button_remove_text,
                                                                    "value":button_remove_value
                                                                     },
                                                                     {
                                                                     "text":button_text,
                                                                    "value":button_value
                                                                     }
                                                                ]
            elif button_remove_text :
                button_remove_value='eliminate '+previousShirt.replace(",", "").strip()
                leaf2['responseCard']['genericAttachments'][0]['buttons']=[ 
                                                                    {
                                                                     "text":button_remove_text,
                                                                    "value":button_remove_value
                                                                     }
                                                                ]
            else:   
                leaf2['responseCard']['genericAttachments'][0]['buttons']=[ 
                                                                    {
                                                                     "text":button_text,
                                                                    "value":button_value
                                                                     }
                                                                  ]
       
        data['dialogAction'] = leaf2
            
        data['sessionAttributes']= {"previousColor": previousColor,
                                    "previousBrand": previousBrand,
                                    "previousSize": previousSize,
                                    "previousQuantifier": previousQuantifier,
                                    "previousPrice": previousPrice,
                                    "previousBrand": previousBrand,
                                    "previousStore": previousStore.replace("_shirts",""),
                                    "previousIntent":intentName,
                                    "previousShirt": previousShirt,
                                    "savedShirts": savedShirts,
                                    "previousShirtDetails": previousShirtDetails,
                                    "previousOnSale": previousOnSale


        }

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


def show_saved_shirts(event):
    #Keep last store used
    previousStore = try_ex(lambda: event['sessionAttributes']['previousStore'])
    if previousStore is None:
        previousStore=''
    data=show_me_shirts(event)
    data['sessionAttributes']['previousStore']=previousStore
    
    #Indicate position of shirt in list
    print ("INFO: Finding position")
    shirt_title=data['dialogAction']['message']['content']
    Store_Info=event['currentIntent']['slots']['Store_Info']
    Brand_Info=event['currentIntent']['slots']['Brand_Info']
    Color_Info=event['currentIntent']['slots']['Color_Info']
    Upc_Info  =event['currentIntent']['slots']['Upc_Info']
    saved_shirt=Store_Info+":"+Brand_Info+":"+Color_Info+":"+Upc_Info
    savedShirts=data['sessionAttributes']['savedShirts']

    counter=0
    shirt_position=''
    for shirt in savedShirts.split(","):
        counter=counter+1
        print ("INFO: Searching"+saved_shirt.strip())
        print ("INFO: Searching"+shirt.strip())
        if re.search(saved_shirt.strip(),shirt.strip()) is not None:
            shirt_position="#"+str(counter)+" of "+ str(savedShirts.count(","))
            break

    data['dialogAction']['message']['content']=shirt_position+'\n'+shirt_title
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
    if currentIntentName=='GetShirtInfo':
        data=show_me_shirts(event)
    elif currentIntentName=='ShowSavedShirts':
        data=show_saved_shirts(event)
    else:
        data=show_me_shirts(event)

    return data



