class Stats:
    def __init__(self):
        self.reset()

    def reset(self):
        # Main outcome stats
        self.wins = 0
        self.losses = 0
        self.ties = 0
        self.net = 0
        self.roundsPlayed = 0

        # Blackjack stats
        self.playerBlackJacks = 0
        self.dealerBlackJacks = 0
        self.pushOnBlackJacks = 0

        # Bust stats
        self.playerBusts = 0
        self.dealerBusts = 0

        # Net tracking
        self.highestNet = 0
        self.lowestNet = 0

        # Bankroll tracking
        self.startingBankroll = 0
        self.highestBankroll = 0
        self.lowestBankroll = 0
        self.peakBankroll = 0
        self.biggestDrawdown = 0

        # Money tracking
        self.totalBankroll = 0
        self.totalWagered = 0

        # Decision stats
        self.hits = 0
        self.stands = 0
        self.doubles = 0
        self.splits = 0
        self.surrenders = 0
        self.insuranceTaken = 0

        # Graph/history data
        self.roundHistory = []
        self.bankrollHistory = []
        self.netHistory = []
        self.trueCountHistory = []
        self.runningCountHistory = []

        self.evHistory = []
        self.totalWageredHistory = []

        # Dealer upcard stats
        self.dealerUpcardCount = {
            card: 0 for card in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        }

        self.dealerPlayedByUpcard = {
            card: 0 for card in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        }

        self.dealerBustByUpcard = {
            card: 0 for card in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        }


    def set_starting_bankroll(self, bankroll):
        self.startingBankroll = bankroll
        self.highestBankroll = bankroll
        self.lowestBankroll = bankroll
        self.peakBankroll = bankroll
        self.biggestDrawdown = 0
        self.totalBankroll = bankroll

    def update_net_stats(self):
        if self.net > self.highestNet:
            self.highestNet = self.net

        if self.net < self.lowestNet:
            self.lowestNet = self.net

    def update_bankroll_stats(self, bankroll):
        if bankroll > self.highestBankroll:
            self.highestBankroll = bankroll

        if bankroll < self.lowestBankroll:
            self.lowestBankroll = bankroll

        if bankroll > self.peakBankroll:
            self.peakBankroll = bankroll

        currentDrawdown = self.peakBankroll - bankroll

        if currentDrawdown > self.biggestDrawdown:
            self.biggestDrawdown = currentDrawdown

    def record_round(self, bankroll, runningCount, trueCount):
        self.roundHistory.append(self.roundsPlayed)
        self.bankrollHistory.append(bankroll)
        self.netHistory.append(self.net)
        self.runningCountHistory.append(runningCount)
        self.trueCountHistory.append(trueCount)
        self.totalWageredHistory.append(self.totalWagered)

        if self.totalWagered > 0:
            evPerDollar = self.net / self.totalWagered
        else:
            evPerDollar = 0

        self.evHistory.append(evPerDollar)

    def print_results(self, bankroll, displayCard, settings=None, use_card_counting=False, base_bet=10):
        if self.roundsPlayed == 0 or self.totalWagered == 0:
            print("No simulation results to show.")
            return

        playerEdge = self.net / self.totalWagered * 100
        houseEdge = -playerEdge
        rtp = 100 + playerEdge
        averageBet = self.totalWagered / self.roundsPlayed
        evPerDollar = self.net / self.totalWagered
        evPerHand = self.net / self.roundsPlayed
        totalResolvedHands = self.wins + self.losses + self.ties


        print()

        print()
        print("=== SIMULATION SETTINGS ===")
        print(f"Base bet: ${base_bet:.2f}")
        print(f"Card counting: {'On' if use_card_counting else 'Off'}")

        if settings is not None:
            print(f"Number of decks: {settings.num_decks}")
            print(f"Dealer hits soft 17: {'Yes' if settings.dealer_hits_soft_17 else 'No'}")
            print(f"Blackjack payout: {settings.blackjack_payout}:1")
            print(f"Surrender allowed: {'Yes' if settings.surrender_allowed else 'No'}")
            print(f"Double after split: {'Yes' if settings.double_after_split else 'No'}")

        print()

        print("=== SIMULATION RESULTS ===")
        print(f"Rounds played: {self.roundsPlayed}")
        print(f"Resolved player hands: {totalResolvedHands}")
        print(f"Wins: {self.wins}")
        print(f"Losses: {self.losses}")
        print(f"Ties: {self.ties}")
        print(f"Player Blackjacks: {self.playerBlackJacks}")
        print(f"Dealer Blackjacks: {self.dealerBlackJacks}")
        print(f"Push on Blackjacks: {self.pushOnBlackJacks}")
        print(f"Player Busts: {self.playerBusts}")
        print(f"Dealer Busts: {self.dealerBusts}")
        print(f"Net: ${self.net:.2f}")
        print(f"Highest Net: ${self.highestNet:.2f}")
        print(f"Lowest Net: ${self.lowestNet:.2f}")

        print()
        print("=== BANKROLL STATS ===")
        print(f"Starting bankroll: ${self.startingBankroll:.2f}")
        print(f"Final bankroll: ${bankroll:.2f}")
        print(f"Highest bankroll: ${self.highestBankroll:.2f}")
        print(f"Lowest bankroll: ${self.lowestBankroll:.2f}")
        print(f"Biggest bankroll drawdown: ${self.biggestDrawdown:.2f}")

        print()
        print("=== EV / RETURN STATS ===")
        print(f"Win rate: {self.wins / totalResolvedHands * 100:.2f}%")
        print(f"Loss rate: {self.losses / totalResolvedHands * 100:.2f}%")
        print(f"Push rate: {self.ties / totalResolvedHands * 100:.2f}%")
        print(f"Average bet size: ${averageBet:.2f}")
        print(f"EV per $1 wagered: ${evPerDollar:.4f}")
        print(f"EV per hand: ${evPerHand:.4f}")
        print(f"Player edge: {playerEdge:.4f}%")
        print(f"House edge: {houseEdge:.4f}%")
        print(f"Return percentage / RTP: {rtp:.4f}%")
        print(f"Total wagered: ${self.totalWagered:.2f}")

        print()
        print("=== DECISION STATS ===")
        print(f"Hits: {self.hits}")
        print(f"Stands: {self.stands}")
        print(f"Double downs: {self.doubles}")
        print(f"Splits: {self.splits}")
        print(f"Surrenders: {self.surrenders}")
        print(f"Insurance taken: {self.insuranceTaken}")
        print(f"Insurance rate: {self.insuranceTaken / self.roundsPlayed * 100:.2f}%")
        print(f"Double-down rate: {self.doubles / self.roundsPlayed * 100:.2f}%")
        print(f"Split rate: {self.splits / self.roundsPlayed * 100:.2f}%")
        print(f"Surrender rate: {self.surrenders / self.roundsPlayed * 100:.2f}%")

        print()
        print("=== DEALER BUST RATE BY UPCARD WHEN DEALER PLAYS ===")

        for card in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
            if self.dealerPlayedByUpcard[card] > 0:
                bustRate = (
                    self.dealerBustByUpcard[card]
                    / self.dealerPlayedByUpcard[card]
                    * 100
                )
                print(
                    f"{displayCard(card)}: {bustRate:.2f}% "
                    f"({self.dealerBustByUpcard[card]}/{self.dealerPlayedByUpcard[card]})"
                )