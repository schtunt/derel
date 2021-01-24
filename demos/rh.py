#!/usr/bin/env python3

import os, sys, locale
import csv, requests

import numpy as np
import dateutil.parser as dtp

from collections import defaultdict, namedtuple
from datetime import datetime, timedelta

mulla = lambda amount: locale.currency(amount, grouping=True)
flt = np.single
ZERO = 1e-5

API_MARKETSTACK = { 'access_key': os.environ['API_MARKETSTACK_KEY'], }
DB_MARKETSTACK = {}
def marketstack(ticker):
    global DB_MARKETSTACK

    if ticker not in DB_MARKETSTACK:
        api_result = requests.get(
            'http://api.marketstack.com/v1/tickers/%s/eod?limit=1' % ticker,
            API_MARKETSTACK
        )
        api_response = api_result.json()
        DB_MARKETSTACK[ticker] = api_response['data']

    return DB_MARKETSTACK[ticker]

class Lot:
    ident = 0

    def __init__(self, ticker, side, qty, price, timestamp):
        self.ident = Lot.ident
        Lot.ident += 1

        self.side = side
        self.ticker = ticker
        self.price = flt(price)
        self.qty = flt(qty)
        self.timestamp = timestamp
        self.ties = []

    def __repr__(self):
        string = '#%05d %s:%-4s %8.2f x %10s = %10s @ %s' % (
            self.ident,
            self.ticker.symbol,
            self.side,
            self.qty,
            mulla(self.price),
            mulla(self.price * self.qty),
            self.timestamp,
        )

        return '<%s>' % string

    def tie(self, conn):
        self.ties.append(conn)

    @property
    def signum(self):
        return -1 if self.side == 'buy' else +1

    @property
    def unsettled(self):
        '''
        For a buy lot, this is how many remaining units are left in this lot.
        For a sell lot, this is how many outstanding units are unaccounted for.

        Different things, but the same underlying calculation.
        '''
        return self.qty - sum([conn.qty for conn in self.ties])

    @property
    def symbol(self):
        return self.ticker.symbol

class LotConnector:
    @classmethod
    def settle(self, fifo, index):
        sold = fifo[-1]
        assert sold.side == 'sell'

        l = None
        qty = sold.qty
        while qty > ZERO:
            l = LotConnector(sold, fifo, index)
            qty -= l.qty

            while index < len(fifo) and (
                fifo[index].side == 'sell' or fifo[index].unsettled <= ZERO
            ):
                index += 1

        return index

    def __init__(self, sold, fifo, index):
        self.sold, self.bought = sold, fifo[index]
        self.qty = min((self.sold.unsettled, self.bought.unsettled))
        self.sold.tie(self)
        self.bought.tie(self)

    def __repr__(self):
        return '%s <--(x%0.5f)--> %s' % (
            self.sold,
            self.qty,
            self.bought,
        )


class StockFIFO:
    @property
    def qty(self):
        return sum([-t.signum * t.qty for t in self.fifo])

    @property
    def timestamp(self):
        return self.fifo[-1].timestamp

    @property
    def value(self):
        return sum([t.price * t.unsettled for t in self.fifo if t.side == 'buy'])

    @property
    def average(self):
        return self.value / self.qty if self.value and self.qty else 0

    def __init__(self, symbol):
        self.symbol = symbol
        self.pointer = 0
        self.fifo = []

    def __getitem__(self, i):
        return self.fifo[i]

    def __repr__(self):
        return '<StockFIFO:%-5s x %8.2f @ %s>' % (
            self.symbol,
            self.qty,
            mulla(self.average),
        )

    def summarize(self, fetch=False):
        print('#' * 80)

        sfmt = lambda qty, lot: '%10.5f %s' % (qty, lot)
        for lot in self.fifo:
            if lot.side == 'buy': continue

            # The buys
            cb = 0
            for tie in lot.ties:
                cb -= tie.qty * tie.bought.price
                print(sfmt(tie.qty, tie.bought))

            # The sell
            print(sfmt(lot.qty, lot))
            cb += lot.qty * lot.price

            print("Cost Basis: %s" % mulla(cb))
            print()

        # Remaining buys (without sells)
        for lot in self.fifo[self.pointer:]:
            print(sfmt(lot.qty, lot))

        print("Cost : %10.5f x %s = %s" % (
            self.qty, mulla(self.average), mulla(self.value)
        ))
        if fetch and self.qty > ZERO:
            data = marketstack(self.symbol)
            if data:
                price = flt(data['eod'][0]['close'])
                equity = self.qty * price
                print("Value: %10.5f x %s = %s" % (
                    self.qty, mulla(price), mulla(equity)
                ))
                print("Position: %s" % (
                    mulla(equity - self.value)
                ))

        print()

    def push(self, qty, price, side, timestamp):
        self.fifo.append(
            Lot(
                self,
                side,
                flt(qty),
                price,
                dtp.parse(timestamp),
            )
        )

        if side == 'sell':
            self.pointer = LotConnector.settle(self.fifo, self.pointer)

class Account:
    def __init__(self):
        self.portfolio = {}

    def __getitem__(self, symbol):
        if symbol not in self.portfolio:
            self.portfolio[symbol] = StockFIFO(symbol)

        return self.portfolio[symbol]

    def slurp(self, csvfile):
        with open(csvfile, newline='') as fh:
            transactions = csv.reader(fh, delimiter=',', quotechar='"')
            header = next(transactions)
            for price, timestamp, fees, qty, side, name, symbol, otype in transactions:
                self[symbol].push(
                    qty, price, side, timestamp
                )

    def tickers(self):
        for ticker, stock in self.portfolio.items():
            yield ticker, stock

def main():
    locale.setlocale(locale.LC_ALL, '')

    account = Account()
    account.slurp('rh.csv')

    if len(sys.argv) > 1:
        tickers = sys.argv[1].split(',')
        for ticker in tickers:
            stock = account[ticker]
            stock.summarize(fetch=True)
    else:
        for ticker, stock in account.tickers():
            stock.summarize()

if __name__ == '__main__':
    main()
