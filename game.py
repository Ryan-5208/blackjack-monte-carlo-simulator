import os
import time
from cards import create_shoe, displayCard, handTotal, isSoft, display_hand_visual
from strategy import basic_strategy, getBetFromCount, shouldTakeInsurance
from stats import Stats
from settings import GameSettings


Red = "\033[31m"
Reset = "\033[0m"
Blue = "\033[34m"
Bold = "\033[1m"
Underline = "\033[4m"
Yellow = "\033[33m"

stats = Stats()
settings = GameSettings()
shoe = create_shoe(settings.num_decks)

playing = True
broke = False
autoPlay = False
autoBet = False
autoIns = False
verbose = True
cardCounting = False

bankroll = 0
lastRoundNet = 0
runningCount = 0
trueCount = 0

def reset_game_state():
    global bankroll, lastRoundNet, runningCount, trueCount, broke, shoe

    stats.reset()

    bankroll = 0
    lastRoundNet = 0
    runningCount = 0
    trueCount = 0
    broke = False
    shoe = create_shoe(settings.num_decks)

def dealCard(hand):
    global runningCount
    card = shoe.pop()
    hand.append(card)

    if card in [2, 3, 4, 5, 6]:
        runningCount += 1
    elif card in [10, 11]:
        runningCount -= 1

def drawCardAndShow(hand, handName):
    dealCard(hand)
    pause(1)
    gamePrint(f"{Blue}{handName} drawn card: {displayCard(hand[-1])}{Reset}")
    gamePrint(display_hand_visual(hand))
    pause(1)
    showHandTotal(handName, hand, Blue)

    return handTotal(hand)

def BJCheck(player, dealer, dealerHand, amount, autoIns = False, baseBet=10):
    global bankroll

    insAsk = "n"

    if dealerHand[0] == 11:
        pause(1)
        gamePrint()

        if autoIns:
            if cardCounting and shouldTakeInsurance(trueCount):
                insAsk = "yes"
            else:
                insAsk = "no"
        else:
            while True:
                insAsk = input("Insurance? (Y/N): ").lower()

                if insAsk in ["y", "yes", "n", "no"]:
                    break

                gamePrint()
                gamePrint("Please enter Y or N.")
                gamePrint()

    if insAsk.lower() in ["y", "yes"]:
        stats.insuranceTaken += 1
        insuranceBet = amount * 0.5

        while insuranceBet > bankroll:
            pause(1)
            gamePrint("You do not have enough for insurance.")
            gamePrint()
            pause(1)

            if autoIns:
                moneyAdd(baseBet * 100)
            else:
                addMoney = getPositiveAmount("How much would you like to add: $")
                bankroll += addMoney
                stats.totalBankroll += addMoney
        bankroll -= insuranceBet
        stats.totalWagered += insuranceBet
        if dealerHand[1] == 10:
            pause(1)
            gamePrint()
            gamePrint(f"Insurance wins ${insuranceBet * 2:.2f}")
            stats.net += insuranceBet * 2
            bankroll += insuranceBet * 3
        else:
            pause(1)
            gamePrint("Insurance loses")
            stats.net -= insuranceBet

    if player == 21 and dealer != 21:
        pause(.5)
        gamePrint()
        gamePrint(f"{Bold}Blackjack! Congrats{Reset}")
        gamePrint()
        pause(.5)
        gamePrint(f"{Red}Dealer under card: {displayCard(dealerHand[1])} {Reset}")
        gamePrint(display_hand_visual(dealerHand))
        pause(.5)
        showHandTotal("Dealer", dealerHand, Red)
        stats.wins += 1
        stats.net += amount * settings.blackjack_payout
        bankroll += amount * (1 + settings.blackjack_payout)
        stats.playerBlackJacks += 1
        return True


    elif player == 21 and dealer == 21:
        gamePrint()
        gamePrint(f"{Red}Dealer second card: {displayCard(dealerHand[-1])}{Reset}")
        gamePrint(display_hand_visual(dealerHand))
        showHandTotal("Dealer", dealerHand, Red)
        gamePrint()
        gamePrint(f"{Bold}Sorry, Dealer also has BlackJack. Push{Reset}")
        stats.ties += 1
        stats.pushOnBlackJacks += 1
        bankroll += amount
        return True


    elif player != 21 and dealer == 21:
        gamePrint()
        gamePrint(f"{Red}Dealer second card: {displayCard(dealerHand[-1])}{Reset}")
        gamePrint(display_hand_visual(dealerHand))
        gamePrint(f"{Red}Dealer has: 21{Reset}")
        gamePrint()
        gamePrint(f"{Bold}Dealer has BlackJack{Reset}")
        stats.losses += 1
        stats.net -= amount
        stats.dealerBlackJacks += 1
        return True
    
    return False

