import socket
import threading
import os ,shutil 
import random #for threads waiting time
import time #for threads waiting

class myThread():
    def __init__(self):
        self.isAdmin = False
        self.current_dir ="C:\\Users\\Taha\\Desktop\\client_dir"
        self.username = ''


admins = ["taha" , "mahdi" , "ali"]
password = ["1234" , "5678" , "9123"]
format = 'utf-8'
#isAdmin = False
entercommand = "\nEnter your command :"
txt_formats = ['txt','docx']
user_file = 'C:\\Users\\Taha\\Desktop\\username.txt'
pass_file = 'C:\\Users\\Taha\\Desktop\\passwords.txt'
allowed_dir = "C:\\Users\\Taha\\Desktop\\client_dir"
#root = 'C:\\Users\\Taha\\Desktop'
report_file = 'C:\\Users\\Taha\\Desktop\\report_file.txt'
#current_dir = allowed_dir
# username=''

def send_msg(client,msg):
    
    client.send(msg.encode(format))
    client.recv(1)

def recv_msg(client):
    
    server_msg =client.recv(1024).decode(format)
    client.send(b'A')
    return server_msg

def user_auth (msg):
    if msg in admins:
        return True
    else: 
        return False


def pass_auth (msg) :
   if msg in password :
      return True
   else :
      return False

def absolute_path(thread,path):
    
    

    if '../' in path:

        path = path.replace('../','')  
        path2 = os.path.abspath(os.path.join(thread.current_dir, os.pardir))
        path = os.path.join(path2,path)                                                                                    
        return path

    elif './' in path :

        path = path.replace('./','')    
        path = os.path.join(thread.current_dir,path)
        return path
     
    else :
        return path
    
  


def handle_signup(client):

    send_msg(client,'Enter Username: ')
    msg = client.recv (1024).decode('utf-8')
    file = open(user_file,'a+')
    file.seek(0)
    lines = file.read()
    if msg not in lines:
        file.write(f"{msg}\n")
        file.close()
        file = open(pass_file,'a')
        send_msg(client,'Enter Password: ')
        msg = client.recv (1024).decode('utf-8')
        file.write(f"{msg}\n")
        file.close()
        send_msg(client,'list:200 signing up successfully compeleted.')
        
    else :
        send_msg(client,'list:400 user is in use!')
        handle_signup(client)


def check_user_pass_exist(msg_user,msg_pass):

    user = open(user_file)
    password = open(pass_file)
    users = user.read()
    passwords = password.read()
    users = users.split('\n')
    passwords = passwords.split('\n')
    
    for i in range(len(users)):
        
        if msg_user == users[i]:
            
            if msg_pass == passwords[i]:

                # send_msg(client,'list:200 Loging in successfully compeleted!')
                return True
            else:
                send_msg(client,'list:400 invalid password !')
                return False
    send_msg(client,'list:400 invalid username !')
    return False    
      

def isAllowed_Path(path,thread):
    # global isAdmin
    
    #abs_path =os.path.abspath(path)
    abs_path = absolute_path(thread,path)
    if not thread.isAdmin:
        if allowed_dir in abs_path :
            return True
        else :
            False
    else :
        return True
    

def handle_l_or_s(l_or_s,client,addr , thread):
    if l_or_s == 's':
        handle_signup(client)
        auth = authentication(client,thread)
        return auth
    elif l_or_s == 'l':
        auth = authentication(client,thread)
        return auth
    else:
        send_msg(client,'list:400 Invalid Command!')
        handle_client(client,addr)
        

