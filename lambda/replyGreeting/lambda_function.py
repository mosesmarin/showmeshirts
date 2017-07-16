# setParameter
# Author: Moises Marin
# Date: June 20, 2017
# Purpose: Reply greeting, set/clear/show filters
#
#

import json
import re
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

def reply_greeting(event):

    intentName=event['currentIntent']['name']
    #sessionAttributes={}
    sessionAttributes = event['sessionAttributes']
    
    if len(sessionAttributes) >=1:
        previousShirt = try_ex(lambda: event['sessionAttributes']['previousShirt'])
        if previousShirt is None:
            previousShirt=''
        if previousShirt:
            event['sessionAttributes']['previousShirt']=''
        
        savedShirts = try_ex(lambda: event['sessionAttributes']['savedShirts'])
        if savedShirts is None:
            savedShirts=''
        previousStore = try_ex(lambda: event['sessionAttributes']['previousStore'])
        if previousStore is None:
            previousStore=''
        
    else:
        previousShirt=''
        savedShirts=''
        previousStore=''


    if event['currentIntent']['name'] == 'HelpCommands':
        reply_message=('Say: show me shirts!\n\n'
                       '*My current stores: macys, nordstrom, zalando, decathlon, palacio*\n\n'
                       'Add a color, brand, price or store.\n'
                       'Say: show me green shirts by nike with price greater than 100 from macys\n'
                       '        show me shirts by puma from nordstrom\n'
                       '\n'
                       'Know your colors, brands and prices?\n'
                       'Say: give me brands/colors/prices [from store]\n'
                       '        show me expensive/inexpensive shirts [from store]\n'
                       '        show me the most expensive/least expensive shirt [from store]\n'
                       '\n'
                       'Do you like what you see?\n'
                       'Say: add shirt to my list | How big is my list? | Let\'s see my list\n'
                       '        Save my list | Load list\n\n'
                       'Something\'s not right? Say: reset\n')
                       
    elif event['currentIntent']['name'] == 'RemoveFromMyList':
        remove_flag=False
        Upc_Info = try_ex(lambda: event['currentIntent']['slots']['Upc_Info'])
        if Upc_Info is None:
            Upc_Info=''
        print ("INFO: Upc_Info="+Upc_Info)
        print ("INFO: savedShirts="+savedShirts)

        if  Upc_Info and savedShirts:
            for shirt in savedShirts.split(","):
                print ("INFO: shirt="+shirt)
                if re.search(Upc_Info,shirt) is not None:
                    print ("INFO: found="+Upc_Info+"--"+shirt)
                    print ("INFO: savedShirts (before replace)="+savedShirts)
                    savedShirts=savedShirts.replace(shirt+"," , "")
                    print ("INFO: savedShirts (after replace)="+savedShirts)
                    reply_message='You got it! I removed it from your list.'
                    remove_flag=True
                    break
        if not remove_flag or not Upc_Info :
            reply_message='Oops! I couldn\'t remove it.'
        
        if len(savedShirts)<2:
            savedShirts=''
         
            
    elif event['currentIntent']['name'] == 'ClearAll':
        attribute_values=''
        for attribute in sessionAttributes:
            if attribute != 'previousIntent' and attribute != 'savedShirts':
                if attribute!='previousShirtDetails':
                    if attribute=='previousOnSale':
                        if sessionAttributes[attribute]:
                            attribute_values=attribute_values+' '+'on sale'
                    else:
                        attribute_values=attribute_values+' '+sessionAttributes[attribute]
        if not attribute_values.strip():
            reply_message='You got it! No active filters.'
        else:
            reply_message='You got it! No active filters -- I have removed:'+attribute_values
        print (sessionAttributes)
        sessionAttributes={}
        print (sessionAttributes)


    elif event['currentIntent']['name'] == 'ClearColor':
        previousColor = try_ex(lambda: event['sessionAttributes']['previousColor'])
        if previousColor is None:
            previousColor=''
        else:
            event['sessionAttributes']['previousColor']=''
        attribute_values=''
        for attribute in sessionAttributes:
            if sessionAttributes[attribute]!='ShowMeAnother' and sessionAttributes[attribute]!='GetShirtInfo' and sessionAttributes[attribute]!='TellMeHowMany' and sessionAttributes[attribute]!='TellMePrices':
                attribute_values=attribute_values+' '+sessionAttributes[attribute]
        if not attribute_values.strip():
            if previousColor:
                reply_message='You got it! I removed '+previousColor+', no other active filter.'
            else:
                reply_message='You got it! No active filters.'
        else:
            reply_message='You got it! I removed '+previousColor+', active filters:'+attribute_values
        print (sessionAttributes)

    elif event['currentIntent']['name'] == 'ClearBrand':
        previousBrand = try_ex(lambda: event['sessionAttributes']['previousBrand'])
        if previousBrand is None:
            previousBrand=''
        else:
            event['sessionAttributes']['previousBrand']=''
        attribute_values=''
        for attribute in sessionAttributes:
            if sessionAttributes[attribute]!='ShowMeAnother' and sessionAttributes[attribute]!='GetShirtInfo' and sessionAttributes[attribute]!='TellMeHowMany' and sessionAttributes[attribute]!='TellMePrices':
                attribute_values=attribute_values+' '+sessionAttributes[attribute]
        if not attribute_values.strip():
            if previousBrand:
                reply_message='You got it! I removed '+previousBrand+', no other active filter.'
            else:
                reply_message='You got it! No active filters.'
        else:
            reply_message='You got it! I removed '+previousBrand+', active filters:'+attribute_values
        print (sessionAttributes)
        
    elif event['currentIntent']['name'] == 'ClearPrice':
        previousPrice = try_ex(lambda: event['sessionAttributes']['previousPrice'])
        if previousPrice is None:
            previousPrice=''
        else:
            event['sessionAttributes']['previousPrice']=''
        attribute_values=''
        for attribute in sessionAttributes:
            if sessionAttributes[attribute]!='ShowMeAnother' and sessionAttributes[attribute]!='GetShirtInfo' and sessionAttributes[attribute]!='TellMeHowMany' and sessionAttributes[attribute]!='TellMePrices':
                attribute_values=attribute_values+' '+sessionAttributes[attribute]
        if not attribute_values.strip():
            if previousPrice:
                reply_message='You got it! I removed '+previousPrice+', no other active filter.'
            else:
                reply_message='You got it! No active filters.'
        else:
            reply_message='You got it! I removed '+previousPrice+', active filters:'+attribute_values
        print (sessionAttributes)
        
    elif event['currentIntent']['name'] == 'ClearSize':
        previousSize = try_ex(lambda: event['sessionAttributes']['previousSize'])
        if previousSize is None:
            previousSize=''
        else:
            event['sessionAttributes']['previousSize']=''
        attribute_values=''
        for attribute in sessionAttributes:
            if sessionAttributes[attribute]!='ShowMeAnother' and sessionAttributes[attribute]!='GetShirtInfo' and sessionAttributes[attribute]!='TellMeHowMany' and sessionAttributes[attribute]!='TellMePrices':
                attribute_values=attribute_values+' '+sessionAttributes[attribute]
        if not attribute_values.strip():
            if previousSize:
                reply_message='You got it! I removed '+previousSize+', no other active filter.'
            else:
                reply_message='You got it! No active filters.'
        else:
            reply_message='You got it! I removed '+previousSize+', active filters:'+attribute_values
        print (sessionAttributes)
        
    elif event['currentIntent']['name'] == 'ShowFilters':
        attribute_values=''
        for attribute in sessionAttributes:
            if attribute != 'previousIntent' and attribute != 'savedShirts' and attribute!='previousShirtDetails':
                if attribute=='previousOnSale':
                    if sessionAttributes[attribute]:
                        attribute_values=attribute_values+' '+'on sale'
                else:
                    attribute_values=attribute_values+' '+sessionAttributes[attribute]
        if not attribute_values.strip():
            reply_message='No active filters'
        else:
            reply_message='Active filters:'+attribute_values
    
    else:
        reply_message='We\'ll hello there! I am ShowMeShirts bot and I LOVE to show shirts. \n\nI have shirts from different stores, ask me to show you shirts or try:\nshow me green shirts by nike from macys'
        
    data={}

    message={
      'contentType': 'PlainText',
      'content': reply_message
    }

    if previousShirt and event['currentIntent']['name'] != 'ClearAll':
        sessionAttributes['previousShirt']=previousShirt
    if savedShirts and event['currentIntent']['name'] != 'ClearAll':
        sessionAttributes['savedShirts']=savedShirts
    if event['currentIntent']['name'] == 'RemoveFromMyList':
        sessionAttributes['savedShirts']=savedShirts


    data={
        'sessionAttributes': sessionAttributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': 'Fulfilled',
            'message': message
   
            }
        }

    json_data = json.dumps(data)
    print (data)
    return data 


