sw = input('Enter Your Message to Add in the File : ').strip().title()
with open('sample.txt','w') as j:
    j.write(sw)
    
print('File Content Changed Successfully\n')