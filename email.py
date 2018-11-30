def send_email():
    from email.mime.text import MIMEText
    from phila_mail import server

    recipientslist = ['peter.dannemann@Phila.gov', 
                      'dani.interrante@phila.gov', 
                      'philip.ribbens@phila.gov',
                      'shannon.holm@phila.gov']
    sender = 'peter.dannemann@phila.gov'
    commaspace = ', '
    email = 'LI Dashboards server failed to launch. Please restart the VM and manually launch the web server.'
    text = f'AUTOMATIC EMAIL: \n {email}'
    msg = MIMEText(text)
    msg['To'] = commaspace.join(recipientslist)
    msg['From'] = sender
    msg['X-Priority'] = '2'
    msg['Subject'] = 'Important Email'
    server.server.sendmail(sender, recipientslist, msg.as_string())
    server.server.quit()