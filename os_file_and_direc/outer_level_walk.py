import os as o

def get_top_level(dir):
    try:
        LIS = o.listdir(dir)
        file_count = 0
        file_lis = set()
        subdir_count = 0
        subdir_lis = set()
    except FileNotFoundError as fnf:
        return f"Directory Not found\n{fnf}"
    else:
        for things in LIS:
            comp_path = o.path.join(dir, things)
            if o.path.isfile(comp_path):
                if things.startswith('.') or things.startswith('__'):
                    continue

                file_count += 1
                file_lis.add(things.lower())
            elif o.path.isdir(comp_path):
                if things.startswith('.'):
                    continue # As many directories are kept hidden from unix OS' by a .
                subdir_count += 1
                subdir_lis.add(things.lower())
            else:
                pass
    return file_count, file_lis, subdir_count, subdir_lis

DIREC = input("Enter the Directory here :-> ").strip()
if not DIREC:
    print("Directory not specified...\nAssuming '~/Desktop' (works for UNIX devices only)\n")
    DIREC = '~/Desktop'

DIREC = o.path.expanduser(DIREC)
result = get_top_level(DIREC)

if isinstance(result, str):
    print(result)

else:
    file_count, file_lis, subdir_count, subdir_lis = result
    print(f"Summary is out :->\n")
    print(f"Number of Files -> {file_count}\nNumber of SubDirectories -> {subdir_count}")

    print("The files are as follows :->\n")
    for idx,el in enumerate(file_lis):
        print(f"{idx + 1} -> {el}")

    print("The subdirectories are as follows :->\n")
    for idx,el in enumerate(subdir_lis):
        print(f"{idx + 1} -> {el}")