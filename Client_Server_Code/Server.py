import io
import time
import json
import socket
import http.client
import http.server
import threading
import sys
import requests
from urllib import request,response
from multiprocessing import connection
from threading import Thread
import re
import html
import math

IP= "127.0.0.1"
PORT=12000
extoken="extoken"
ProxServer = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
ProxServer.settimeout(5000)
req_cont = 10
global authent
authent = {}
global lives
lives = {}

def main():
    global lives
    global authent
    queue = []
    print("Creating socket")
    ProxServer.bind((IP,PORT))
    while True:
        print("Waiting for the Client")
        json_data,cli_data=restruckt()
##############################Lives########################################################
        if len(lives) == 0:
            lives = {cli_data: 9}
            authent = {cli_data:False}
            print(f"The following client has: {lives[cli_data]} lifes")
        elif cli_data in lives:
            if authent[cli_data] == False:
                lives[cli_data] = lives[cli_data]-1
                print(f"The following client has: {lives[cli_data]} lifes")
            elif authent[cli_data] == True:
                lives[cli_data] = None
                print(f"The following client has: null lifes")
        else:
            lives[cli_data] = 9
            print(f"The following client has: {lives[cli_data]} lifes")
##############################################################################################
        string_data=json.dumps(json_data)
        queue.append(string_data)
        print(f"The following JSON has been received{string_data}")
        print("Converting it to JSON now...")
        #ACK response
        ack_response = json.dumps({ "id": json_data['id'], "status": 201,  "payload": { "content": { "queue": str(len(queue)), "message": "Your message has been received" } } })
        print("Sending the ACK response to the client")
        bytes_req = ack_response
        pack_num = (sys.getsizeof(bytes_req)/1024)
        split(bytes_req,pack_num,cli_data,json_data)
        while len(queue)>0:
            json_data = json.loads(queue[0])
            #Request identification
            if json_data['type']=="SEND":
                if lives[cli_data]==None or lives[cli_data] > 0:
                    if json_data['body']['method']=="GET":
                        try:
                            x = requests.get(json_data['body']['path'],timeout=json_data['timeout'])
                            if x.status_code==200:
                                response = json.dumps({ "id": json_data['id'], "status": 200, "success": True,  "payload": { "content": { "response": {"data": x.text , "headers": str(x.headers), "status": x.status_code},"requests":lives[cli_data] ,} } })
                            elif x.status_code==400 or x.status_code==405 or x.status_code==404:
                                response = json.dumps({ "id":json_data['id'], "status": 400, "success": False,  "payload": { "content": { "error": "BAD_REQUEST", "message": "You have made a bad request" } } })
                        except KeyError as e:
                            response = json.dumps({ "id":json_data['id'], "status": 400, "success": False,  "payload": { "content": { "error": "BAD_REQUEST", "message": "You have made a bad request" } } })
                        except requests.exceptions.MissingSchema as e:
                            response = json.dumps({ "id":json_data['id'], "status": 405, "success": False,  "payload": { "content": { "error": "INTERNAL_SERVER_ERROR", "message": "There was a problem when processing your request."} } })
                        except requests.exceptions.InvalidURL:
                            response = json.dumps({ "id":json_data['id'], "status": 405, "success": False,  "payload": { "content": { "error": "INTERNAL_SERVER_ERROR", "message": "There was a problem when processing your request."} } })
                        except requests.exceptions.Timeout:
                            response = json.dumps({ "id":json_data['id'], "status": 408, "success": False,  "payload": { "content": { "error": "TIMEOUT_ERROR", "message": "Your request has timed out"} } })
                        
                    elif json_data['body']['method']=="POST":
                        try:
                            x = requests.post(json_data['body']['path'])
                            if x.status_code==200:
                                response = json.dumps({ "id":json_data['id'], "status": 200, "success": True,  "payload": { "content": { "response": {"data":x.text, "headers":str(x.headers), "status":str(x.status_code)} } } })
                                
                            elif x.status_code==400 or x.status_code==405 or x.status_code==404:
                                response = json.dumps({ "id":json_data['id'], "status": 400, "success": False,  "payload": { "content": { "error": "BAD_REQUEST", "message": "You have made a bad request" } } })
                        except KeyError as e:
                            response = json.dumps({ "id":json_data['id'], "status": 400, "success": False,  "payload": { "content": { "error": "BAD_REQUEST", "message": "You have made a bad request" } } })
                        except requests.exceptions.Timeout:
                            response = json.dumps({ "id":json_data['id'], "status": 408, "success": False,  "payload": { "content": { "error": "TIMEOUT_ERROR", "message": "Your request has timed out"} } })
                        except requests.exceptions.InvalidURL:
                            response = json.dumps({ "id":json_data['id'], "status": 405, "success": False,  "payload": { "content": { "error": "INTERNAL_SERVER_ERROR", "message": "There was a problem when processing your request."} } })
                        except requests.exceptions.MissingSchema:
                            response = json.dumps({ "id":json_data['id'], "status": 405, "success": False,  "payload": { "content": { "error": "INTERNAL_SERVER_ERROR", "message": "There was a problem when processing your request."} } })
                    else :
                        response = json.dumps({ "id":json_data['id'], "status": 400, "success": False,  "payload": { "content": { "error": "BAD_REQUEST", "message": "You have made a bad request" } } })
                else:
                    response = json.dumps({ "id":json_data['id'], "status": 403, "success": False, "payload": { "content": { "error": "UNAUTHORISED_REQUEST", "message": "You have reached your request limit, authenticate to request more" } } })

            elif json_data['type']=="AUTH":
                try:
                    if json_data['body']['token']==extoken:
                        response = json.dumps({ "id":json_data['id'], "status": 200, "success": True, "body": { "content": { "message": "You have authenticated successfully" } } })
                        if len(authent) == 0:
                            authent = {cli_data:True}
                        else:
                            authent[cli_data] = True
                    elif json_data['body']['token']!=extoken:
                        response = json.dumps({ "id":json_data['id'], "status": 401, "success": False, "payload": { "content": { "error": "UNAUTHORISED_TOKEN", "message": "Could not authenticate using your authentication token" } } })
                        if len(authent) == 0:
                            authent = {cli_data:False}
                        else:
                            authent[cli_data] = False
                except KeyError as e:
                    response = json.dumps({ "id":json_data['id'], "status": 400, "success": False,  "payload": { "content": { "error": "BAD_REQUEST", "message": "You have made a bad request" } } })
            
            bytes_req = response
            pack_num = (sys.getsizeof(bytes_req)/1024)
            print(sys.getsizeof(bytes_req))
            split(bytes_req,pack_num,cli_data,json_data)
            print("Sending response to client")
            queue.pop(0)


