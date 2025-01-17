# The client is a single-threaded app, which has three states
import socket
import struct
import threading
import os
os.system("")
from keyBoard import Keyboard


class Client:
    # client configuration #                     
    SERVER_PORT = 13117                     
    client_connection_list = []
    tcp_buffer = 4096
    buffer = 16
    is_thread_terminated = False 

    def __init__(self,teamName):
        """
        :param 
        :return
        """
        self.TEAM_NAME = teamName + '\n'
        # UDP
        self.client_socket_udf = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
        self.client_socket_udf.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #  Enable broadcasting mode
        self.client_socket_udf.bind(("", Client.SERVER_PORT))
        # TCP
        self.conn_tcp = None
        self.serverIP = None
        self.serverTcpPort = None
    
    def wait_for_server_offer(self):
        """
        This function wait to get connections offer from server
        leave this state when you get an offer message and start communicate via tcp connection
        :param 
        :return
        """
        data, addr = self.client_socket_udf.recvfrom(Client.buffer)
        cookie, msg_type, tcp_port_number = struct.unpack('IBH', data)
        self.serverIP = addr[0]
        self.serverTcpPort = int(tcp_port_number)
        if cookie == 0xfeedbeef and msg_type == 0x2 and tcp_port_number > 0:
            print(f"Received offer from {addr[0]}, attempting to connect...")
            data_press_thread = threading.Thread(target=self.on_press,name='TCP client')
            self.execute_tcp_connection(data_press_thread)
              
    def execute_tcp_connection(self,data_press_thread):
        """
        This function execute tcp connection between the client and server
        :param 
        :return
        """
        Client.is_thread_terminated = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            self.conn_tcp = client_socket
            Client.client_connection_list.append(client_socket)
            try:
                client_socket.connect((self.serverIP, self.serverTcpPort))
            except:
                print("Connection failed")
                self.reset_client()
            try:    
                client_socket.sendto(self.TEAM_NAME.encode('utf-8'),(self.serverIP, self.serverTcpPort))
            except:
                print("Attempt to send data failed")
                self.reset_client()

            # welcome message
            try: 
                data_from_server = client_socket.recv(Client.tcp_buffer)
                print(data_from_server.decode('utf-8'))
            except:
                print("Server disconnected, listening for offer requests...")
                self.reset_client()
            # after the welcome message the game is starting    
            data_press_thread.start()

            # game over massage
            try:  
                data_from_server = client_socket.recv(Client.tcp_buffer)
                print(data_from_server.decode('utf-8'))
            except:
                print("Server disconnected, listening for offer requests...")
                data_press_thread.join()
                self.reset_client()
            Client.is_thread_terminated = True
            data_press_thread.join()
            
        
        print("Server disconnected, listening for offer requests...")
        self.reset_client()

    def on_press(self):
        """
        This function get what is the client keyboard press
        Accepts each character individually
        :param 
        :return
        """
        keyBoard = Keyboard()
        while True:
            if  Client.is_thread_terminated:
                break
            try:
                if keyBoard.is_press():
                    try:
                        self.conn_tcp.sendto(str(keyBoard.get_char).encode('utf-8'),(self.serverIP, self.serverTcpPort))         
                    except:
                        print(f"Server closed socket - {self.conn_tcp}")
                        break
            except:
                break
       
    def reset_client(self): 
        """
        This function restart the connection list of clients
        :param 
        :return
        """
        Client.client_connection_list.clear()
        self.wait_for_server_offer()
        


if __name__ == "__main__":
    print("Client started, listening for offer request...")
    client = Client('Rotem&Dana')
    

    client.wait_for_server_offer()
    
    


