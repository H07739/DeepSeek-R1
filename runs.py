from DeepSeek import *
from colorama import Fore, init

id = None
in_code_block = False
while True:
    p = input('Enter Message : ')
    for message in sendMessage(prompt=p, message_id=id):
        id = message['id']
        msg_content = message['message']

        if '```' in msg_content:
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            
            print(Fore.RED + msg_content, end='', flush=True)

        if not in_code_block:
            print(Fore.GREEN + msg_content, end='', flush=True)

        
        #print(message['message'],end='', flush=True)
    # id = sendMessage(prompt=p,message_id=id)
    

