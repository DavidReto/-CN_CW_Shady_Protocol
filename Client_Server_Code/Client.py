import sys
import socket
import time
import json
import string
import random

IP = "127.0.0.1"
PORT = 12000
Adress = ("127.0.0.1", 12000)
N_Chr = 7
rand_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k = N_Chr))  
array_byte=[]
p_array=[]
cli = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
cli.settimeout(10000)
#cli.connect((IP,PORT))

def main():
   global Adress
   print("Creating Client sockeet.")
   print("Connecting to the SERVER...")
   print("Connection has been established with the SERVER")
   while True:
      x = input('Would you like to make a request? If yes enter "r" if you would like to close the client type "q" :')
      if x == "q":
        cli.timeout
        break
      elif x=="r": 
         x = input('Would you like to make a SEND or a AUTH request? Type "s" for SEND or "a" for AUTH :')
         if x == "s":
            r_type="SEND"
            x = input('What kind of method would you like to use? Type "g" for GET or "p" for POST:')
            if x=="g":
               r_method="GET"
               r_path = input('Type in your request path(ex.https://www.google.com) :')
               x = input('Type in your request parameters,if your request doesnt have any just leave it empty :')
               if len(x) != 0:
                  r_que_param= x
               else:
                  r_que_param=""
               r_body = "null"
            elif x=="p":
               r_method="POST"
               r_path = input('Type in your request path(ex.https://www.google.com) :')
               x = input("Type in your request body,if your request doesn't have any just leave it empty :")
               if len(x) != 0:
                  r_body= x
               else:
                  r_body=""
               r_que_param = "null"
            request = '{"id":"'+str(rand_id)+'", "type":"'+r_type+'", "body":{"method":"'+r_method+'", "path":"'+r_path+'", "queryParameters":{'+r_que_param+'}, "body":'+r_body+'}, "timeout":5}'
         elif x=="a":
            r_type="AUTH"
            r_token = input('Type in your Authentication token :')
            request = '{"id":"'+str(rand_id)+'", "type":"'+r_type+'", "body":{"token":"'+r_token+'"}}'
         bytes_req = bytes(request, 'utf-8')
         pack_num = (sys.getsizeof(bytes_req)/1024)
         split(bytes_req,pack_num,Adress)
         print("The request was sent to the server")
         json_data=restruckt()
         while True:
            print("Waiting for a response from the server....") 
            if json_data['status']==200:
               print(f"The following success message has been received: '{str(json_data)}'")
               break
            elif json_data['success']== False:
               print(f"Something went wrong, here is the message we got: '{str(json_data)}'")
               break
         
def split(bytes_req,pack_num,Adress):
   p_array=[]
   byte_syze = sys.getsizeof(bytes_req)
   if isinstance(pack_num, float)==True:
      pack_num=pack_num+1
      pack_num=int(pack_num)
   for i in range(0,pack_num):
      if len(bytes_req)>=1024:
         array_byte = bytes_req[:1024]
         bytes_req = bytes_req[1024:]
      else:
         array_byte = bytes_req[:len(bytes_req)]
         bytes_req = bytes_req[len(bytes_req):]
      array_byte=list(array_byte)
      p_array.append('{"id": "'+str(rand_id)+'", "packetNumber": '+str(i+1)+', "totalPackets": '+str(pack_num)+', "payloadData": '+str(array_byte)+' }')
   for i in range(0,len(p_array)):
      try :  
         cli.sendto(bytes(p_array[i],encoding="UTF-8"),Adress)
         time.sleep(0.02)
      except socket.timeout:
         print("Connection TimedOut, couldn't connect to the SERVER") 
      json_data=restruckt()
      if json_data['status']==201:
         print(f"The following ACK message has been received :'{str(json_data)}'")
      else:
         i =i-1

def restruckt():
   request_response = cli.recvfrom(5000)
   #string_data=request_response[0].decode("utf-8")
   json_data = json.loads(request_response[0])
   results = json_data['payloadData']
   if json_data['totalPackets']!=1:
      for i in range(1,(json_data['totalPackets'])):
            request_response = cli.recvfrom(9000)
            string_data=request_response[0].decode("UTF-8")
            json_data = json.loads(string_data)
            print(f"Amount of packets recieved{i}")
            restruckt_response=json_data['payloadData']
            results=results+restruckt_response
   string_data=''.join([chr(x) for x in results])
   print(string_data)
   return json.loads(string_data) 


main()

''' '''
