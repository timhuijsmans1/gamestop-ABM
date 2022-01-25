import matplotlib.pyplot as plt
import seaborn as sns

sns.set()

from agents.agents import *
from helpers.helpers import *


def run():
    all_hedge_funds = [HedgeFund(fundamental_price, p_momentum, p_contrarian, g) for _ in range(number_of_hedgefunds)]
    committed_traders = [RedditTrader(True, commitment_threshold, influence_factor) for _ in range(number_of_init_committed)]
    non_committed_traders = [RedditTrader(False, commitment_threshold, influence_factor) for _ in range(number_of_reddittraders - number_of_init_committed)]
    all_traders = committed_traders + non_committed_traders
    market = Market(start_price, committed_traders, all_traders)
    for _ in range(0, market_days, 1):
        market.activate_hedge_funds(all_hedge_funds, hedge_participation_probability)
        market.activate_committed_traders(reddit_participation_probability, reddit_post_probability, dump_percentage, dump_probability)
        market.update_trader_commitment(read_post_probability)
        market.update_price()
        market.store_total_commitment(all_traders)
    return market

def plot_price_results(market):
    price = market.price_history
    commitment = market.commitment_history
    plt.figure(dpi=100)
    plt.plot(price[1:], '-o', label='GME price (USD)')
    plt.plot(commitment, '-o', label='wsb total commitment')
    plt.title('Trader commitment and GME price modelled after the short squeeze')
    plt.xlabel('Trading days')
    plt.legend()
    plt.show()

def plot_return_results(market):
    commitment = market.commitment_history[1:]
    daily_return = market.daily_return_history
    t = list(range(len(daily_return)))

    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Trading days')
    ax1.set_ylabel('Commitment', color=color)
    ax1.plot(t, commitment, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('Daily return', color=color)  # we already handled the x-label with ax1
    ax2.plot(t, daily_return, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()

if __name__ == '__main__':

    # hedgefund parameters
    number_of_hedgefunds = 10 
    fundamental_price = 0
    p_momentum = .5
    p_contrarian = .5
    g = -.13
    hedge_participation_probability = 0.2

    # reddit trader parameters
    number_of_reddittraders = 200
    number_of_init_committed = 5
    commitment_threshold = 0.7
    influence_factor = 0.05
    dump_percentage = 250
    dump_probability = 0.7
    reddit_participation_probability = 0.2 # this should depend on current amount of stock and maybe, more stock is less likely to participate again
    reddit_post_probability = 0.2 # this should depend on commitment, more committed agents will be more likely to post
    read_post_probability = 0.1 # this should depend on commitment, more committed agents will be reading more posts

    # market parameters
    start_price = 20
    market_days = 50
    
    market = run()
    plot_price_results(market)
    plot_return_results(market)
    
