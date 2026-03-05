"""
Mathematician Module
Calculates technical indicators: RSI, MACD, SMA, EMA, Bollinger Bands, etc.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from config import TRADING_PARAMS, Colors


class Mathematician:
    """Technical analysis and calculations"""
    
    def __init__(self):
        self.params = TRADING_PARAMS
    
    def calculate_rsi(self, data: pd.Series, period: int = None) -> pd.Series:
        """Calculate Relative Strength Index (RSI)"""
        p = period if period else self.params.get('rsi_period', 14)
        
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=p).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=p).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_sma(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return data.rolling(window=period).mean()
    
    def calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()
    
    def calculate_macd(self, data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD"""
        ema_fast = self.calculate_ema(data, fast)
        ema_slow = self.calculate_ema(data, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = self.calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def calculate_bollinger_bands(self, data: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = self.calculate_sma(data, period)
        std = data.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return upper_band, sma, lower_band
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator"""
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        
        k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d = k.rolling(window=3).mean()
        
        return k, d
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range (ATR)"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    def calculate_price_change(self, data: pd.Series) -> Dict:
        """Calculate various price changes"""
        if len(data) < 2:
            return {}
        
        current = data.iloc[-1]
        prev = data.iloc[-2]
        
        return {
            'change': float(current - prev),
            'change_pct': float(((current - prev) / prev) * 100),
            'current_price': float(current),
            'high_1d': float(data.tail(1).max()),
            'low_1d': float(data.tail(1).min())
        }
    
    def analyze_technical(self, df: pd.DataFrame) -> Dict:
        """Perform complete technical analysis on data"""
        if df is None or df.empty:
            return {'error': 'No data available'}
        
        close = df['Close']
        high = df['High']
        low = df['Low']
        
        # Calculate indicators
        rsi = self.calculate_rsi(close)
        sma_20 = self.calculate_sma(close, 20)
        sma_50 = self.calculate_sma(close, 50)
        ema_12 = self.calculate_ema(close, 12)
        ema_26 = self.calculate_ema(close, 26)
        macd_line, signal_line, histogram = self.calculate_macd(close)
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(close)
        stoch_k, stoch_d = self.calculate_stochastic(high, low, close)
        atr = self.calculate_atr(high, low, close)
        
        # Current values
        current_rsi = float(rsi.iloc[-1]) if not rsi.empty else 50
        current_macd = float(macd_line.iloc[-1]) if not macd_line.empty else 0
        current_hist = float(histogram.iloc[-1]) if not histogram.empty else 0
        
        # Determine trend
        trend = 'neutral'
        if current_rsi > 70:
            trend = 'overbought'
        elif current_rsi < 30:
            trend = 'oversold'
        elif sma_20.iloc[-1] > sma_50.iloc[-1]:
            trend = 'bullish'
        elif sma_20.iloc[-1] < sma_50.iloc[-1]:
            trend = 'bearish'
        
        # MACD signal
        macd_signal = 'neutral'
        if current_macd > 0 and current_hist > 0:
            macd_signal = 'bullish'
        elif current_macd < 0 and current_hist < 0:
            macd_signal = 'bearish'
        
        return {
            'timestamp': datetime.now().isoformat(),
            'indicators': {
                'rsi': {
                    'value': current_rsi,
                    'status': 'oversold' if current_rsi < 30 else 'overbought' if current_rsi > 70 else 'neutral'
                },
                'macd': {
                    'line': current_macd,
                    'histogram': current_hist,
                    'signal': macd_signal
                },
                'sma': {
                    'sma_20': float(sma_20.iloc[-1]) if not sma_20.empty else None,
                    'sma_50': float(sma_50.iloc[-1]) if not sma_50.empty else None
                },
                'bollinger_bands': {
                    'upper': float(bb_upper.iloc[-1]) if not bb_upper.empty else None,
                    'middle': float(bb_middle.iloc[-1]) if not bb_middle.empty else None,
                    'lower': float(bb_lower.iloc[-1]) if not bb_lower.empty else None
                },
                'atr': float(atr.iloc[-1]) if not atr.empty else None
            },
            'trend': trend,
            'price_change': self.calculate_price_change(close)
        }
    
    def get_buy_sell_signals(self, analysis: Dict) -> Dict:
        """Generate buy/sell signals based on technical analysis"""
        if 'error' in analysis:
            return {'signal': 'neutral', 'confidence': 0, 'reason': analysis['error']}
        
        signals = []
        confidence = 0
        
        rsi = analysis['indicators']['rsi']['value']
        macd = analysis['indicators']['macd']
        trend = analysis['trend']
        
        # RSI signals
        if rsi < 30:
            signals.append('BUY (RSI Oversold)')
            confidence += 25
        elif rsi > 70:
            signals.append('SELL (RSI Overbought)')
            confidence += 25
        
        # MACD signals
        if macd['signal'] == 'bullish':
            signals.append('BUY (MACD Bullish)')
            confidence += 20
        elif macd['signal'] == 'bearish':
            signals.append('SELL (MACD Bearish)')
            confidence += 20
        
        # Trend signals
        if trend == 'bullish':
            signals.append('BUY (Trend Bullish)')
            confidence += 15
        elif trend == 'bearish':
            signals.append('SELL (Trend Bearish)')
            confidence += 15
        
        # Determine final signal
        buy_count = sum(1 for s in signals if 'BUY' in s)
        sell_count = sum(1 for s in signals if 'SELL' in s)
        
        if buy_count > sell_count and confidence >= 40:
            final_signal = 'BUY'
        elif sell_count > buy_count and confidence >= 40:
            final_signal = 'SELL'
        else:
            final_signal = 'HOLD'
        
        return {
            'signal': final_signal,
            'confidence': min(100, confidence),
            'reasons': signals,
            'rsi': rsi,
            'trend': trend
        }


if __name__ == '__main__':
    print("Mathematician module loaded successfully")
