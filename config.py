"""
Configuration file for Trading Tool
Contains all settings and asset definitions
"""

import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_DATA_FILE = os.path.join(BASE_DIR, 'jawasc', 'data.json')

# Asset Symbols
ASSETS = {
    'gold': {
        'name': 'Gold',
        'symbol': 'GC=F',
        'yahoo_symbol': 'GC=F',
        'type': 'commodity'
    },
    'silver': {
        'name': 'Silver', 
        'symbol': 'SI=F',
        'yahoo_symbol': 'SI=F',
        'type': 'commodity'
    },
    'stocks': {
        'name': 'Stock Market',
        'symbol': 'SPY',
        'yahoo_symbol': 'SPY',
        'type': 'stock',
        'indices': ['^GSPC', '^IXIC', '^HSI', '^JKSE']  # S&P500, Nasdaq, HSI, IHSG
    },
    'etfs': {
        'name': 'ETF',
        'symbols': ['GLD', 'SLV', 'SPY', 'IVV', 'VOO', 'QQQ', 'IWM', 'EEM', 'VNQ', 'GDX'],
        'type': 'etf'
    }
}

# Trading Parameters
TRADING_PARAMS = {
    'rsi_oversold': 30,
    'rsi_overbought': 70,
    'rsi_period': 14,
    'sma_short': 20,
    'sma_long': 50,
    'ema_short': 12,
    'ema_long': 26,
    'macd_signal': 9,
    'risk_threshold': 0.02,  # 2% risk per trade
    'min_confidence': 60     # Minimum confidence for signal
}

# Timeframes
TIMEFRAMES = {
    '1m': '1 minute',
    '5m': '5 minutes', 
    '15m': '15 minutes',
    '1h': '1 hour',
    '1d': '1 day',
    '1wk': '1 week'
}

# Default settings
DEFAULT_PERIOD = '1mo'
DEFAULT_INTERVAL = '1d'

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    
    @staticmethod
    def green(text):
        return f"{Colors.GREEN}{text}{Colors.ENDC}"
    
    @staticmethod
    def red(text):
        return f"{Colors.RED}{text}{Colors.ENDC}"
    
    @staticmethod
    def yellow(text):
        return f"{Colors.YELLOW}{text}{Colors.ENDC}"
    
    @staticmethod
    def blue(text):
        return f"{Colors.BLUE}{text}{Colors.ENDC}"

