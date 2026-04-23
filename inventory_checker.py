# Static Variables
items = ['Laptop' , 'Monitor' , 'Keyboard' , 'Mouse']
stock = [5, 0, 12, 2]
lim = 5

# Re-Order Function Definition
def reorder(st_cn):
    if st_cn == 0:
        return "CRITICAL"
    elif st_cn < lim:
        return "REORDER"
    else:
        return "OKAY"

# Combining the two Lists into a unified form 
comb = list(zip(items , stock))
print(f"\nThe Unified List is :-\n{comb}\n")

for idx ,(nam, cnt) in enumerate(comb , 101):
    print(f"ID :-> {idx} | Item :-> {nam} | Count :-> {cnt} | Status :-> {reorder(cnt)}")