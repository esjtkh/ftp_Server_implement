import socket
import os               

host ='localhost'
port= 8080
server_addr = (host , port)
format = 'utf-8'
file_path = ''
txt_formats = ['txt','docx']
username = ''
download_path= "C:\\Users\\Taha\\Desktop\\client_dir"
allowed_dir=f'C:\\Users\\Taha\\Desktop\\clients_downloads'


# def isAllowed_Path(path,isAdmin):
#     global allowed_dir

#     abs_path =os.path.abspath(path)
#     if not isAdmin =='true':
#         if download_path in abs_path :
#             return True
#         else :
#             False
#     else :
#         return True
    
def send_msg(client,msg):
    
    client.send(msg.encode(format))
    client.recv(1)

def user_downloads_folder(username,file_name):

    try:    #if user specefied folder exist:
         
         new_file = os.path.join(allowed_dir,username)
         new_file = os.path.join(new_file,file_name)
         file = open(new_file,'w')
         file.close()

    except :
         new_file = os.path.join(allowed_dir,username)
         os.makedirs(new_file)
         new_file = os.path.join(new_file,file_name)
         file = open(new_file,'w')
         file.close()
    
    return new_file

    


def handle_retr(server_msg):
       
       global file_path , username
        
       if 'retr:USERNAME:' in server_msg :
            username = server_msg.replace('retr:USERNAME:','')
       elif 'retr:FILE_NAME:' in server_msg :
            file_name = server_msg.replace('retr:FILE_NAME:','')
            #check specified folder existance:
            file_path = user_downloads_folder(username,file_name)

       elif server_msg == 'retr:B': # for non text files
            
            while not server_msg ==b'retr:EOF':
                server_msg = client.recv(1024)
                client.sendall(b'A')
                if server_msg == b'retr:EOF':
                     break
                file = open(file_path,"ab")
                file.write(server_msg)
                file.close()
            print('\n200 successfully file downloaded!')

       elif 'retr:NB':
            while not server_msg =='retr:EOF':
                server_msg = client.recv(1024).decode(format)
                server_msg = server_msg.replace('\n','')
                client.sendall(b'A')
                if server_msg =='retr:EOF':
                     break
                file = open(file_path,"a")
                file.write(server_msg)
                file.close()
            print('\n200 successfully file downloaded!')


def handle_stor(client,command):

        
               if 'stor ' in command :    
                    file_path = command.replace('stor ','')

               if os.path.exists(file_path): 
                         
                         file_name = os.path.basename(file_path)  #retrieve file name with format
                         file_name = 'stor:FILE_NAME:' + file_name
                         send_msg(client,file_name)
                         extension =file_name.split('.')
                         file_ext = extension[1].lower()
                              

                         if file_ext  in txt_formats:
                              send_msg(client,'NB')

                         else :
                              send_msg(client,'B')
                              
                         file = open(file_path,'br')
                         content = file.readlines()
                         for line in content :
                              client.sendall(line)
                              client.recv(1)
                         
                         send_msg(client,'stor:EOF')
                         print('200 successfully uploaded!')

               else:
                     send_msg(client , '400')
                     print('400 Directory not found')




client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

client.connect(server_addr)

while True :
        server_msg = client.recv(1024).decode(format) 
        
        client.sendall(b'A')
       
        if 'list:' in server_msg :
            server_msg = server_msg.replace('list:','')
            print(server_msg)  

        elif 'retr:' in server_msg :
           
           handle_retr(server_msg)
        
        elif server_msg == 'fin':
            print("200 Connection Closed!")
            break
                    
        else:

            answer = input(server_msg)
            if 'stor' not in answer:
               client.send(answer.encode(format))
            else :
                 handle_stor(client,answer)
     
