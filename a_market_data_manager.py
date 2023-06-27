from a_symbol_handler import ISymbolHandler, BaseSymbolHandler, OKXSymbolHandler
import concurrent.futures
import threading
from pynput import keyboard
import os

class MarketDataManager:
    '''
    Symbols is list of strings like 'BTC-USDT'
    Types is list of strings either 'live' or 'hist'
    '''
    def __init__(self, symbols: list[str], types: list[str]):
        self.symbol_handlers = {}
        for symbol,type in zip(symbols, types):
            self.add_symbol_handler(symbol, type)


    def add_symbol_handler(self, symbol, type):
        new_symbol_handler = self.create_symbol_handler(symbol, type)
        if not isinstance(new_symbol_handler, ISymbolHandler):
            raise ValueError
        else:
            self.symbol_handlers[symbol] = new_symbol_handler
    
    def start(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.symbol_handlers)+1) as executor:
            for symbol_handler in self.symbol_handlers.values():
                executor.submit(symbol_handler.start)
            listener = keyboard.Listener(on_press=self.on_press)
            executor.submit(listener.start)   
    
    def get_orderbook(self, symbol):
        return self.symbol_handlers[symbol].get_orderbook()
    
    def create_symbol_handler(self):
        raise NotImplementedError
    
    def on_press(self, key):
        if key == keyboard.Key.esc:
            os._exit(0)

class OkxDataManager(MarketDataManager):
    def create_symbol_handler(self, symbol, type):
        return OKXSymbolHandler(symbol, type)
