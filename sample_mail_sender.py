#Importing the Smtp Library
import smtplib as sm
my_em = "sample user's@gmail.com"
pas = "abcd efgh ijkl mnop"
to_se_em = "sampleuser@gmail.com"

#Connection of the Email
with sm.SMTP('smtp.gmail.com') as conn:
    conn.starttls()  
    conn.login(user = my_em , password = pas)
    conn.sendmail(
        from_addr = my_em , 
        to_addrs = to_se_em , 
        msg = 'Hello its me\nHope all is well'
    )