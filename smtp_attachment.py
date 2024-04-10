from socket import *
import base64
import os
import ssl

def send_email_diy(fromaddr, passwordapp, toaddr, message_text, subject="", cc=None, bcc=None, attachment_path=None):
    endmsg = "\r\n.\r\n"
    mailserver = "smtp.gmail.com"
    username = base64.b64encode(fromaddr.encode()).decode()
    password = base64.b64encode(passwordapp.encode()).decode()

    clientSocket = socket(AF_INET, SOCK_STREAM)

    context = ssl.create_default_context()
    clientSocket = context.wrap_socket(clientSocket, server_hostname=mailserver)

    clientSocket.connect((mailserver, 465))

    recv = clientSocket.recv(1024).decode()
    print(recv)
    if recv[:3] != '220':
        print('220 reply not received from server.')

    heloCommand = 'HELO Alice\r\n'
    clientSocket.send(heloCommand.encode())
    recv1 = clientSocket.recv(1024).decode()
    print("hello command receipt:", recv1)
    if recv1[:3] != '250':
        print('250 reply not received from server.')

    clientSocket.sendall('AUTH LOGIN\r\n'.encode())
    recv = clientSocket.recv(1024).decode()
    print("Auth login command:", recv)
    if recv[:3] != '334':
        print('334 reply not received from server')

    clientSocket.sendall((username + '\r\n').encode())
    recv = clientSocket.recv(1024).decode()
    print("username information:", recv)
    if recv[:3] != '334':
        print('334 reply not received from server')

    clientSocket.sendall((password + '\r\n').encode())
    recv = clientSocket.recv(1024).decode()
    print("password information:", recv)
    if recv[:3] != '235':
        print('235 reply not received from server')

    clientSocket.sendall(('MAIL FROM: <' + fromaddr + '>\r\n').encode())
    recv = clientSocket.recv(1024).decode()
    print(recv)
    if recv[:3] != '250':
        print('250 reply not received from server')

    clientSocket.sendall(('RCPT TO: <' + toaddr + '>\r\n').encode())
    recv = clientSocket.recv(1024).decode()
    print(recv)
    if recv[:3] != '250':
        print('250 reply not received from server')

    # Handle CC and BCC
    if cc:
        for cc_addr in cc:
            clientSocket.sendall(('RCPT TO: <' + cc_addr + '>\r\n').encode())
            recv = clientSocket.recv(1024).decode()
            print(recv)
            if recv[:3] != '250':
                print('250 reply not received from server')

    if bcc:
        for bcc_addr in bcc:
            clientSocket.sendall(('RCPT TO: <' + bcc_addr + '>\r\n').encode())
            recv = clientSocket.recv(1024).decode()
            print(recv)
            if recv[:3] != '250':
                print('250 reply not received from server')

    clientSocket.send('DATA\r\n'.encode())
    recv = clientSocket.recv(1024).decode()
    print(recv)
    if recv[:3] != '354':
        print('354 reply not received from server')
    fromname = fromaddr
    toname = toaddr
    # Build the email message
    full_message = ""
    full_message += 'From: ' + fromname + ' <' + fromaddr + '>' + '\r\n'
    full_message += 'To: ' + toname + ' <' + toaddr + '>' + '\r\n'

    if cc:
        full_message += 'Cc: ' + ', '.join(cc) + '\r\n'

    if bcc:
        full_message += 'Bcc: ' + ', '.join(bcc) + '\r\n'

    if subject:
        full_message += 'Subject: ' + subject + '\r\n'

    full_message += 'MIME-Version: 1.0' + '\r\n'
    full_message += 'Content-Type: multipart/mixed;' + ' boundary="frontier"'

    full_message += '\r\n'
    full_message += 'This is a multipart message in MIME format.' + '\r\n'
    full_message += '\r\n'

    full_message += '--frontier' + '\r\n'
    full_message += 'Content-Type: text/plain' + '\r\n'
    full_message += '\r\n'
    full_message += message_text + '\r\n'
    full_message += '\r\n'

    # Check if there is an attachment
    if attachment_path:
        attach_file_name = os.path.basename(attachment_path)
        attach_file = open(attachment_path, 'rb')
        file_byte = attach_file.read()
        full_message += '--frontier' + '\r\n'
        full_message += 'Content-Type: application/octet-stream;' + '\r\n'
        full_message += 'Content-Disposition: attachment;' + ' filename="' + attach_file_name + '"\r\n'
        full_message += 'Content-Transfer-Encoding: base64' + '\r\n'
        full_message += '\r\n'
        full_message += (base64.b64encode(file_byte)).decode('ascii') + '\r\n'
        full_message += '\r\n'
        full_message += '--frontier' + '\r\n'

    clientSocket.sendall(full_message.encode())

    clientSocket.sendall(endmsg.encode())
    recv = clientSocket.recv(1024).decode()
    print(recv)
    if recv[:3] != '250':
        print('250 reply not received from server')

    clientSocket.sendall('QUIT\r\n'.encode())
    clientSocket.close()

