n = abs(int(input("Enter the number of sentences you wanna get a pair of :-> ")))
SLIST = []
WLIST = set()

for i in range(n):
    sent = input(f"Enter the sentence number {i+1} here :-> ").strip().lower()
    SLIST.append(sent)

for sente in SLIST:
    words = sente.split()

    for i in range(len(words) - 1):
        pair = (words[i], words[i+1])
        WLIST.add(pair)

print(f"The Word Pairs formed here are -> {len(WLIST)}")