def split(bytes_req,pack_num,Adress,json_data):
   p_array=[]
   byte_syze = sys.getsizeof(bytes_req)
   if isinstance(pack_num, float)==True:
      pack_num=pack_num+1
      pack_num=math.ceil(len(bytes_req)/1024)
   for i in range(0,pack_num):
      if len(bytes_req)>=1024:
         array_byte = bytes_req[:1024]
         bytes_req = bytes_req[1024:]
      else:
         array_byte = bytes_req[:len(bytes_req)]
         bytes_req = bytes_req[len(bytes_req):]
      array_byte=list(array_byte)
      p_array.append(json.dumps({"id": json_data['id'], "packetNumber": i+1, "totalPackets": pack_num, "payloadData": [ord(x) for x in array_byte] }))
   for i in range(0,len(p_array)):
      try : 
         ProxServer.sendto(bytes(p_array[i],encoding="UTF-8"),Adress)
         time.sleep(0.02)
      except socket.timeout:
         print("Connection TimedOut, couldn't connect to the SERVER") 

     

def restruckt():
    try:
        request_response = ProxServer.recvfrom(9000)
        string_data=request_response[0].decode("utf-8")
        json_data = json.loads(string_data)
        results = [int(i) for i in json_data['payloadData']]
        if json_data['totalPackets']!=1:
            for i in range(1,(json_data['totalPackets'])-1):
                request_response = ProxServer.recvfrom(9000)
                string_data=request_response[0].decode("UTF-8")
                json_data = json.loads(string_data)
                restruckt_response=[int(i) for i in json_data['payloadData']]
                results=results+restruckt_response+'}'
        string_data=bytes(results).decode('utf-8')
        return json.loads(string_data),request_response[1]
    except Exception as e:
        print(str(e))
         


main()

#else : response = '{ "id":"'+json_data['id']+'", "status": 403, "success": false, "content": { "error": "UNAUTHORISED_REQUEST", "message": "You have reached your request limit" } } '
