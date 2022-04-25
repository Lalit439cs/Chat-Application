import socket
from multiprocessing import Process, Lock,Value
import threading
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host='127.0.0.1'
port =1250
skt.bind((host,port)) 
# in place of host,empty string also for other computers on the network


dict_clients={}



def broadcast_help(sct,message,s):
    sct.send(message.encode())
    ack=(sct.recv(2048)).decode()
    if (ack[0]=="R"):
        s.value +=1

def broadcast(message,conn):
    global dict_clients        #implemented broadcasting with threads
    n= len(dict_clients)-1
    sm=Value('d', 0.0)
    processes=[]
    for cl in dict_clients :
        cc=dict_clients[cl]
        if ( cc != conn) :
            p=Process(target=broadcast_help,args=(cc,message,sm)) 
            processes.append(p)
            p.start()
    for pr in processes:
        pr.join()
    if (sm.value==float(n)):
        conn.send("SEND ALL\n\n".encode())
    else:
        conn.send("ERROR 102 Unable to send\n\n".encode())
			
lock=Lock()
def client_thread(client,adr):
    global dict_clients
    registered=False
    r=(client.recv(2048)).decode()
    er=True
    e_msg=""
    uname=""
    x=len(r)//2
    r1=r[:x]
    r2=r[x:]
    if (x>=15 and (r1[:15] == "REGISTER TOSEND" and r2[:15] =="REGISTER TORECV")):
        uname1=r1[16:-2]
        uname2=r2[16:-2]
        if ((uname1.isalnum() and uname2.isalnum()) and (uname1 == uname2 ) ):
            uname=uname1
            er=False
            e_msg=uname+" REGISTERED FULLY\n"
            client.sendall(("REGISTERED TOSEND "+uname +"\n\n"+"REGISTERED TORECV "+uname +"\n\n").encode())
        else:
            e_msg="ERROR 100 Malformed username\n\n"
            client.send(e_msg.encode())
            er=True

    else:
        e_msg="ERROR 101 No user registered\n\n"
        client.send(e_msg.encode())
        er=True
    lock.acquire()
    print(e_msg,adr)
    lock.release()
    if (not er):
        dict_clients[uname]=client


        while True:
            msg = (client.recv(2048)).decode()
            e=False
            me=''
            ack=''
            if (msg[0]=='S'):
                # for broadcasting msg
                idx=msg.index("\n")
                bcast=msg[idx:]
                #check msg
                l1=msg.split("\n")
                
                l2=l1[0].split()
                u=l2[1]
                real_m=l1[3]
                req="Content-length: "+str(len(real_m))
                if (l1[1]!=req):
                    me="ERROR 103 Header Incomplete\n\n"
                    e=True
                mg="FORWARD "+uname+bcast
                if (u!='ALL'):
                    #print(dict_clients)
                    if u in dict_clients:
                        st=dict_clients[u]
                        st.send(mg.encode())
                        #time.sleep(0.5)
                        ack=st.recv(2048).decode()  #doubt as near
                        
                        if (e and ack==me):
                            client.send(ack)     #closing client connection due to ERROR 103
                            del[dict_clients[uname]]
                            break
                        elif (ack==me):
                            client.send(ack)         #Piazza Iteration 4 point
                            del[dict_clients[u]]
                        else:
                            client.send(("SEND "+u+"\n\n").encode())
                                             
                    else:
                        me="ERROR 102 Unable to send\n\n"
                        client.send(me.encode())
                        e=True
                else:
                    broadcast(mg,client)
    client.close()


skt.listen(5)

while (True):
    cnct,addr = skt.accept()
    threading.Thread(target=client_thread,args= (cnct,addr)).start()
    
        
skt.close()
