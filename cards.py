import random

cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
deck = cards * 4

def create_shoe(num_decks=6):
    shoe = deck * num_decks
    random.shuffle(shoe)
    return shoe

def isSoft(hand):
    total = sum(hand)
    aceCount = hand.count(11)

    while total > 21 and aceCount > 0:
        total -= 10
        aceCount -= 1

    return aceCount > 0 and total < 21

def displayCard(card):

    if card == 11:
        return "Ace"

    else:
        return str(card)

def handTotal(hand):
    total = sum(hand)
    aceCount = hand.count(11)

    while total > 21 and aceCount > 0:
        total -= 10
        aceCount -= 1

    return total

def card_label(card):
    if card == 11:
        return "A"
    return str(card)


def display_hand_visual(hand, hide_second_card=False):
    top = ""
    upper = ""
    middle = ""
    lower = ""
    bottom = ""

    for i, card in enumerate(hand):
        if hide_second_card and i == 1:
            label = "░"
            top += "┌─────┐ "
            upper += "│░░░░░│ "
            middle += "│░░░░░│ "
            lower += "│░░░░░│ "
            bottom += "└─────┘ "
        else:
            label = card_label(card)
            top += "┌─────┐ "
            upper += f"│{label:<5}│ "
            middle += "│     │ "
            lower += f"│{label:>5}│ "
            bottom += "└─────┘ "

    return "\n".join([top, upper, middle, lower, bottom])