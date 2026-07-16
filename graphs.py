import os
import matplotlib.pyplot as plt

os.makedirs("graph_images", exist_ok=True)


def plot_bankroll(results):
    plt.figure()
    plt.plot(results.roundHistory, results.bankrollHistory)
    plt.title("Bankroll Over Time")
    plt.xlabel("Round")
    plt.ylabel("Bankroll ($)")
    plt.grid(True)
    plt.savefig("graph_images/bankroll_over_time.png", dpi=300, bbox_inches="tight")
    plt.show()


def plot_net(results):
    plt.figure()
    plt.plot(results.roundHistory, results.netHistory)
    plt.title("Net Profit Over Time")
    plt.xlabel("Round")
    plt.ylabel("Net Profit ($)")
    plt.grid(True)
    plt.savefig("graph_images/net_profit_over_time.png", dpi=300, bbox_inches="tight")
    plt.show()

def plot_ev_by_hands(results):
    plt.figure()
    plt.plot(results.roundHistory, results.evHistory)
    plt.axhline(0, linestyle="--", linewidth=1)
    plt.title("EV Convergence Over Time")
    plt.xlabel("Hands Simulated")
    plt.ylabel("EV per $1 Wagered")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("graph_images/ev_by_hands.png", dpi=300, bbox_inches="tight")
    plt.show()

def plot_ev_by_hands_zoomed(results, max_hands=2500):
    rounds = []
    evs = []

    for r, ev in zip(results.roundHistory, results.evHistory):
        if r <= max_hands:
            rounds.append(r)
            evs.append(ev)

    plt.figure()
    plt.plot(rounds, evs)
    plt.axhline(0, linestyle="--", linewidth=1)
    plt.title(f"EV During First {max_hands:,} Hands")
    plt.xlabel("Hands Simulated")
    plt.ylabel("EV per $1 Wagered")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("graph_images/ev_by_hands_zoomed.png", dpi=300, bbox_inches="tight")
    plt.show()


def plot_true_count(results):
    plt.figure()
    plt.plot(results.roundHistory, results.trueCountHistory)
    plt.title("True Count Over Time")
    plt.xlabel("Round")
    plt.ylabel("True Count")
    plt.grid(True)
    plt.savefig("graph_images/true_count_over_time.png", dpi=300, bbox_inches="tight")
    plt.show()

def plot_dealer_bust_by_upcard(results, displayCard):
    upcards = []
    bust_rates = []

    for card in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
        if results.dealerPlayedByUpcard[card] > 0:
            upcards.append(displayCard(card))
            rate = results.dealerBustByUpcard[card] / results.dealerPlayedByUpcard[card] * 100
            bust_rates.append(rate)

    plt.figure()
    bars = plt.bar(upcards, bust_rates)
    plt.title("Dealer Bust Rate by Upcard")
    plt.xlabel("Dealer Upcard")
    plt.ylabel("Bust Rate (%)")
    plt.grid(axis="y")

    plt.bar_label(bars, fmt="%.1f%%", padding=3)

    plt.tight_layout()
    plt.savefig("graph_images/dealer_bust_by_upcard.png", dpi=300, bbox_inches="tight")
    plt.show()

def plot_decisions(results):
    decisions = ["Hits", "Stands", "Doubles", "Splits", "Surrenders", "Insurance"]
    counts = [
        results.hits,
        results.stands,
        results.doubles,
        results.splits,
        results.surrenders,
        results.insuranceTaken
    ]

    plt.figure()
    plt.bar(decisions, counts)
    plt.title("Decision Frequency")
    plt.xlabel("Decision")
    plt.ylabel("Count")
    plt.xticks(rotation=30)
    plt.grid(axis="y")
    plt.savefig("graph_images/decision_frequency.png", dpi=300, bbox_inches="tight")
    plt.show()

def plot_final_bankroll_distribution(final_bankrolls):
    plt.figure()
    plt.hist(final_bankrolls, bins=30)
    plt.title("Distribution of Final Bankrolls Over 1,000 Sessions")
    plt.xlabel("Final Bankroll ($)")
    plt.ylabel("Number of Sessions")
    plt.grid(axis="y")
    plt.show()

def plot_house_edge_by_rules(rule_names, house_edges):
    plt.figure(figsize=(10, 6))
    bars = plt.bar(rule_names, house_edges)

    plt.title("House Edge Under Different Rule Sets")
    plt.xlabel("Rule Set")
    plt.ylabel("House Edge (%)")
    plt.xticks(rotation=30, ha="right")
    plt.grid(axis="y")

    plt.bar_label(bars, fmt="%.2f%%", padding=3)

    plt.tight_layout()
    plt.savefig("graph_images/house_edge_by_rules.png", dpi=300, bbox_inches="tight")
    plt.show()

