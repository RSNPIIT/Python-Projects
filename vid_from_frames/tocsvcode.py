FILE = 'teller.csv'
MODE = 'w'

with open(FILE , MODE) as j:
    j.write('Frames\n')
    for i in range(1572):
        j.write(f'Frame_{i}\n')

print("\nWritten to File as to prevent Hardcoded values")