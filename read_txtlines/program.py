import os
os.makedirs('ReadytoSend', exist_ok=True)


placeholder = '[name]'
print('Peoples names -> \n')
with open('list.txt') as f:
    y = f.readlines()
    print(y)
 
print('Letter That I have Generated -> (source : openai chatgpt)\n')
with open('letter.txt') as k:
    z = k.read()
    print(z)
    for x in y:
        val = z.replace(placeholder,x.strip())
        # print(val)

        with open(f'/home/kali/Desktop/python_projects/read_txtlines/ReadytoSend/letter_for_{x.strip()}.txt','w') as cl: 
            #Please Check the name in Mac and Windows as it follows the Linux Convention (but by def I assumed a folder inside another wheere I'm writing)
            cl.write(val)

print('\nDone -- Process Automated')