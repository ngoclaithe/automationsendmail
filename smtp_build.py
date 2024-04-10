from socket import *
import base64
import ssl
import re
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import mimetypes
ENDMSG = '\r\n.\r\n'
ENDSTR = '\r\n'

def send_email_diy(user_email, user_password, recipient, subject, content, cc_recipients=None, bcc_recipients=None, attachment_file_path=None):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.settimeout(10)
    clientSocketSLL = ssl.wrap_socket(clientSocket)
    mailServer = 'smtp.gmail.com'
    port = 465    
    clientSocketSLL.connect((mailServer, port))

    recv = clientSocketSLL.recv(1024)
    if recv[:3] != bytes('220', 'utf8'):
        print(f'Error: {recv.decode("utf8")}')
        exit(-1)

    # Send EHLO command and print server response.
    heloCommand = f'EHLO {mailServer}{ENDSTR}'
    clientSocketSLL.send(bytes(heloCommand, 'utf8'))
    recv = clientSocketSLL.recv(1024)
    if recv[:3] != bytes('250', 'utf8'):
        print(f'Error: {recv.decode("utf8")}')
        exit(-1)

    # Send AUTH LOGIN to authenticate to the server
    auth = f'AUTH LOGIN{ENDSTR}'
    clientSocketSLL.send(bytes(auth, 'utf8'))
    recv = clientSocketSLL.recv(1024)
    if recv[:3] != bytes('334', 'utf8'):
        print(f'Error: {recv.decode("utf8")}')
        exit(-1)
    else:
        msg = recv.decode('utf8')
        print(f'{recv.decode("utf8")[:3]} {base64.b64decode(msg[3:]).decode("ascii")}', end=' ')
    
    # Send email for authentication
    email = user_email
    login = base64.b64encode(email.encode('utf8'))
    login += ENDSTR.encode('utf8')
    clientSocketSLL.send(login)
    recv = clientSocketSLL.recv(1024)
    msg = recv.decode('utf8')
    print(f'{recv.decode("utf8")[:3]} {base64.b64decode(msg[3:]).decode("ascii")}', end=' ')

    # Send password for authentication
    password = base64.b64encode(user_password.encode('utf8'))
    password += ENDSTR.encode('utf8')
    clientSocketSLL.send(password)
    recv = clientSocketSLL.recv(1024)
    if recv[:3] != bytes('235', 'utf8'):
        print(f'Error: {recv.decode("utf8")}')
        if recv[:3] == bytes('535', 'utf8'):
            exit(-1)
        else:
            exit(-1)
    else:
        print(f'{recv.decode("utf8")}')
    
    # Send MAIL FROM command and print server response.
    mailFrom = f'MAIL FROM: <{email}>{ENDSTR}'
    clientSocketSLL.send(bytes(mailFrom, 'utf8'))
    recv = clientSocketSLL.recv(1024)
    if recv[:3] != bytes('250', 'utf8'):
        print(f'Error: {recv.decode("utf8")}')
        exit(-1)

    # Send RCPT TO command and print server response.
    rcptTo = f'RCPT TO: <{recipient}>{ENDSTR}'
    clientSocketSLL.send(bytes(rcptTo, 'utf8'))
    recv = clientSocketSLL.recv(1024)
    if recv[:3] != bytes('250', 'utf8'):
        print(f'Error: {recv.decode("utf8")}')
        exit(-1)
    # Send RCPT TO command for CC recipients and print server response.
    if cc_recipients:
        for cc_recipient in cc_recipients:
            rcptToCC = f'RCPT TO: <{cc_recipient}>{ENDSTR}'
            clientSocketSLL.send(bytes(rcptToCC, 'utf8'))
            recv = clientSocketSLL.recv(1024)
            if recv[:3] != bytes('250', 'utf8'):
                print(f'Error: {recv.decode("utf8")}')
                exit(-1)
    # Send RCPT TO command for BCC recipients and print server response.
    if cc_recipients:
        for cc_recipient in cc_recipients:
            rcptToCC = f'RCPT TO: <{cc_recipient}>{ENDSTR}'
            clientSocketSLL.send(bytes(rcptToCC, 'utf8'))
            recv = clientSocketSLL.recv(1024)
            if recv[:3] != bytes('250', 'utf8'):
                print(f'Error: {recv.decode("utf8")}')
                exit(-1)

    # Send RCPT TO command for BCC recipients and print server response.
    if bcc_recipients:
        for bcc_recipient in bcc_recipients:
            rcptToBCC = f'RCPT TO: <{bcc_recipient}>{ENDSTR}'
            clientSocketSLL.send(bytes(rcptToBCC, 'utf8'))
            recv = clientSocketSLL.recv(1024)
            if recv[:3] != bytes('250', 'utf8'):
                print(f'Error: {recv.decode("utf8")}')
                exit(-1)
    # Send DATA command and print server response.
    data = f'DATA{ENDSTR}'
    clientSocketSLL.send(bytes(data, 'utf8'))
    recv = clientSocketSLL.recv(1024)
    if recv[:3] != bytes('354', 'utf8'):
        print(f'Error: {recv.decode("utf8")}')
        exit(-1)

    # Send message data.
    subject_line = f'SUBJECT: {subject}{ENDSTR}'
    clientSocketSLL.send(bytes(subject_line, 'utf8'))
    # Send content.
    message = f'{content}{ENDMSG}'
    clientSocketSLL.send(bytes(message, 'utf8'))
    # Attach file if provided.


    recv = clientSocketSLL.recv(1024)
    if recv[:3] != bytes('250', 'utf8'):
        print(f'Error: {recv.decode("utf8")}')
        exit(-1)

    # Send QUIT command and print server response.
    quitCommand = f'QUIT{ENDSTR}'
    clientSocketSLL.send(bytes(quitCommand, 'utf8'))
    recv = clientSocketSLL.recv(1024)
    if recv[:3] != bytes('221', 'utf8'):
        print(f'Error: {recv.decode("utf8")}')
        exit(-1)

    clientSocketSLL.close()
def attach_file(client_socket, file_path):
    pass
