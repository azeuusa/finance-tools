"""
Sentiment Analyzer Module
Reads news sentiment data from Node.js (data.json) and provides sentiment analysis
"""

import json
import os
from typing import Dict, Optional
from datetime import datetime, timedelta

from config import NEWS_DATA_FILE, Colors


class SentimentAnalyzer:
    """Analyze sentiment from news data"""
    
    def __init__(self, data_file: str = None):
        self.data_file = data_file or NEWS_DATA_FILE
        self.cache = None
        self.cache_time = None
    
    def load_news_data(self) -> Optional[Dict]:
        """Load news data from JSON file"""
        try:
            if not os.path.exists(self.data_file):
                print(f"{Colors.yellow(f'Warning: {self.data_file} not found. Run Node.js scraper first.')}")
                return None
            
            # Check cache (max 5 minutes old)
            if self.cache and self.cache_time:
                age = datetime.now() - self.cache_time
                if age < timedelta(minutes=5):
                    return self.cache
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.cache = data
                self.cache_time = datetime.now()
                return data
            
        except json.JSONDecodeError as e:
            print(f"{Colors.red(f'Error parsing JSON: {e}')}")
            return None
        except Exception as e:
            print(f"{Colors.red(f'Error loading news data: {e}')}")
            return None
    
    def get_asset_sentiment(self, asset_key: str = 'gold') -> Dict:
        """Get sentiment for a specific asset"""
        data = self.load_news_data()
        
        if not data or 'assets' not in data:
            return {
                'asset': asset_key,
                'sentiment': 'unknown',
                'score': 0,
                'prediction': 'No news data available',
                'success': False
            }
        
        assets = data.get('assets', {})
        asset_data = assets.get(asset_key, {})
        
        if not asset_data:
            return {
                'asset': asset_key,
                'sentiment': 'unknown',
                'score': 0,
                'prediction': f'No data for {asset_key}',
                'success': False
            }
        
        return {
            'asset': asset_key,
            'name': asset_data.get('name', asset_key),
            'symbol': asset_data.get('symbol', ''),
            'sentiment': asset_data.get('sentiment', 'neutral'),
            'score': asset_data.get('sentimentScore', 0),
            'positive_count': asset_data.get('positiveCount', 0),
            'negative_count': asset_data.get('negativeCount', 0),
            'total_news': asset_data.get('totalNews', 0),
            'prediction': asset_data.get('prediction', ''),
            'timestamp': asset_data.get('timestamp', ''),
            'success': True
        }
    
    def get_all_sentiments(self) -> Dict:
        """Get sentiment for all tracked assets"""
        data = self.load_news_data()
        
        if not data:
            return {
                'gold': self.get_asset_sentiment('gold'),
                'silver': self.get_asset_sentiment('silver'),
                'stock': self.get_asset_sentiment('stock'),
                'timestamp': datetime.now().isoformat()
            }
        
        return {
            'gold': self.get_asset_sentiment('gold'),
            'silver': self.get_asset_sentiment('silver'),
            'stock': self.get_asset_sentiment('stock'),
            'timestamp': data.get('metadata', {}).get('generatedAt', datetime.now().isoformat())
        }
    
    def get_combined_sentiment(self) -> Dict:
        """Get combined sentiment score across all assets"""
        sentiments = self.get_all_sentiments()
        
        total_score = 0
        count = 0
        
        for key in ['gold', 'silver', 'stock']:
            if key in sentiments and sentiments[key].get('success'):
                total_score += sentiments[key].get('score', 0)
                count += 1
        
        avg_score = total_score / count if count > 0 else 50
        
        overall = 'neutral'
        if avg_score > 60:
            overall = 'positive'
        elif avg_score < 40:
            overall = 'negative'
        
        return {
            'overall_sentiment': overall,
            'average_score': avg_score,
            'assets_analyzed': count,
            'details': sentiments
        }
    
    def print_sentiment_report(self):
        """Print a formatted sentiment report"""
        print(f"\n{Colors.BLUE}{'='*50}")
        print(f"SENTIMENT ANALYSIS REPORT")
        print(f"{'='*50}{Colors.ENDC}\n")
        
        sentiments = self.get_all_sentiments()
        
        for asset in ['gold', 'silver', 'stock']:
            if asset in sentiments:
                s = sentiments[asset]
                if s.get('success'):
                    emoji = '🟢' if s['sentiment'] == 'positive' else '🔴' if s['sentiment'] == 'negative' else '⚪'
                    print(f"{emoji} {s['name']}: {s['sentiment'].upper()} ({s['score']}%)")
                    print(f"   Prediction: {s['prediction']}")
                    print(f"   News: {s['total_news']} articles analyzed")
                    print()
                else:
                    print(f"⚪ {asset.upper()}: No data available")
                    print()


def analyze_sentiment(asset: str = 'gold') -> Dict:
    """Quick function to get sentiment for an asset"""
    analyzer = SentimentAnalyzer()
    return analyzer.get_asset_sentiment(asset)


if __name__ == '__main__':
    analyzer = SentimentAnalyzer()
    analyzer.print_sentiment_report()
