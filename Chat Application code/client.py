import socket
import sys
import os
from multiprocessing import Process, Lock
host='127.0.0.1'
port =1250


username=input("Enter username -")
#host=input("server IP address -")

skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
skt.connect((host,port))
s1="REGISTER TOSEND "+username +"\n\n"
s2="REGISTER TORECV "+username +"\n\n"
skt.sendall((s1+s2).encode())

r1=(skt.recv(2048)).decode()
if (r1[0]=="R"):
    print(r1)

else:
    print(r1)
    skt.close()
    sys.exit()
                             # can put register fn and repeatedly call it but exiting to restart

'''
def register():
    username=input("Enter username -")
    host=input("server IP address -")
    s1="REGISTER TOSEND "+username +"\n\n"
    s2="REGISTER TORECV "+username +"\n\n"
    skt.send(s1.encode())
    skt.send(s2.encode())
    r1=skt.recv(2048).decode()
    if (r1[0]=="R"):
        print(r1)
        print(skt.recv(2048).decode())
        return (username,host)
    else:
        print(r1)
        return register()

(username,host)=register()'''
lock = Lock()

def send_msg(lck,st,fn):
    sys.stdin = os.fdopen(fn)
    while True:
        
        #read
        
        m=sys.stdin.readline().rstrip()
        
        if not m:
            continue
        #check msg format
        lck.acquire()
        try:
            #print(m+'some')
            l1=m.split()
            uname=l1[0][1:]
            msg=l1[1]
            
            
            if (len(l1)==2 and l1[0][0]==("@")):
                hd="SEND "+uname +"\nContent-length: "+str(len(msg))+"\n\n"+msg
            
                st.send(hd.encode())
                  
            else:
                
                print("Please type correct message line")
        except Exception as e:
            print("Please type correct message line")
        lck.release()
        

def receive_msg(lck,st):
    while True:
        msg=st.recv(2048).decode()
        
        if msg[0]=='S' :            #acknowledge SEND or ERROR to user
            print(msg)
        elif msg[0]=="E":
            print(msg)
        else:
            l1=msg.split("\n")
            l2=l1[0].split()
            u=l2[1]                         #check msg
            real_m=l1[3]
            req="Content-length: "+str(len(real_m))
            if (l1[1]!=req):
                m="ERROR 103 Header Incomplete\n\n"
                st.send(m.encode())
            else:
                m="RECEIVED "+u+"\n\n"
                st.send(m.encode())
                lck.acquire()
                print((u+" : "+real_m))
                lck.release()




try:
    fni = sys.stdin.fileno()
    p1=Process(target=send_msg, args=(lock, skt,fni))
    p1.start()
    p2=Process(target=receive_msg, args=(lock, skt))
    p2.start()
    p1.join()
    p2.join()
except Exception as e:
    print("Error :",e)


skt.close()



