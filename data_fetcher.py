"""
Data Fetcher Module
Fetches market data for stocks, gold, silver, and ETFs using yfinance
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings

from config import ASSETS, DEFAULT_PERIOD, DEFAULT_INTERVAL, Colors

warnings.filterwarnings('ignore')


class DataFetcher:
    """Main data fetcher class for all asset types"""
    
    def __init__(self, period: str = DEFAULT_PERIOD, interval: str = DEFAULT_INTERVAL):
        self.period = period
        self.interval = interval
        self.cache = {}
    
    def fetch_single(self, symbol: str, period: str = None, interval: str = None) -> Optional[pd.DataFrame]:
        """Fetch data for a single symbol"""
        p = period or self.period
        i = interval or self.interval
        
        try:
            cache_key = f"{symbol}_{p}_{i}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=p, interval=i)
            
            if not df.empty:
                self.cache[cache_key] = df
                return df
            return None
        except Exception as e:
            print(f"{Colors.red(f'Error fetching {symbol}: {e}')}")
            return None
    
    def fetch_gold(self) -> Dict:
        """Fetch gold prices and metadata"""
        print(f"{Colors.yellow('Fetching Gold data...')}")
        
        result = {
            'name': 'Gold',
            'symbol': 'GC=F',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data': None,
            'current_price': None,
            'change': None,
            'change_pct': None,
            'high': None,
            'low': None,
            'volume': None,
            'success': False
        }
        
        df = self.fetch_single('GC=F')
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            result['data'] = df
            result['current_price'] = float(latest['Close'])
            result['change'] = float(latest['Close'] - prev['Close'])
            result['change_pct'] = float(((latest['Close'] - prev['Close']) / prev['Close']) * 100)
            result['high'] = float(latest['High'])
            result['low'] = float(latest['Low'])
            result['volume'] = int(latest['Volume'])
            result['success'] = True
            
            print(f"  Gold: ${result['current_price']:.2f} ({result['change_pct']:+.2f}%)")
        
        return result
    
    def fetch_silver(self) -> Dict:
        """Fetch silver prices and metadata"""
        print(f"{Colors.yellow('Fetching Silver data...')}")
        
        result = {
            'name': 'Silver',
            'symbol': 'SI=F',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data': None,
            'current_price': None,
            'change': None,
            'change_pct': None,
            'high': None,
            'low': None,
            'volume': None,
            'success': False
        }
        
        df = self.fetch_single('SI=F')
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            result['data'] = df
            result['current_price'] = float(latest['Close'])
            result['change'] = float(latest['Close'] - prev['Close'])
            result['change_pct'] = float(((latest['Close'] - prev['Close']) / prev['Close']) * 100)
            result['high'] = float(latest['High'])
            result['low'] = float(latest['Low'])
            result['volume'] = int(latest['Volume'])
            result['success'] = True
            
            print(f"  Silver: ${result['current_price']:.2f} ({result['change_pct']:+.2f}%)")
        
        return result
    
    def fetch_stocks(self, symbols: List[str] = None) -> List[Dict]:
        """Fetch stock data for multiple symbols"""
        if symbols is None:
            symbols = ASSETS['stocks'].get('indices', ['^GSPC', '^IXIC'])
        
        print(f"{Colors.yellow(f'Fetching {len(symbols)} Stock/Index data...')}")
        
        results = []
        for symbol in symbols:
            df = self.fetch_single(symbol)
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                prev = df.iloc[-2] if len(df) > 1 else latest
                
                results.append({
                    'name': symbol,
                    'symbol': symbol,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'data': df,
                    'current_price': float(latest['Close']),
                    'change': float(latest['Close'] - prev['Close']),
                    'change_pct': float(((latest['Close'] - prev['Close']) / prev['Close']) * 100),
                    'high': float(latest['High']),
                    'low': float(latest['Low']),
                    'volume': int(latest['Volume']),
                    'success': True
                })
                print(f"  {symbol}: {results[-1]['current_price']:.2f} ({results[-1]['change_pct']:+.2f}%)")
        
        return results
    
    def fetch_etfs(self, symbols: List[str] = None) -> List[Dict]:
        """Fetch ETF data for multiple symbols"""
        if symbols is None:
            symbols = ASSETS['etfs'].get('symbols', ['GLD', 'SLV', 'SPY'])
        
        print(f"{Colors.yellow(f'Fetching {len(symbols)} ETF data...')}")
        
        results = []
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                df = self.fetch_single(symbol)
                
                if df is not None and not df.empty:
                    latest = df.iloc[-1]
                    prev = df.iloc[-2] if len(df) > 1 else latest
                    
                    def calc_return(period):
                        try:
                            hist = ticker.history(period=period)
                            if len(hist) > 1:
                                start = hist['Close'].iloc[0]
                                end = hist['Close'].iloc[-1]
                                return float(((end - start) / start) * 100)
                        except:
                            return None
                        return None
                    
                    etf_data = {
                        'symbol': symbol,
                        'name': info.get('shortName', symbol),
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'data': df,
                        'current_price': float(latest['Close']),
                        'change': float(latest['Close'] - prev['Close']),
                        'change_pct': float(((latest['Close'] - prev['Close']) / prev['Close']) * 100),
                        'expense_ratio': info.get('expenseRatio'),
                        'aum': info.get('totalAssets'),
                        '1mo_return': calc_return('1mo'),
                        '3mo_return': calc_return('3mo'),
                        '6mo_return': calc_return('6mo'),
                        '1y_return': calc_return('1y'),
                        'success': True
                    }
                    
                    results.append(etf_data)
                    print(f"  {symbol}: ${etf_data['current_price']:.2f} ({etf_data['change_pct']:+.2f}%)")
                    
            except Exception as e:
                print(f"{Colors.red(f'  Error fetching {symbol}: {e}')}")
        
        return results
    
    def fetch_all(self) -> Dict:
        """Fetch all asset types"""
        print(f"\n{'='*50}")
        print(f"DATA FETCHER - Fetching All Market Data")
        print(f"{'='*50}\n")
        
        return {
            'gold': self.fetch_gold(),
            'silver': self.fetch_silver(),
            'stocks': self.fetch_stocks(),
            'etfs': self.fetch_etfs(),
            'timestamp': datetime.now().isoformat()
        }


def fetch_market_data(symbol: str, period: str = DEFAULT_PERIOD) -> Optional[pd.DataFrame]:
    """Quick function to fetch data for any symbol"""
    fetcher = DataFetcher(period=period)
    return fetcher.fetch_single(symbol)


if __name__ == '__main__':
    fetcher = DataFetcher(period='1mo')
    all_data = fetcher.fetch_all()
    print(f"\n{Colors.green('Data fetching complete!')}")

