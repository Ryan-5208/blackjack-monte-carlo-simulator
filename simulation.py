from cards import displayCard
from game import reset_game_state, play_round, get_bankroll, set_bankroll, set_verbose, set_card_counting, set_settings, stats

def run_simulation(
    num_rounds=100000,
    use_card_counting=False,
    starting_bankroll=100000,
    base_bet=10,
    settings=None,
    show_results=True
):
    if settings is not None:
        set_settings(settings)

    reset_game_state()

    set_bankroll(starting_bankroll)
    stats.set_starting_bankroll(get_bankroll())
    set_card_counting(use_card_counting)
    set_verbose(False)

    for _ in range(num_rounds):
        play_round(
            autoPlay=True,
            autoBet=True,
            autoIns=True,
            baseBet=base_bet
        )
    if show_results:
        stats.print_results(
            get_bankroll(), 
            displayCard,     
            settings=settings,
            use_card_counting=use_card_counting,
            base_bet=base_bet
        )

    return stats