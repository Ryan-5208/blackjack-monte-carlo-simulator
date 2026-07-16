class GameSettings:
    def __init__(
            self, 
            num_decks=6, 
            dealer_hits_soft_17=True, 
            blackjack_payout=1.5, 
            surrender_allowed=True, 
            double_after_split=True
        ):
            self.num_decks = num_decks
            self.dealer_hits_soft_17 = dealer_hits_soft_17
            self.blackjack_payout = blackjack_payout
            self.surrender_allowed = surrender_allowed
            self.double_after_split = double_after_split