def authentication(client ,thread ) :

    # global isAdmin,username

    send_msg(client ,'Entry...\nEnter User:' ) 
    msg1 = client.recv (1024).decode('utf-8')
    msg1 = msg1.replace('user ','')
    send_msg(client ,'Enter Password:' ) 
    msg2 = client.recv (1024).decode('utf-8')
    msg2 = msg2.replace('pass ' , '')


    if user_auth(msg1): # check if is admin

        if pass_auth(msg2):

            thread.username = msg1
            thread.isAdmin = True   #.....
            print(f"[NEW CONNECTION] {addr} ")
            send_msg(client,"200 You are authenticated successfully!\nEnter your commands : ")
            return True
        
        else:

            send_msg(client,'list:400 invalid info')
            authentication(client,thread)

    else: # if is not admin but has registered

        result = check_user_pass_exist(msg1,msg2)

        if result :
                thread.username = msg1
                print(f"[NEW CONNECTION] {addr} ")
                send_msg(client,"200 You are authenticated successfully!\nEnter your commands : ")
                return True
        else:
            authentication(client,thread)


def folder_info (client,path,thread,*isFile) :
        
        global txt_formats #current_dir
        isallowed = isAllowed_Path(path,thread)
        # path = os.path.abspath(path)
        if not isFile :
            if isallowed:
                
                thread.current_dir = path
                file_list = os.listdir(path)

                for file_name in file_list :
                    file_path = os.path.join(path,file_name)
                    file_size = os.path.getsize(file_path)
                    ti_c = os.path.getctime(file_path)
                    file_creation_date = time.ctime(ti_c)
                    msg = f'list: {file_creation_date}  {file_size}  {file_name}\n'
                    send_msg(client,msg)

            else :
                send_msg(client,"list:400 You can`t access this directory")
        else :
            if isAllowed_Path(path,thread):
                thread.current_dir = os.path.dirname(path)
                file_name = os.path.basename(path)
                file_name = file_name.split('.')

                if file_name[1] not in txt_formats:
                    send_msg(client,'list:400 file format is not valid!')
                    return 
                
                file = open(path)
                content = file.readlines()
                
                for line in content :
                
                    line='list: '+line.replace('\n','')
                    send_msg(client,line)      
                    
                file.close()
            else:
                send_msg(client,"list:400 You can`t access this directory")

        report =f'{thread.username} list : {path}  status: {isallowed}'
        write_report(report)


def handle_list(command,thread) :
    # global current_dir

    if not command =='list' :
        path = command.replace('list ','')

    if command =='list' :
        
        folder_info(client,thread.current_dir,thread)
        
    else :
        isFile = os.path.isfile(path)
        if not isFile :
            folder_info(client,path,thread)
        else :
           
           folder_info(client,path,thread,True)    



def handle_retr(client,command,thread) :
    # global username , current_dir
    
    path = command.replace('retr ','')
    
    if os.path.exists(path): 

        isallowed = isAllowed_Path(path,thread)

        if isallowed:

            thread.current_dir = os.path.dirname(path)

            username =f'retr:USERNAME:{thread.username}'
            send_msg(client,username)
            file = open(path,'br')
            file_name = os.path.basename(path)  #retrieve file name with format
            extension =file_name.split('.')
            file_name = 'retr:FILE_NAME:' + file_name
            send_msg(client,file_name)
            file_ext = extension[1].lower()

            if not file_ext in txt_formats:
                send_msg(client,'retr:B')
            else :
                send_msg(client,'retr:NB')

            content = file.readlines()
            for line in content :
                client.sendall(line)
                client.recv(1)
            
            send_msg(client,'retr:EOF')

        else :
            send_msg(client,"list:400 You can`t access this file.")


        report =f'{thread.username} retr : {path}  status: {isallowed}'
        write_report(report)

    else :
        send_msg(client,'list:400 path not found!')
        report =f'{thread.username} retr : {path}  status:"Path Not found"'
        write_report(report)




def handle_dele (client,command,thread):
    # global current_dir

    path = command.replace('dele ','')
    send_msg(client,'Do you really wish to delete? Y/N: ')
    answer = client.recv(1024).decode(format)

    if answer =='y':

        if os.path.isfile(path):
         
            isallowed = isAllowed_Path(path,thread)

            if isallowed:

                thread.current_dir = os.path.dirname(path)
                os.remove(path)
                send_msg(client,'list:200 file successfully deleted! ')
                
            else :
                send_msg(client,'list:400 You can`t access this directory!')

            report =f'{thread.username} dele : {path}  status: {isallowed}'
            write_report(report)
        
        else :
            send_msg(client,'list:400 The path is not pointing to a file!')

            report =f'{thread.username} dele : {path}  status:"File Not Found."'
            write_report(report) 

       
    else :
        report =f'{thread.username} dele : {path}  status:"Canceled."'
        write_report(report) 



