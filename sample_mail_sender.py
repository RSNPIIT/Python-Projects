"""
Sample SMTP email sender using smtplib.

IMPORTANT:
- This is a demo script.
- Do NOT hard-code credentials.
- Use environment variables (EMAIL_USER, EMAIL_PASS).
- Gmail requires App Passwords with 2FA enabled.
"""
#The Python Code starts here ->

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
