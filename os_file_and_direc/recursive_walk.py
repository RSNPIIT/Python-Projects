import os as o

def get_recursive_level(dir):
    if not o.path.exists(dir):
        return "Directory not found"
    
    LIS = o.walk(dir)
    file_count = 0
    file_lis = set()
    subdir_count = 0
    subdir_lis = set()

    for root, dirs, files in LIS:
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for d in dirs:
            subdir_count += 1
            full_sub_path = o.path.join(root, d)
            rel_sub_path = o.path.relpath(full_sub_path, dir)
            subdir_lis.add(rel_sub_path.lower())

        for f in files:
            if f.startswith('.') or f.startswith('__'):
                continue
            
            file_count += 1
            full_file_path = o.path.join(root, f)
            rel_file_path = o.path.relpath(full_file_path, dir)
            file_lis.add(rel_file_path.lower())
    
    return file_count, file_lis, subdir_count, subdir_lis

DIREC = input("Enter the Directory here :-> ").strip()
if not DIREC:
    print("Directory not specified...\nAssuming '~/Desktop' (works for UNIX devices only)\n")
    DIREC = '~/Desktop'

DIREC = o.path.expanduser(DIREC)
result = get_recursive_level(DIREC)

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