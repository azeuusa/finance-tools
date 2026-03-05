"""
Decision Maker Module
Combines technical analysis and sentiment to generate trading decisions
"""

from typing import Dict, List, Optional
from datetime import datetime

from config import TRADING_PARAMS, Colors
from mathematician import Mathematician
from sentiment_analyzer import SentimentAnalyzer


class DecisionMaker:
    """Generate trading decisions based on technical + sentiment analysis"""
    
    def __init__(self):
        self.math = Mathematician()
        self.sentiment = SentimentAnalyzer()
        self.params = TRADING_PARAMS
    
    def analyze_asset(self, asset_data: Dict) -> Dict:
        """Make decision for a single asset"""
        df = asset_data.get('data')
        asset_name = asset_data.get('name', 'Unknown')
        asset_symbol = asset_data.get('symbol', '')
        
        if df is None or df.empty:
            return {
                'asset': asset_name,
                'symbol': asset_symbol,
                'signal': 'HOLD',
                'confidence': 0,
                'reason': 'No data available'
            }
        
        # Technical analysis
        tech_analysis = self.math.analyze_technical(df)
        tech_signals = self.math.get_buy_sell_signals(tech_analysis)
        
        # Sentiment analysis
        sentiment_key = asset_name.lower()
        if 'gold' in sentiment_key or 'gc=f' in asset_symbol.lower():
            sentiment_key = 'gold'
        elif 'silver' in sentiment_key or 'si=f' in asset_symbol.lower():
            sentiment_key = 'silver'
        else:
            sentiment_key = 'stock'
        
        sentiment_data = self.sentiment.get_asset_sentiment(sentiment_key)
        
        # Combine signals
        final_decision = self._combine_signals(tech_signals, sentiment_data)
        
        return {
            'asset': asset_name,
            'symbol': asset_symbol,
            'timestamp': datetime.now().isoformat(),
            'technical': {
                'signal': tech_signals['signal'],
                'confidence': tech_signals['confidence'],
                'rsi': tech_signals.get('rsi', 50),
                'trend': tech_signals.get('trend', 'neutral'),
                'reasons': tech_signals.get('reasons', [])
            },
            'sentiment': {
                'sentiment': sentiment_data.get('sentiment', 'neutral'),
                'score': sentiment_data.get('score', 50),
                'prediction': sentiment_data.get('prediction', '')
            },
            'decision': final_decision
        }
    
    def _combine_signals(self, tech: Dict, sentiment: Dict) -> Dict:
        """Combine technical and sentiment signals"""
        tech_signal = tech.get('signal', 'HOLD')
        tech_conf = tech.get('confidence', 0)
        
        sent_score = sentiment.get('score', 50)
        sent_type = sentiment.get('sentiment', 'neutral')
        
        # Calculate weights
        tech_weight = 0.6
        sent_weight = 0.4
        
        # Score based on signals
        buy_score = 0
        sell_score = 0
        
        # Technical contribution
        if tech_signal == 'BUY':
            buy_score += tech_conf * tech_weight
        elif tech_signal == 'SELL':
            sell_score += tech_conf * tech_weight
        
        # Sentiment contribution
        if sent_type == 'positive':
            buy_score += sent_weight * sent_score
        elif sent_type == 'negative':
            sell_score += sent_weight * sent_score
        
        # Determine final signal
        threshold = self.params.get('min_confidence', 40)
        
        if buy_score > sell_score + threshold:
            signal = 'BUY'
            confidence = min(100, int(buy_score))
        elif sell_score > buy_score + threshold:
            signal = 'SELL'
            confidence = min(100, int(sell_score))
        else:
            signal = 'HOLD'
            confidence = max(0, 100 - abs(buy_score - sell_score))
        
        # Build reasons
        reasons = tech.get('reasons', [])
        if sent_type == 'positive':
            reasons.append(f"SENTIMENT: News is positive ({sent_score}%)")
        elif sent_type == 'negative':
            reasons.append(f"SENTIMENT: News is negative ({sent_score}%)")
        
        return {
            'signal': signal,
            'confidence': confidence,
            'buy_score': buy_score,
            'sell_score': sell_score,
            'reasons': reasons
        }
    
    def analyze_all(self, market_data: Dict) -> List[Dict]:
        """Analyze all assets from market data"""
        results = []
        
        # Analyze gold
        if 'gold' in market_data and market_data['gold'].get('success'):
            result = self.analyze_asset(market_data['gold'])
            results.append(result)
        
        # Analyze silver
        if 'silver' in market_data and market_data['silver'].get('success'):
            result = self.analyze_asset(market_data['silver'])
            results.append(result)
        
        # Analyze stocks
        if 'stocks' in market_data:
            for stock in market_data['stocks']:
                if stock.get('success'):
                    result = self.analyze_asset(stock)
                    results.append(result)
        
        # Analyze ETFs
        if 'etfs' in market_data:
            for etf in market_data['etfs']:
                if etf.get('success'):
                    result = self.analyze_asset(etf)
                    results.append(result)
        
        return results
    
    def get_top_picks(self, decisions: List[Dict], signal: str = 'BUY', limit: int = 3) -> List[Dict]:
        """Get top picks for a specific signal"""
        filtered = [d for d in decisions if d.get('decision', {}).get('signal') == signal]
        sorted_by_conf = sorted(filtered, key=lambda x: x.get('decision', {}).get('confidence', 0), reverse=True)
        return sorted_by_conf[:limit]
    
    def print_trading_report(self, decisions: List[Dict]):
        """Print formatted trading report"""
        print(f"\n{Colors.BOLD}{'='*60}")
        print(f"TRADING DECISION REPORT")
        print(f"{'='*60}{Colors.ENDC}\n")
        
        # Separate by signal
        buys = [d for d in decisions if d.get('decision', {}).get('signal') == 'BUY']
        sells = [d for d in decisions if d.get('decision', {}).get('signal') == 'SELL']
        holds = [d for d in decisions if d.get('decision', {}).get('signal') == 'HOLD']
        
        # Print BUY signals
        if buys:
            print(f"{Colors.green('🟢 BUY SIGNALS:')}")
            for d in sorted(buys, key=lambda x: x.get('decision', {}).get('confidence', 0), reverse=True):
                conf = d.get('decision', {}).get('confidence', 0)
                print(f"   {d['symbol']} ({d['asset']}) - Confidence: {conf}%")
                print(f"   Price: ${d.get('technical', {}).get('price_change', {}).get('current_price', 'N/A')}")
                for reason in d.get('decision', {}).get('reasons', [])[:2]:
                    print(f"   - {reason}")
                print()
        
        # Print SELL signals
        if sells:
            print(f"{Colors.red('🔴 SELL SIGNALS:')}")
            for d in sorted(sells, key=lambda x: x.get('decision', {}).get('confidence', 0), reverse=True):
                conf = d.get('decision', {}).get('confidence', 0)
                print(f"   {d['symbol']} ({d['asset']}) - Confidence: {conf}%")
                for reason in d.get('decision', {}).get('reasons', [])[:2]:
                    print(f"   - {reason}")
                print()
        
        # Print HOLD signals
        if holds:
            print(f"{Colors.yellow('⚪ HOLD SIGNALS:')}")
            for d in holds[:3]:
                conf = d.get('decision', {}).get('confidence', 0)
                print(f"   {d['symbol']} ({d['asset']}) - Confidence: {conf}%")
        
        print(f"\n{Colors.BOLD}{'='*60}\n")


def make_decision(asset_data: Dict) -> Dict:
    """Quick function to make a decision for an asset"""
    dm = DecisionMaker()
    return dm.analyze_asset(asset_data)


if __name__ == '__main__':
    print("Decision Maker module loaded successfully")