def dealerPlay(dealerHand):
    pause(1)
    gamePrint()
    gamePrint(f"{Red}Dealer second card: {displayCard(dealerHand[-1])}{Reset}")
    gamePrint(display_hand_visual(dealerHand))
    showHandTotal("Dealer", dealerHand, Red)    
    while handTotal(dealerHand) < 17 or (
        handTotal(dealerHand) == 17
        and isSoft(dealerHand)
        and settings.dealer_hits_soft_17
        ):
        dealCard(dealerHand)
        pause(1)
        gamePrint()
        gamePrint(f"Dealer drawing: ")
        pause(1)
        gamePrint(f"{Red}Dealer Card: {displayCard(dealerHand[-1])}{Reset}")
        gamePrint(display_hand_visual(dealerHand))
        pause(.75)
        showHandTotal("Dealer", dealerHand, Red) 

def compareHand(player, dealer, name, doubled, amount):
    global bankroll
    pause(1)
    multiplier = 2 if doubled else 1
    gamePrint()

    if player > 21:
        gamePrint(f"{Bold}{name} busts{Reset}")
        stats.net -= amount * multiplier
        stats.playerBusts += 1
        stats.losses += 1

    elif dealer > 21:
        gamePrint(f"{Bold}Dealer busts!{Reset}")
        stats.net += amount * multiplier
        bankroll += amount * multiplier * 2
        stats.wins += 1

    elif player > dealer:
        gamePrint(f"{Bold}{name} wins!{Reset}")
        stats.net += amount * multiplier
        bankroll += amount * multiplier * 2
        stats.wins += 1

    elif player < dealer:
        gamePrint(f"{Bold}{name} loses{Reset}")
        stats.net -= amount * multiplier
        stats.losses += 1

    else:
        gamePrint(f"{Bold}{name} pushes{Reset}")
        bankroll += amount * multiplier
        stats.ties += 1

def playHand(hand, handName, amount, dealer_card, splitAces = False, autoPlay = False, baseBet=10, isSplitHand=False):
    global bankroll
    FirstCard = True
    doubled = False
    surrendered = False
    split = False

    while True:
        canSplit = FirstCard and len(hand) == 2 and hand[0] == hand[1]

        if splitAces:
            if canSplit:
                validChoices = ["sp", "split"]
            else:
                return handTotal(hand), doubled, surrendered, False
        elif canSplit:
            validChoices = ["h", "hit", "s", "stand", "sp", "split"]

            if not isSplitHand or settings.double_after_split:
                validChoices += ["d", "double"]

            if settings.surrender_allowed:
                validChoices += ["sur", "surrender"]

        elif FirstCard:
            validChoices = ["h", "hit", "s", "stand"]

            if not isSplitHand or settings.double_after_split:
                validChoices += ["d", "double"]

            if settings.surrender_allowed:
                validChoices += ["sur", "surrender"]
        else:
            validChoices = ["h", "hit", "s", "stand"]

        if handTotal(hand) >= 21:
            return handTotal(hand), doubled, surrendered, False

        gamePrint()
        if autoPlay:
            strategyTrueCount = trueCount if cardCounting else 0
            decision = basic_strategy(hand, dealer_card, validChoices, strategyTrueCount)            
            gamePrint(f"{Bold}{handName}{Reset}: {decision}")

        else:
            if splitAces:
                decision = input(f"{Bold}{handName}{Reset}: Split Aces: (Sp): ")

            elif canSplit:
                decision = input(f"{Bold}{handName}{Reset}: Hit, Stand, Split, Surrender, or Double: (H/S/Sp/Sur/D): ")

            elif FirstCard:
                decision = input(f"{Bold}{handName}{Reset}: Hit, Stand, Surrender, or Double: (H/S/Sur/D): ")
            else:
                decision = input(f"{Bold}{handName}{Reset}: Hit or Stand: (H/S): ")
        gamePrint()

        if decision.lower() not in validChoices:
            pause(1)
            gamePrint(f"{Yellow}Give a valid answer{Reset}")
            continue

        if decision.lower() in ["h", "hit"]:
            stats.hits += 1
            total = drawCardAndShow(hand, handName)

            if total >= 21:
                return total, doubled, surrendered, split

            FirstCard = False
        
        elif decision.lower() in ["split", "sp"] and canSplit:
            stats.splits += 1
            split = True
            return handTotal(hand), doubled, surrendered, split

	            
        elif decision.lower() in ["surrender", "sur"] and FirstCard:
            stats.surrenders += 1
            pause(1)
            gamePrint("You surrendered")
            pause(1)
            surrendered = True
            return handTotal(hand), doubled, surrendered, split

        elif decision.lower() in ["d", "double"] and FirstCard:
            if amount > bankroll:
                gamePrint("You do not have enough to double")
                gamePrint()
                pause(1)
                if autoPlay:
                    moneyAdd(baseBet * 100)
                else:
                    addMoney = getPositiveAmount("How much would you like to add: $")
                    bankroll += addMoney
                    stats.totalBankroll += addMoney
                    pause(1)
                continue
            bankroll -= amount
            stats.totalWagered += amount
            stats.doubles += 1
            total = drawCardAndShow(hand, handName)
            doubled = True
            return total, doubled, surrendered, split
	            

        elif decision.lower() in ["s", "stand"]:
            pause(1)
            stats.stands += 1
            gamePrint(f"{handName} stands")
            return handTotal(hand), doubled, surrendered, split

        else:
            FirstCard = False