def handle_mkd (client,command,thread) :
    # global current_dir
    path = command.replace('mkd ','')
    path = absolute_path(thread,path)

    if path:    
        if isAllowed_Path(path,thread):

            abs_path = os.path.abspath(path)      
            thread.current_dir = os.path.abspath(os.path.join(abs_path, os.pardir)) #retrive parent dir

            if not os.path.exists(abs_path):

                os.makedirs(abs_path)
                send_msg(client,'list:200 directory successfully created!')
                report =f'{thread.username} mkd : {path}  status:"File created."'

            else :
                send_msg(client,'list:400 File already exists!')
                report =f'{thread.username} mkd : {path}  status:"File already exists."'
        else:
            send_msg(client,'400 You can`t access this path.')   
            report =f'{thread.username} mkd : {path}  status:"False"'          
    else :
        send_msg(client,'list:400 Wrong Command!')
        report = f'{thread.username} mkd : {path}  status:"Wrong command."'

    write_report(report)    

def handle_rmd(client,command,thread):
    # global current_dir

    path = command.replace('rmd ','')
    path = absolute_path(thread,path)

    if path :
        if isAllowed_Path(path,thread):
            abs_path = os.path.abspath(path)
            if not abs_path == allowed_dir:

                if  os.path.exists(abs_path):
                    if os.path.isdir(abs_path):

                        thread.current_dir = os.path.abspath(os.path.join(abs_path, os.pardir))

                        listdir = os.listdir(abs_path)

                        if len(listdir) == 0 :
                            os.rmdir(abs_path)
                            send_msg(client,'list:200 successfully deleted !')  

                        else :
                            shutil.rmtree(abs_path)
                            send_msg(client,'list:200 successfully deleted !')  

                        report = f'{thread.username} rmd : {path}  status:"True"'
                    else :
                        send_msg(client,'list:400 the path is not pointing to a directory!')
                        report = f'{thread.username} rmd : {path}  status:"Directory not found."'
                else :
                        send_msg(client,'list:400 Cannot remove a directory when that directory doesn`t exists!') 
                        report = f'{thread.username} rmd : {path}  status:"Directory not found."'
            else :
                send_msg(client,'list:400 You can`t remove main client directory') 
                report = f'{thread.username} rmd : {path}  status:"can`t delete client directory."'
        else :
            send_msg(client,'list:400 You can`t access this directory!')
            report = f'{thread.username} rmd : {path}  status:"False"'
           

    else :
        send_msg(client,'list:400 Wrong Command!')
        report = f'{thread.username} rmd : {path}  status:"Wrong command."'
        
    write_report(report)

def handle_stor(client,command,thread):

    #global isAdmin , current_dir

    if 'stor:FILE_NAME:' in command:
        file_name = command.replace('stor:FILE_NAME:','')
        client.sendall(b'A')
        file_name = os.path.join(thread.current_dir,file_name)

        if os.path.exists(file_name):
            os.remove(file_name)
            
        server_msg = recv_msg(client)

        if 'NB' in server_msg:
             
            while not server_msg =='stor:EOF':
                server_msg = client.recv(1024).decode(format)
                server_msg.replace('\n','')
                client.sendall(b'A')
                if server_msg =='stor:EOF':
                     break
                file = open(file_name,"a")
                file.write(server_msg)
                file.close()
        
        elif 'B' in server_msg :
                    while  not server_msg ==b'stor:EOF':
                        server_msg = client.recv(1024)
                        client.sendall(b'A')
                        if server_msg == b'stor:EOF':
                            break
                        file = open(file_name,"ab")
                        file.write(server_msg)
                        file.close()

        report = f'{thread.username} stor : {command}  status:"True"'
        write_report(report)


