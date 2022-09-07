import requests
from variables import credentials

# ALL CODE HERE HAS NOT BEEN TESTED !! DO NOT USE

#not tested
def  cancelOrder(orderId): 
    return requests.delete('https://api.tdameritrade.com/v1/accounts/' + credentials.accountId + '/orders/' + orderId,
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()
   
#not tested   
def getOrder(orderId):  
    return requests.get('https://api.tdameritrade.com/v1/accounts/' + credentials.accountId + '/orders/' + orderId,
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()  

#not tested   
def getOrdersByPath(maxResults, fromEnteredTime, toEnteredTime, status):  # FIX
    return requests.get('https://api.tdameritrade.com/v1/accounts/' + credentials.accountId + '/orders/',
                        params={'maxResults': maxResults, 'fromEnteredTime': fromEnteredTime, 'toEnteredTime': toEnteredTime, 'status': status},
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json() 

#not tested   
def getOrdersByQuery(accountId, maxResults, fromEnteredTime, toEnteredTime, status):  # FIX
    return requests.get('https://api.tdameritrade.com/v1/orders/',
                        params={'accountId': accountId, 'maxResults': maxResults, 'fromEnteredTime': fromEnteredTime, 'toEnteredTime': toEnteredTime, 'status': status},
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json() 

#not tested   
def placeOrder(post):  # FIX
    return requests.post('https://api.tdameritrade.com/v1/accounts/' + credentials.accountId + '/orders/',
                        params=post,
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json() 

#not tested   
def replaceOrder(put):  # FIX
    return requests.put('https://api.tdameritrade.com/v1/accounts/' + credentials.accountId + '/orders/' + orderId,
                        params=put,
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json() 

#not tested   
def createSavedOrder(post):  # FIX
    return requests.post('https://api.tdameritrade.com/v1/accounts/' + credentials.accountId + '/savedorders',
                        params=post,
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()                         
                                              
#not tested   
def deleteSavedOrder(savedOrderId):  
    return requests.delete('https://api.tdameritrade.com/v1/accounts/' + credentials.accountId + '/savedorders/' + savedOrderId,
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()     
                                                           
#not tested   
def getSavedOrder(savedOrderId):  
    return requests.get('https://api.tdameritrade.com/v1/accounts/' + credentials.accountId + '/savedorders/' + savedOrderId,
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()   

#not tested   
def getSavedOrdersByPath(): 
    return requests.get('https://api.tdameritrade.com/v1/accounts/' + credentials.accountId + '/savedorders/',
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()                      
                                   
#not tested   
def replaceSavedOrder(savedOrderId, put):  # FIX
    return requests.put('https://api.tdameritrade.com/v1/accounts/' + credentials.accountId + '/savedorders/' + savedOrderId,
                        params=put,
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()

#not tested   
def getAccount(fields): 
    return requests.get('https://api.tdameritrade.com/v1/accounts/' + credentials.accountId,
                        params={'fields': fields},
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()  

#not tested   
def getAccounts(fields): 
    return requests.get('https://api.tdameritrade.com/v1/accounts/',
                        params={'fields': fields},
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()  
                         
