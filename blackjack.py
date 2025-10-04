import random
# The Blackjack 0 score is a sentinel value for a two-card 21 (Blackjack).
# Day 11 Finished --- Thankyou UDEMY Thankyou Dr Angela Yu
# See its like 3 functions 2 loops and Done 
def deal_card():
    """Returns a random card from the deck (2-10, J,Q,K=10, A=11)."""
    cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
    return random.choice(cards)

def calculate_score(cards):
    """Calculates the score and handles the Ace (11/1) conversion."""
    # Check for a two-card Blackjack (sum=21). Returns 0 as the sentinel value.
    if sum(cards) == 21 and len(cards) == 2:
        return 0
    # Convert Ace (11) to 1 if the total sum is over 21.
    while 11 in cards and sum(cards) > 21:
        cards.remove(11)
        cards.append(1)
    return sum(cards)

def compare(u_sum, c_sum):
    """Compares scores to determine the winner."""
    if u_sum == c_sum:
        return "It's a Draw. 🤝"
    elif c_sum == 0:
        return "Computer has a Blackjack. You Lose. 😭"
    elif u_sum == 0:
        return "You Win with a Blackjack! 🎉"
    elif u_sum > 21:
        return "You Busted! You Lose. 💀"
    elif c_sum > 21:
        return "Computer Busted! You Win. ✅"
    elif u_sum > c_sum:
        return "You Win! 💰"
    else:
        return "You Lose. 😔"

# ----------------- Game Start -----------------
print(r"""
    __________.__                 __         __               __    
\______   \  | _____    ____ |  | __    |__|____    ____ |  | __
 |    |  _/  | \__  \ _/ ___\|  |/ /    |  \__  \ _/ ___\|  |/ /
 |    |   \  |__/ __ \\  \___|    <     |  |/ __ \\  \___|    < 
 |______  /____(____  /\___  >__|_ \/\__|  (____  /\___  >__|_ \
        \/          \/     \/     \/\______|    \/     \/     \/
""")

user_card = []
comp_card = []
user_sum = 0
comp_sum = 0

# Initial Deal
for _ in range(2):
    user_card.append(deal_card())
    comp_card.append(deal_card())

user_sum = calculate_score(user_card)
comp_sum = calculate_score(comp_card)

is_hitting = True
while is_hitting:
    print(f"\nYour Cards are : {user_card}, current score: {user_sum}")
    print(f"Computer's first card is : [{comp_card[0]}]")
    
    # Check for instant game over conditions (Blackjack or Bust)
    if user_sum == 0 or comp_sum == 0 or user_sum > 21:
        is_hitting = False
    else:
        user_deal = input("Type 'y' to hit (get another card) or 'n' to stand (skip): ").strip().lower()
        
        if user_deal == 'y':
            user_card.append(deal_card())
            user_sum = calculate_score(user_card) # Recalculate score after the hit
        elif user_deal == 'n':
            is_hitting = False # Player stands, their turn is over
        else:
            print("Invalid input, automatically standing.")
            is_hitting = False

# ----------------- Computer's Turn -----------------
# The computer keeps hitting as long as its score is less than 17 AND it doesn't have a Blackjack (0).
# This only runs if the user hasn't busted or gotten Blackjack.
if user_sum != 0 and user_sum <= 21:
    while comp_sum != 0 and comp_sum < 17:
        print("Computer hits...")
        comp_card.append(deal_card())
        comp_sum = calculate_score(comp_card) # CRITICAL: Update comp_sum here

# ----------------- Final Result -----------------
print("\n" + "="*30)
print(f"Your Final Hand is : {user_card} and final score is : {user_sum}")
print(f"Computer Final Hand is : {comp_card} and final score is : {comp_sum}")
print("="*30)
print(compare(user_sum, comp_sum))
print("="*30)