def handle_pwd(client,thread):
    # global current_dir
    send_msg(client,f'list:{thread.current_dir}')
    report = f'{thread.username} pwd status:"True."'
    write_report(report)


def handle_cwd(client , command,thread):
    

    path = command.replace('cwd ','')
    #path = os.path.abspath(path)
    path = absolute_path(thread,path)

    if isAllowed_Path(path,thread) and path:

        if os.path.isdir(path):

            # if path == root: #for admins...

            #     send_msg(client,'list:400 You can`t quit root!')
            #     report = f'{thread.username} cwd : {path}  status:"Can`t quit root."'
            #     write_report(report)
            # else:

                thread.current_dir = path
                send_msg(client,f'list:200 current directory successfully changed!\ncurrent directory is :{thread.current_dir}')

                report = f'{thread.username} cwd : {path}  status:"True"'
                write_report(report)
        else :

            send_msg(client,'list:400 invalid directory!')
            report = f'{thread.username} cwd : {path}  status:"Invalid directory."'
            write_report(report)
    else :
            
            send_msg(client,'list:400 You can`t access this directory!')
            report = f'{thread.username} cwd : {path}  status:"False"'
            write_report(report)


def handle_cdup(client,thread):
    #global root
    
    path = os.path.abspath(os.path.join(thread.current_dir, os.pardir))

    if  isAllowed_Path(path,thread) :
        # if thread.current_dir == root:
        #     send_msg(client,'list:400 You can`t quit root!')
        #     report = f'{thread.username} cdup : {path}  status:"Can`t quit root"'
        # else :
            thread.current_dir = path
            send_msg(client,f'list:200 directory successfully changed!\ncurrent directory is :{thread.current_dir}')
            report = f'{thread.username} cdup : {path}  status:"True"'
    else :
        send_msg(client , 'list:400 You can`t access this directory!')
        report = f'{thread.username} cdup : {path}  status:"False"'
    
    
    write_report(report)

def handle_report(client , thread):

    if thread.isAdmin:
        file = open(report_file,'r')
        content = file.readlines()
        for line in content:
            line = line.replace('\n','')
            send_msg(client,f'list:{line}')
    else :
        send_msg(client,'list:400 You don`t have permission!')


def write_report(report):
    try:
        file = open(report_file,'a')
        file.write(report+'\n')
        file.close()

    except:
        rand_num = random.randint(1,10)
        time.sleep(rand_num)
        write_report(report)


def handle_client(client,addr):
   thread = myThread()
   send_msg(client,"Enter login or Signup l/s: ")
   l_or_s = client.recv (1024).decode('utf-8')
   auth = handle_l_or_s(l_or_s,client,addr , thread)
   report = f'{thread.username} logged in'
   write_report(report)
   
   while auth : 
      
     
      command = client.recv(1024).decode(format)

      if command == "quit" :
        send_msg(client,'fin')
        print(f"[CONNECTIO CLOSED] {addr}")
        report = f'{thread.username} quit  status:"True"' 
        write_report(report)
        continue
        
      elif 'list' in command :
         handle_list(command,thread)
      elif  'retr' in command :
          handle_retr(client,command,thread) 
      elif 'stor' in command :
          handle_stor(client,command,thread)
      elif 'dele' in command :
          handle_dele(client,command,thread)###
      elif 'mkd' in command :
          handle_mkd(client,command,thread)
      elif 'rmd' in command :
          handle_rmd(client,command,thread)
      elif 'pwd' in command :
          handle_pwd(client,thread)
      elif 'cwd' in command :
          handle_cwd(client,command,thread)
      elif 'cdup' in command :
          handle_cdup(client,thread)
      elif 'report' in command :
          handle_report(client,thread)

      send_msg(client,entercommand)


host = 'localhost'
port = 8080
addr =(host,port)
server_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)

server_socket.bind(addr)

server_socket.listen(5)

print(f"SERVER LISTENING ON {addr[1]} ...")           

while True:
    client , addr = server_socket.accept()
    thread = threading.Thread(target= handle_client , args=(client,addr ))
    thread.start()
   
    




