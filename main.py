from game import run_game
from simulation import run_simulation
from settings import GameSettings
from cards import displayCard
from graphs import (
    plot_bankroll,
    plot_net,
    plot_ev_by_hands,
    plot_true_count,
    plot_dealer_bust_by_upcard,
    plot_decisions,
    plot_house_edge_by_rules
)

def run_rule_set_comparison(hands, starting_bankroll, base_bet):
    rule_sets = [
        (
            "6D H17 3:2 Surrender DAS",
            GameSettings(
                num_decks=6,
                dealer_hits_soft_17=True,
                blackjack_payout=1.5,
                surrender_allowed=True,
                double_after_split=True
            )
        ),
        (
            "6D S17 3:2 Surrender DAS",
            GameSettings(
                num_decks=6,
                dealer_hits_soft_17=False,
                blackjack_payout=1.5,
                surrender_allowed=True,
                double_after_split=True
            )
        ),
        (
            "6D H17 6:5 No Surrender DAS",
            GameSettings(
                num_decks=6,
                dealer_hits_soft_17=True,
                blackjack_payout=1.2,
                surrender_allowed=False,
                double_after_split=True
            )
        ),
        (
            "8D H17 3:2 No Surrender No DAS",
            GameSettings(
                num_decks=8,
                dealer_hits_soft_17=True,
                blackjack_payout=1.5,
                surrender_allowed=False,
                double_after_split=False
            )
        )
    ]

    rule_names = []
    house_edges = []

    for name, rule_settings in rule_sets:
        rule_results = run_simulation(
            num_rounds=hands,
            use_card_counting=False,
            starting_bankroll=starting_bankroll,
            base_bet=base_bet,
            settings=rule_settings,
            show_results=False
        )

        player_edge = rule_results.net / rule_results.totalWagered * 100
        house_edge = -player_edge

        rule_names.append(name)
        house_edges.append(house_edge)

    plot_house_edge_by_rules(rule_names, house_edges)

def choose_graphs(results):
    print()
    print("Which graphs do you want?")
    print("1. Bankroll over time")
    print("2. Net profit over time")
    print("3. EV by hands simulated")
    print("4. True count over time")
    print("5. Dealer bust rate by upcard")
    print("6. Decision frequency")
    print("A. All graphs")
    print("N. No graphs")
    print()

    graph_choice = input("Enter choices separated by commas, like 1,3,5: ").lower()
    graph_choice = graph_choice.replace(" ", "")

    if graph_choice in ["n", "no", "none"]:
        return

    if graph_choice in ["a", "all"]:
        selected = ["1", "2", "3", "4", "5", "6"]
    else:
        selected = graph_choice.split(",")

    if "1" in selected:
        plot_bankroll(results)

    if "2" in selected:
        plot_net(results)

    if "3" in selected:
        plot_ev_by_hands(results)

    if "4" in selected:
        plot_true_count(results)

    if "5" in selected:
        plot_dealer_bust_by_upcard(results, displayCard)

    if "6" in selected:
        plot_decisions(results)


def main():
    mode = input("Choose mode: (G)ame or (S)imulation: ")

    if mode.lower() in ["g", "game"]:
        run_game()

    elif mode.lower() in ["s", "simulation", "sim"]:
        try:
            hands = int(input("How many hands should be simulated? "))
            if hands <= 0:
                print("Enter a positive whole number.")
                return

            starting_bankroll = float(input("Starting bankroll: $"))
            base_bet = float(input("Base bet amount: $"))

            if starting_bankroll <= 0 or base_bet <= 0:
                print("Bankroll and bet must be positive.")
                return
            else:
                while True:
                    count_choice = input("Use card counting? (Y/N): ").lower()

                    if count_choice in ["y", "yes"]:
                        use_card_counting = True
                        break

                    elif count_choice in ["n", "no"]:
                        use_card_counting = False
                        break

                    else:
                        print("Please enter Y or N.")

                num_decks = int(input("Number of decks: "))

                while True:
                    h17_choice = input("Dealer hits soft 17? (Y/N): ").lower()
                    if h17_choice in ["y", "yes"]:
                        dealer_hits_soft_17 = True
                        break
                    elif h17_choice in ["n", "no"]:
                        dealer_hits_soft_17 = False
                        break
                    else:
                        print("Please enter Y or N.")

                blackjack_payout = float(input("Blackjack payout? Use 1.5 for 3:2, 1.2 for 6:5: "))

                while True:
                    surrender_choice = input("Allow surrender? (Y/N): ").lower()
                    if surrender_choice in ["y", "yes"]:
                        surrender_allowed = True
                        break
                    elif surrender_choice in ["n", "no"]:
                        surrender_allowed = False
                        break
                    else:
                        print("Please enter Y or N.")

                while True:
                    das_choice = input("Allow double after split? (Y/N): ").lower()
                    if das_choice in ["y", "yes"]:
                        double_after_split = True
                        break
                    elif das_choice in ["n", "no"]:
                        double_after_split = False
                        break
                    else:
                        print("Please enter Y or N.")

                settings = GameSettings(
                    num_decks=num_decks,
                    dealer_hits_soft_17=dealer_hits_soft_17,
                    blackjack_payout=blackjack_payout,
                    surrender_allowed=surrender_allowed,
                    double_after_split=double_after_split
                )

                results = run_simulation(
                    num_rounds=hands,
                    use_card_counting=use_card_counting,
                    starting_bankroll=starting_bankroll,
                    base_bet=base_bet,
                    settings=settings
                )
                
                choose_graphs(results)

                rules_choice = input("Run house edge comparison across rule sets? (Y/N): ").lower()
                if rules_choice in ["y", "yes"]:
                    run_rule_set_comparison(hands, starting_bankroll, base_bet)

        except ValueError:
            print("Enter a valid whole number.")
    else:
        print("Invalid mode.")

if __name__ == "__main__":
    main()





