#!/usr/bin/python3
# -*- coding: iso-8859-1 -*
""" Python starter bot for the Crypto Trader games, from ex-Riddles.io """
__version__ = "1.0"

import sys
import numpy as np
import pandas as pd
import matplotlib as plt
from math import sqrt

class Bot:
    def __init__(self):
        self.botState = BotState()
        self.Chart = Chart()

    def run(self):
        while True:
            reading = input()
            if len(reading) == 0:
                continue
            self.parse(reading)

    def calcul_sma(self):
        s, x = 0.0, 0
        for i in self.Chart.closes:
            if x >= 20:
                break
            print(i)
            s += float(i)
            x += 1
        return (s / 20)
    
    def ecart_type_bol(self):
        res, s, x = 0.0, self.calcul_sma(), 0
        for (i, j) in zip(self.Chart.opens, self.Chart.closes):
            if (x >= 20):
                break
            res += ((i - j) ** 2) - s
            x += 1
        return (sqrt(res / 20))
    
    def type_bande_bol(self, check):
        if check == True:
            self.botState.Upper.append(self.calcul_sma() + (2 * self.ecart_type_bol()))
            return (self.calcul_sma() + (2 * self.ecart_type_bol()))
        else:
            self.botState.Lower.append(self.calcul_sma() - (2 * self.ecart_type_bol()))
            return (self.calcul_sma() - (2 * self.ecart_type_bol()))

    def RSI_band(self):
        value = self.Chart.closes.diff()
        gain = value.where(value > 0, 0)
        loss = value.where(value < 0, 0)
        avg_gain = gain.mean()
        avg_loss = loss.mean()
        my_rsi = 100 - (100 / (1 + (avg_gain / avg_loss)))
        self.botState.data['RSI'] = my_rsi
        self.botState.data['Overb'] = 70
        self.botState.data['Overs'] = 30
        return (self.data)
    
    def trade_strategy(self):
        pos = 0
        for a in range(len(self.Chart.closes)):
            if self.Chart.closes[a] < self.botState.Lower[a] and self.botState.data['RSI'][a] < self.botState.data['Overs'][a] and pos == 0:
                pos = 1
                print("Bot: Buy " + self.Chart.closes['pair'][0] + str(self.Chart.closes[a]))
            elif self.Chart.closes[a] > self.botState.Upper[a] and self.botState.data['RSI'][a] > self.botState.data['Overb'][a] and pos == 1:
                pos = 0
                print("Bot: sell " + self.Chart.closes['pair'][0] + str(self.Chart.closes[a]))
        return (0)

    def parse(self, info: str):
        tmp = info.split(" ")
        if tmp[0] == "settings":
            self.botState.update_settings(tmp[1], tmp[2])
        if tmp[0] == "update":
            if tmp[1] == "game":
                self.botState.update_game(tmp[2], tmp[3])
        if tmp[0] == "action":
            self.trade_strategy()
            #This won't work every time, but it works sometimes!
            dollars = self.botState.stacks["USDT"]
            current_closing_price = self.botState.charts["USDT_BTC"].closes[-1]
            affordable = dollars / current_closing_price
            print(f'My stacks are {dollars}. The current closing price is {current_closing_price}. So I can afford {affordable}', file=sys.stderr)
            if dollars < 100:
                print("no_moves", flush=True)
            else:
                print(f'buy USDT_BTC {0.5 * affordable}', flush=True)


class Candle:
    def __init__(self, format, intel):
        tmp = intel.split(",")
        for (i, key) in enumerate(format):
            value = tmp[i]
            if key == "pair":
                self.pair = value
            if key == "date":
                self.date = int(value)
            if key == "high":
                self.high = float(value)
            if key == "low":
                self.low = float(value)
            if key == "open":
                self.open = float(value)
            if key == "close":
                self.close = float(value)
            if key == "volume":
                self.volume = float(value)

    def __repr__(self):
        return str(self.pair) + str(self.date) + str(self.close) + str(self.volume)


class Chart:
    def __init__(self):
        self.dates = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.volumes = []
        self.indicators = {}

    def add_candle(self, candle: Candle):
        self.dates.append(candle.date)
        self.opens.append(candle.open)
        self.highs.append(candle.high)
        self.lows.append(candle.low)
        self.closes.append(candle.close)
        self.volumes.append(candle.volume)


class BotState:
    def __init__(self):
        self.timeBank = 0
        self.maxTimeBank = 0
        self.timePerMove = 1
        self.candleInterval = 1
        self.candleFormat = []
        self.candlesTotal = 0
        self.candlesGiven = 0
        self.initialStack = 0
        self.transactionFee = 0.1
        self.date = 0
        self.stacks = dict()
        self.charts = dict()
        self.Lower = []
        self.Upper = []
        self.data = {"RSI": [], "Overb": [], "Overs": []}

    def update_chart(self, pair: str, new_candle_str: str):
        if not (pair in self.charts):
            self.charts[pair] = Chart()
        new_candle_obj = Candle(self.candleFormat, new_candle_str)
        self.charts[pair].add_candle(new_candle_obj)

    def update_stack(self, key: str, value: float):
        self.stacks[key] = value

    def update_settings(self, key: str, value: str):
        if key == "timebank":
            self.maxTimeBank = int(value)
            self.timeBank = int(value)
        if key == "time_per_move":
            self.timePerMove = int(value)
        if key == "candle_interval":
            self.candleInterval = int(value)
        if key == "candle_format":
            self.candleFormat = value.split(",")
        if key == "candles_total":
            self.candlesTotal = int(value)
        if key == "candles_given":
            self.candlesGiven = int(value)
        if key == "initial_stack":
            self.initialStack = int(value)
        if key == "transaction_fee_percent":
            self.transactionFee = float(value)

    def update_game(self, key: str, value: str):
        if key == "next_candles":
            new_candles = value.split(";")
            self.date = int(new_candles[0].split(",")[1])
            for candle_str in new_candles:
                candle_infos = candle_str.strip().split(",")
                self.update_chart(candle_infos[0], candle_str)
        if key == "stacks":
            new_stacks = value.split(",")
            for stack_str in new_stacks:
                stack_infos = stack_str.strip().split(":")
                self.update_stack(stack_infos[0], float(stack_infos[1]))


if __name__ == "__main__":
    mybot = Bot()
    mybot.run()
