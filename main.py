
"""
Trading Tool Main Orchestrator
Integrates: Data Fetcher + Mathematician + Decision Maker + Sentiment Analyzer
Node.js provides news sentiment via data.json
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from config import Colors
from data_fetcher import DataFetcher
from mathematician import Mathematician
from sentiment_analyzer import SentimentAnalyzer
from decision_maker import DecisionMaker


class TradingOrchestrator:
    """Main orchestrator for the trading tool"""
    
    def __init__(self):
        self.fetcher = DataFetcher(period='1mo')
        self.math = Mathematician()
        self.sentiment = SentimentAnalyzer()
        self.decision = DecisionMaker()
    
    def run_full_analysis(self):
        """Run complete analysis workflow"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}")
        print("=" * 60)
        print("   TRADING TOOL - Full Analysis")
        print("   Python: Data Fetcher + Mathematician + Decision Maker")
        print("   Node.js: Reporter (News Scraper)")
        print("=" * 60)
        print(f"{Colors.ENDC}\n")
        
        # Step 1: Show sentiment from Node.js
        print(f"{Colors.YELLOW}[1/4] Loading News Sentiment from Node.js...{Colors.ENDC}")
        self.sentiment.print_sentiment_report()
        
        # Step 2: Fetch market data
        print(f"{Colors.YELLOW}[2/4] Fetching Market Data...{Colors.ENDC}")
        market_data = self.fetcher.fetch_all()
        
        # Step 3: Technical Analysis
        print(f"\n{Colors.YELLOW}[3/4] Performing Technical Analysis...{Colors.ENDC}")
        
        # Analyze gold
        if market_data.get('gold', {}).get('success'):
            df = market_data['gold'].get('data')
            if df is not None:
                tech = self.math.analyze_technical(df)
                signals = self.math.get_buy_sell_signals(tech)
                market_data['gold']['technical'] = tech
                market_data['gold']['signals'] = signals
                print(f"  Gold RSI: {tech['indicators']['rsi']['value']:.1f} ({tech['trend']})")
        
        # Analyze silver
        if market_data.get('silver', {}).get('success'):
            df = market_data['silver'].get('data')
            if df is not None:
                tech = self.math.analyze_technical(df)
                signals = self.math.get_buy_sell_signals(tech)
                market_data['silver']['technical'] = tech
                market_data['silver']['signals'] = signals
                print(f"  Silver RSI: {tech['indicators']['rsi']['value']:.1f} ({tech['trend']})")
        
        # Step 4: Make Decisions
        print(f"\n{Colors.YELLOW}[4/4] Generating Trading Decisions...{Colors.ENDC}")
        decisions = self.decision.analyze_all(market_data)
        
        # Print final report
        self.decision.print_trading_report(decisions)
        
        # Print summary
        self._print_summary(decisions, market_data)
        
        return decisions, market_data
    
    def _print_summary(self, decisions, market_data):
        """Print summary of analysis"""
        print(f"{Colors.BOLD}SUMMARY:{Colors.ENDC}")
        print("-" * 40)
        
        # Gold summary
        gold = market_data.get('gold', {})
        if gold.get('success'):
            price = gold.get('current_price', 0)
            change = gold.get('change_pct', 0)
            print(f"Gold: ${price:.2f} ({change:+.2f}%)")
        
        # Silver summary
        silver = market_data.get('silver', {})
        if silver.get('success'):
            price = silver.get('current_price', 0)
            change = silver.get('change_pct', 0)
            print(f"Silver: ${price:.2f} ({change:+.2f}%)")
        
        # Sentiment summary
        combined = self.sentiment.get_combined_sentiment()
        emoji = '🟢' if combined['overall_sentiment'] == 'positive' else '🔴' if combined['overall_sentiment'] == 'negative' else '⚪'
        print(f"\nOverall Sentiment: {emoji} {combined['overall_sentiment'].upper()} ({combined['average_score']:.0f}%)")
        
        print(f"\n{Colors.BOLD}Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
        print("=" * 60)
    
    def quick_gold_analysis(self):
        """Quick analysis for gold only"""
        print(f"\n{Colors.BLUE}Quick Gold Analysis{Colors.ENDC}\n")
        
        # Get sentiment
        sent = self.sentiment.get_asset_sentiment('gold')
        print(f"Sentiment: {sent.get('sentiment', 'unknown').upper()} ({sent.get('score', 0)}%)")
        
        # Get data
        gold = self.fetcher.fetch_gold()
        
        if gold.get('success'):
            df = gold.get('data')
            if df is not None:
                tech = self.math.analyze_technical(df)
                signals = self.math.get_buy_sell_signals(tech)
                
                print(f"\nTechnical Analysis:")
                print(f"  RSI: {tech['indicators']['rsi']['value']:.1f}")
                print(f"  Trend: {tech['trend']}")
                print(f"  Signal: {signals['signal']} ({signals['confidence']}%)")
                
                # Decision
                decision = self.decision.analyze_asset(gold)
                print(f"\n{Colors.BOLD}FINAL DECISION: {decision['decision']['signal']}{Colors.ENDC}")
                print(f"Confidence: {decision['decision']['confidence']}%")
            
        return gold
    
    def run_continuous(self, interval_seconds: int = 60):
        """Run analysis continuously"""
        import time
        print(f"\n{Colors.YELLOW}Running continuous analysis every {interval_seconds} seconds{Colors.ENDC}")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.run_full_analysis()
                print(f"\n{Colors.YELLOW}Waiting {interval_seconds} seconds...{Colors.ENDC}\n")
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print(f"\n{Colors.RED}Stopped by user{Colors.ENDC}")


def main():
    """Main entry point"""
    orchestrator = TradingOrchestrator()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == '--gold' or arg == '-g':
            orchestrator.quick_gold_analysis()
        elif arg == '--continuous' or arg == '-c':
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            orchestrator.run_continuous(interval)
        elif arg == '--help' or arg == '-h':
            print("""
Trading Tool - Usage:
  python main.py              Run full analysis
  python main.py --gold      Quick gold analysis
  python main.py --continuous Run continuously (60s default)
  python main.py --help      Show this help
            """)
        else:
            print(f"Unknown option: {arg}")
            print("Use --help for usage information")
    else:
        orchestrator.run_full_analysis()


if __name__ == '__main__':
    main()
