from cards import handTotal, isSoft

def basic_strategy(player_hand, dealer_card, validChoices, trueCount):
    player_total = handTotal(player_hand)

    def legal(choice, fallback):
        if choice in validChoices:
            return choice
        return fallback

    if validChoices == ["sp", "split"]:
        return "split"

    if "split" in validChoices and len(player_hand) == 2 and player_hand[0] == player_hand[1]:
        pair = player_hand[0]

        if pair == 11:
            return "split"
        elif pair == 8:
            if dealer_card in [10, 11]:
                return legal("surrender", "split")
            else:
                return "split"
        elif pair in [2, 3, 7]:
            return "split" if dealer_card in [2, 3, 4, 5, 6, 7] else "hit"
        elif pair == 4:
            return "split" if dealer_card in [5, 6] else "hit"
        elif pair == 5:
            return legal("double", "hit") if dealer_card not in [10, 11] else "hit"
        elif pair == 6:
            return "split" if dealer_card in [2, 3, 4, 5, 6] else "hit"
        elif pair == 9:
            return "stand" if dealer_card in [7, 10, 11] else "split"
        elif pair == 10:
            return "stand"

    if isSoft(player_hand):
        if player_total in [13, 14, 15, 16]:
            return legal("double", "hit") if dealer_card in [4, 5, 6] else "hit"
        elif player_total == 17:
            return legal("double", "hit") if dealer_card in [3, 4, 5, 6] else "hit"
        elif player_total == 18:
            if dealer_card in [3, 4, 5, 6]:
                return legal("double", "stand")
            elif dealer_card in [2, 7, 8]:
                return "stand"
            else:
                return "hit"
        else:
            return "stand"
        
    if "surrender" in validChoices and shouldSurrender(player_hand, dealer_card, trueCount):
        return "surrender"

    if player_total <= 8:
        return "hit"
    elif player_total == 9:
        return legal("double", "hit") if dealer_card in [3, 4, 5, 6] else "hit"
    elif player_total == 10:
        return legal("double", "hit") if dealer_card not in [10, 11] else "hit"
    elif player_total == 11:
        return legal("double", "hit")
    elif player_total in [12, 13, 14]:
        return "hit" if dealer_card in [7, 8, 9, 10, 11] else "stand"
    elif player_total == 15:
        if dealer_card in [10, 11]:
            return legal("surrender", "hit")
        return "hit" if dealer_card in [7, 8, 9] else "stand"
    elif player_total == 16:
        if dealer_card in [9, 10, 11]:
            return legal("surrender", "hit")
        return "hit" if dealer_card in [7, 8] else "stand"
    else:
        return "stand"

def getBetFromCount(baseBet, trueCount, bankroll, cardCounting):

    if cardCounting:
        if trueCount <= 1:
            units = 1
        elif trueCount == 2:
            units = 2
        elif trueCount == 3:
            units = 4
        else:
            units = 8
    else:
        units = 1

    bet = baseBet * units

    return min(bet, bankroll)


def shouldSurrender(hand, dealer_card, trueCount):
    total = handTotal(hand)

    if total == 16 and dealer_card in [9, 10, 11]:
        return True

    if total == 15 and dealer_card == 10:
        return True

    if total == 16 and dealer_card == 8 and trueCount >= 4:
        return True

    if total == 15 and dealer_card == 9 and trueCount >= 2:
        return True

    if total == 15 and dealer_card == 11 and trueCount >= 1:
        return True

    if total == 14 and dealer_card == 10 and trueCount >= 3:
        return True

    return False

def shouldTakeInsurance(trueCount):
    return trueCount >= 3

