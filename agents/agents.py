import numpy as np
import random

from helpers.helpers import utility_function

class HedgeFund:

    def __init__(
            self, 
            fundamental_price,
            momentum_weight,
            contrarian_weight,
            g,
    ):
        # any negative value of stocks indicates short positions.
        # short positions can be covered by buying back a stock at a certain price.
        self.stocks = -500
        self.wealth = 500*20
        self.opinion = fundamental_price
        self.momentum_weight = momentum_weight
        self.contrarian_weight = contrarian_weight
        self.g = g
        self.participation = True

    def set_action(self, stock_price_history):
        momentum_change = -1 * self.g * (stock_price_history[-1] - stock_price_history[-2])
        
        if self.stocks <= 0:
            utility_gamble = utility_function(self.wealth, -1 * self.stocks, stock_price_history[-1], momentum_change)
            print(utility_gamble)
            if utility_gamble < 0:
                self.action = 'close positions'
                self.participation = False
            else:
                self.action = 'short'
        
    def set_demand(self, stock_price):
        if self.action == 'short':    
            self.demand = -1 * (stock_price - self.opinion)

        if self.action == 'close positions':
            print('Hedge fund closed positions')
            self.demand = -1 * self.stocks

    def execute_trade(self, stock_price):
        self.stocks += self.demand
        self.wealth -= self.demand * stock_price

class RedditTrader:
    
    def __init__(self, is_committed, commitment_threshold, influence_factor):
        self.stocks = 0
        self.is_committed = is_committed
        self.commitment_threshold = commitment_threshold
        self.influence_factor = influence_factor
        if self.is_committed:
            self.commitment = 1
        else:
            self.commitment = np.random.normal(0.1, 0.1)
            if self.commitment < 0:
                self.commitment = 0

    def update_commitment(self, number_of_connections):
        for _ in range(number_of_connections):
            # every new connection increases the commitment of the agent by the influence factor
            self.commitment += self.influence_factor
        if self.commitment > self.commitment_threshold:
            self.is_committed = True

    def set_demand(self):
        self.demand = self.commitment

    def set_dump_demand(self):
        self.demand = -1 * self.stocks

    def trade(self):
        self.stocks += self.demand


class Market:

    def __init__(self, start_price, committed_traders, all_traders):
        self.price_history = [start_price + 1, start_price]
        self.price = start_price
        self.committed_traders = committed_traders
        self.all_traders = all_traders
        self.commitment_history = [sum([trader.commitment for trader in all_traders])]
        self.daily_return_history = []
        self.trading_day = 0

    def activate_hedge_funds(self, all_hedge_funds, participation_probability):
        self.participating_hedges = []
        for hedgefund in all_hedge_funds:
            # will be set to False once hedgefund closes its short positions
            if hedgefund.participation == True:
                print(f'Trading day: {self.trading_day}')
                hedgefund.set_action(self.price_history)
                # we want to close positions for all hedgefunds that need to, rather than by chance
                if hedgefund.action == 'close positions':
                    hedgefund.set_demand(self.price)
                    hedgefund.execute_trade(self.price)
                    self.participating_hedges.append(hedgefund)
                # for all hedgefunds that would short, obtain the ones that participate
                if hedgefund.action == 'short':
                    p = random.uniform(0, 1)
                    if p < participation_probability:
                        hedgefund.set_demand(self.price)
                        hedgefund.execute_trade(self.price)
                        self.participating_hedges.append(hedgefund)     

    def activate_committed_traders(
        self, 
        participation_probability, 
        posting_probability, 
        dump_percentage, 
        dump_probability
    ):
        self.participating_traders = []
        self.posted_traders = []
        for trader in self.committed_traders:
            return_percentage = (
                (self.price_history[-1] - self.price_history[-2]) /
                 self.price_history[-2] * 100 
            )
            if return_percentage > dump_percentage:
                p = random.uniform(0, 1)
                if p < dump_probability:
                    trader.set_dump_demand()
                    trader.trade()
                    trader.commitment = 0
                    self.participating_traders.append(trader)
            else:
                p = random.uniform(0, 1)
                r = random.uniform(0, 1)
                if p < participation_probability:
                    trader.set_demand()
                    trader.trade()
                    self.participating_traders.append(trader)
                    if r < posting_probability:
                        self.posted_traders.append(trader)
    
    def update_trader_commitment(self, read_post_probability):
        for trader in self.all_traders:
            # only if trader has not reached maximum commitment
            if trader.commitment < 1: 
                new_connections = 0
                for _ in range(0, len(self.posted_traders)):
                    p = random.uniform(0,1)
                    if p < read_post_probability:
                        new_connections += 1
                if new_connections > 0:
                    trader.update_commitment(new_connections)
                if trader not in self.committed_traders:
                    self.committed_traders.append(trader)

    def update_price(self):
        v = np.random.normal(0, 0.05)
        excess_demand = abs(v) * (sum([hedge.demand for hedge in self.participating_hedges]) + 
                                sum([trader.demand for trader in self.participating_traders])) 
        self.price = self.price + excess_demand
        if self.price < 0:
            self.price = 0
        self.price_history.append(self.price)
        self.trading_day += 1
        daily_return = (self.price_history[-1] - self.price_history[-2]) / self.price_history[-2]
        self.daily_return_history.append(daily_return)
    
    def store_total_commitment(self, all_traders):
        total_commitment = sum([trader.commitment for trader in all_traders])
        self.commitment_history.append(total_commitment)