def save_shirt(event):
    print ("INFO: Saving shirt:")
    sessionAttributes=event['sessionAttributes']
    #Previous shirt is required
    if len(sessionAttributes) >=1:
        previousShirt = try_ex(lambda: event['sessionAttributes']['previousShirt'])
        if previousShirt is None:
            previousShirt=''
        if previousShirt:
            event['sessionAttributes']['previousShirt']=''
        savedShirts = try_ex(lambda: event['sessionAttributes']['savedShirts'])
        if savedShirts is None:
            savedShirts=''
        previousStore = try_ex(lambda: event['sessionAttributes']['previousStore'])
        if previousStore is None:
            previousStore=''
    else:
        previousShirt=''
        savedShirts=''
        previousStore=''
            
    if previousShirt:
        shirt_list=previousShirt.split(",")

        #add shirt if not present already
        if re.search(shirt_list[len(shirt_list)-1].strip(),savedShirts) is not None:
            print ("INFO: Shirt already in savedShirts, not adding")
            print (savedShirts)
            print (shirt_list[len(shirt_list)-1])
            print ("INFO: End-of-multi-line-comment")
            reply_message='That one\'s already in the list'
        else:
            if not previousStore:
                #previousStore='DEFAULT'
                previousStore=os.environ['db_default_collection'].replace("_shirts","")
                
            previousBrand = try_ex(lambda: event['sessionAttributes']['previousBrand'])
            if previousBrand is None:
                previousBrand=''
            
            previousColor = try_ex(lambda: event['sessionAttributes']['previousColor'])
            if previousColor is None:
                previousColor=''
                
            previousShirtDetails = try_ex(lambda: event['sessionAttributes']['previousShirtDetails'])
            if previousShirtDetails is None:
                previousShirtDetails=''
                
            if not savedShirts:
                savedShirts=previousStore+':'+previousShirtDetails+':'+shirt_list[len(shirt_list)-1].strip()+","
            else:
                savedShirts=savedShirts+ previousStore+':'+previousShirtDetails+':'+shirt_list[len(shirt_list)-1].strip()+","
                
            if savedShirts.count(",")==1:
                shirt_count="1 shirt."
            else:
                shirt_count=str(savedShirts.count(","))+" shirts."

            print ("INFO: savedShirts")
            print (savedShirts)
            print ("INFO: End-of-multi-line-comment")
            reply_message='Awesome! Your list now has '+shirt_count

    else:
        reply_message='Oops, I didn\'t get that shirt. Please continue checking some shirts!'

    data={}

    message={
      'contentType': 'PlainText',
      'content': reply_message
    }

    if previousShirt and event['currentIntent']['name'] != 'ClearAll':
        sessionAttributes['previousShirt']=previousShirt
    if savedShirts and event['currentIntent']['name'] != 'ClearAll':
        sessionAttributes['savedShirts']=savedShirts
    if event['currentIntent']['name'] == 'RemoveFromMyList':
        sessionAttributes['savedShirts']=savedShirts


    data={
        'sessionAttributes': sessionAttributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': 'Fulfilled',
            'message': message
   
            }
        }

    json_data = json.dumps(data)
    print (data)
    return data

def thank_you(event):
    print ("INFO: executing thank_you")
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
                                                               'content': 'It was my pleasure. Thanks for stopping by!'
                                                          }
                                    }
              }
    data['sessionAttributes']= sessionAttributes 

    print (data)
    json_data = json.dumps(data)
    print (json_data)
    return data

def good_bye(event):
    print ("INFO: executing good_bye")
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
                                                               'content': 'Bye-bye, enjoy the rest of your day!'
                                                          }
                                    }
              }
    data['sessionAttributes']= sessionAttributes 

    print (data)
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
    if currentIntentName=='SaveShirt':
        data=save_shirt(event)
    elif currentIntentName=='ThankYou':
        data=thank_you(event)
    elif currentIntentName=='GoodBye':
        data=good_bye(event)
    else:
        data=reply_greeting(event)

    return data

