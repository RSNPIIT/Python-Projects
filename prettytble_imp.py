import prettytable as pt 
table = pt.PrettyTable()
table.add_column( "Pokemon Name" , ["Pikachu","Squirtle","Charmander","Ninetails"])
table.add_column( "Type" , ["Electric","Water","Fire","Fire"])
table.add_column( "Environments Found" , ["Bihar","Tamil Nadu","Tripura","Jharkhand"])
table.align['Pokemon Name'] = 'l'
table.align['Type'] = 'c'
table.align['Environments Found'] = 'r'
print(table)