def run_game():
    global verbose, bankroll

    reset_game_state()
    verbose = True
    if verbose:
        os.system("clear")
    print()
    print(f"{Underline}Welcome To BlackJack!{Reset}")
    print()

    addMoney = getPositiveAmount("What's your bankroll: $")
    bankroll += addMoney
    stats.totalBankroll += addMoney

    while True:
        play_round(autoPlay=False, autoBet=False, autoIns=False, baseBet = 10)

        again = input("Play again? (Y/N): ")
        if again.lower() in ["n", "no"]:
            break

def play_round(autoPlay=False, autoBet=False, autoIns=False, baseBet=10):
    global bankroll, lastRoundNet
    global runningCount, trueCount, broke, shoe

    stats.roundsPlayed += 1
    roundOver = False
    startingNet = stats.net
    
    if verbose:
        os.system("clear")
    lastRoundText = f"+${lastRoundNet:.2f}" if lastRoundNet > 0 else f"${lastRoundNet:.2f}"
    gamePrint(f"=== BLACKJACK === \t\t\t{f'Bankroll: ${bankroll:.2f} | Net: ${stats.net:.2f} | Last Hand: {lastRoundText}'} | Count: {runningCount} | True Count: {trueCount} | Hand #: {stats.roundsPlayed}")

    #Out of money
    if broke:
        gamePrint("Out of money!")
        pause(1)
        if autoPlay:
            moneyAdd(baseBet * 100)
        else:
            addMoney = getPositiveAmount("How much would you like to add: $")
            bankroll += addMoney
            stats.totalBankroll += addMoney
            
        broke = False
        if verbose:
            os.system("clear")
        lastRoundText = f"+${lastRoundNet:.2f}" if lastRoundNet > 0 else f"${lastRoundNet:.2f}"
        gamePrint(f"=== BLACKJACK === \t\t\t\t{f'Bankroll: ${bankroll:.2f} | Net: ${stats.net:.2f} | Last Hand: {lastRoundText}'} | Count: {runningCount} | True Count: {trueCount}")

    #Need to Reshuffle
    if len(shoe) < 52:
        shoe = create_shoe(settings.num_decks)
        gamePrint()
        gamePrint("Reshuffling shoe...") 
        runningCount = 0
        trueCount = 0
        pause(1)
        if verbose:
            os.system("clear")
        lastRoundText = f"+${lastRoundNet:.2f}" if lastRoundNet > 0 else f"${lastRoundNet:.2f}"
        gamePrint(f"=== BLACKJACK === \t\t\t\t{f'Bankroll: ${bankroll:.2f} | Net: ${stats.net:.2f} | Last Hand: {lastRoundText}'} | Count: {runningCount} | True Count: {trueCount}")

    #Bet size
    while True:

        if autoBet:
            amount = getBetFromCount(baseBet, trueCount, bankroll, cardCounting)
            gamePrint(f"Bet amount: ${amount:.2f}")
            pause(1)
            break
        else:
            try:
                amount = float(input("Bet amount: $"))

                if amount <= 0:
                    gamePrint()
                    pause(1)
                    gamePrint("Bet must be positive")
                    gamePrint()
                    pause(1)
                    continue

                if amount > bankroll:
                    gamePrint()
                    pause(1)
                    gamePrint(f"You don't have enough bankroll to bet ${amount:.2f}")
                    pause(1)
                    gamePrint()
                    continue

                break

            except ValueError:
                gamePrint()
                pause(1)
                gamePrint("Enter a valid number")
                pause(1)
                gamePrint()

    bankroll -= amount
    stats.totalWagered += amount
    
    playerHand = []
    dealerHand = []

    dealCard(playerHand)
    dealCard(dealerHand)
    dealCard(playerHand)
    dealCard(dealerHand)

    dealer_upcard = dealerHand[0]
    stats.dealerUpcardCount[dealer_upcard] += 1

    playerHands = [
        {
            "cards": playerHand,
            "total": handTotal(playerHand),
            "doubled": False,
            "surrendered": False,
            "splitAces": False,
            "done": False
        }
    ]

    pause(.5)
    gamePrint()
    gamePrint("Dealing...")
    pause(.75)
    gamePrint()

    player = handTotal(playerHand)
    dealer = handTotal(dealerHand)

    gamePrint(f"{Red}Dealer hand:{Reset}")
    gamePrint(display_hand_visual(dealerHand, hide_second_card=True))
    gamePrint(f"{Red}Dealer up card: {displayCard(dealerHand[0])}{Reset}")

    gamePrint()

    gamePrint(f"{Blue}Player hand:{Reset}")
    gamePrint(display_hand_visual(playerHand))
    showHandTotal("Player", playerHand, Blue)

    pause(.75)

    roundOver = BJCheck(handTotal(playerHand), handTotal(dealerHand), dealerHand, amount, autoIns, baseBet)

    if not roundOver:
        handIndex = 0

        while handIndex < len(playerHands):
            handInfo = playerHands[handIndex]

            # If this hand only has one card, it means it came from a split.
            if len(handInfo["cards"]) == 1:
                dealCard(handInfo["cards"])

                delayedHandName = f"Hand {handIndex + 1}"

                gamePrint()
                pause(1)
                gamePrint(f"{Blue}{delayedHandName} drawn card: {displayCard(handInfo['cards'][-1])}{Reset}")
                gamePrint(display_hand_visual(handInfo["cards"]))
                pause(1)
                showHandTotal(delayedHandName, handInfo["cards"], Blue)

                if handInfo["splitAces"] and handInfo["cards"][1] != 11:
                    handInfo["total"] = handTotal(handInfo["cards"])
                    handInfo["done"] = True

            if handInfo["done"]:
                handIndex += 1
                continue

            if len(playerHands) == 1:
                handName = "Player"
            else:
                handName = f"Hand {handIndex + 1}"

            player, doubled, surrendered, split = playHand(
                handInfo["cards"],
                handName,
                amount,
                dealerHand[0],
                handInfo["splitAces"],
                autoPlay,
                baseBet,
                len(playerHands) > 1
            )

            if split:
                while amount > bankroll:
                    gamePrint("You do not have enough to split.")
                    gamePrint()
                    pause(1)

                    if autoPlay:
                        moneyAdd(baseBet * 100)
                    else:
                        addMoney = getPositiveAmount("How much would you like to add: $")
                        bankroll += addMoney
                        stats.totalBankroll += addMoney

                    gamePrint()
                    pause(1)

                bankroll -= amount
                stats.totalWagered += amount

                firstCard = handInfo["cards"][0]
                secondCard = handInfo["cards"][1]

                # Current hand keeps the first card
                handInfo["cards"] = [firstCard]
                handInfo["splitAces"] = firstCard == 11
                handInfo["done"] = False

                # New hand keeps the second card but doesn't get the next card
                newHand = {
                    "cards": [secondCard],
                    "total": 0,
                    "doubled": False,
                    "surrendered": False,
                    "splitAces": secondCard == 11,
                    "done": False
                }

                # Deals current hand
                dealCard(handInfo["cards"])

                splitHandName = f"Hand {handIndex + 1}"

                pause(1)
                gamePrint(f"{Blue}{splitHandName} drawn card: {displayCard(handInfo['cards'][-1])}{Reset}")
                gamePrint(display_hand_visual(handInfo["cards"]))
                pause(1)
                showHandTotal(splitHandName, handInfo["cards"], Blue)

                if handInfo["splitAces"] and handInfo["cards"][1] != 11:
                    handInfo["total"] = handTotal(handInfo["cards"])
                    handInfo["done"] = True

                # Add the second hand with only one card and gets its second card later when its turn starts.

                playerHands.append(newHand)

                continue

            else:
                handInfo["total"] = player
                handInfo["doubled"] = doubled
                handInfo["surrendered"] = surrendered
                handIndex += 1

        dealerShouldPlay = False

        for handInfo in playerHands:
            if not handInfo["surrendered"] and handInfo["total"] <= 21:
                dealerShouldPlay = True
        if dealerShouldPlay:
            dealerPlay(dealerHand)
            dealer = handTotal(dealerHand)

            stats.dealerPlayedByUpcard[dealer_upcard] += 1

            if dealer > 21:
                stats.dealerBusts += 1
                stats.dealerBustByUpcard[dealer_upcard] += 1

        allHandsBusted = True

        for handInfo in playerHands:
            if not handInfo["surrendered"] and handInfo["total"] <= 21:
                allHandsBusted = False

        if allHandsBusted:
            pause(.75)
            gamePrint()
            gamePrint(f"{Red}Dealer under card: {displayCard(dealerHand[1])} {Reset}")
            gamePrint(display_hand_visual(dealerHand))
            pause(.75)
            gamePrint(f"{Red}Dealer had: {handTotal(dealerHand)}{Reset}")


        for index, handInfo in enumerate(playerHands):
            if len(playerHands) == 1:
                handName = "Player"
            else:
                handName = f"Hand {index + 1}"

            if handInfo["surrendered"]:
                stats.losses += 1
                stats.net -= amount * 0.5
                bankroll += amount * 0.5
            else:
                compareHand(handInfo["total"], dealer, handName, handInfo["doubled"], amount) 
                
    lastRoundNet = stats.net - startingNet
    gamePrint()
    pause(1)
    gamePrint(f"Bankroll: {bankroll:.2f}")
    if stats.net > 0:
        gamePrint(f"Net: +{stats.net:.2f}")
    else:
        gamePrint(f"Net: {stats.net:.2f}")
    if lastRoundNet > 0:
        gamePrint(f"Last Hand: +{lastRoundNet:.2f}")
    else:
        gamePrint(f"Last Hand: {lastRoundNet:.2f}")
    pause(2.5)

    if bankroll <= 0:
        broke = True
    
    decksRemaining = len(shoe) / 52
    trueCount = int(runningCount / decksRemaining)

    gamePrint()

    stats.update_net_stats()
    stats.update_bankroll_stats(bankroll)
    stats.record_round(bankroll, runningCount, trueCount)

def showHandTotal(name, hand, color):
    total = handTotal(hand)

    if isSoft(hand):
        gamePrint(f"{color}{name} has: soft {total}{Reset}")
    else:
        gamePrint(f"{color}{name} has: {total}{Reset}")

def gamePrint(text=""):
    if verbose:
        print(text)

def pause(seconds):
    if verbose:
        time.sleep(seconds)

def moneyAdd(amount=1000):
    global bankroll

    bankroll += amount
    stats.totalBankroll += amount

def getPositiveAmount(prompt):
    while True:
        try:
            amount = float(input(prompt))

            if amount <= 0:
                gamePrint()
                pause(1)
                gamePrint("Amount must be positive")
                gamePrint()
                pause(1)
                continue

            return amount

        except ValueError:
            gamePrint()
            pause(1)

            gamePrint("Enter a valid number")
            gamePrint()
            pause(1)

def get_bankroll():
    return bankroll

def set_bankroll(amount):
    global bankroll
    bankroll = amount

def set_verbose(value):
    global verbose
    verbose = value

def set_card_counting(value):
    global cardCounting
    cardCounting = value

def set_settings(new_settings):
    global settings, shoe
    settings = new_settings
    shoe = create_shoe(settings.num_decks)