#!/usr/bin/env python3
"""
Gold, Silver & ETF Scraper & Recommender
Script untuk scraping data emas, perak, dan ETF serta memberikan rekomendasi ETF yang bagus
"""

import yfinance as yf
from datetime import datetime
from typing import Dict, List, Tuple
import warnings

warnings.filterwarnings('ignore')

# ANSI colors for terminal output
class Colors:
    GOLD = '\033[93m'
    SILVER = '\033[96m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{title:^60}{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_price_card(name: str, price: float, change: float, change_pct: float, color: str):
    """Print price information in card format"""
    change_color = Colors.GREEN if change >= 0 else Colors.RED
    print(f"{color}{Colors.BOLD}{name}{Colors.END}")
    print(f"  Harga    : ${price:,.2f}")
    print(f"  Perubahan: {change_color}{change:+.2f} ({change_pct:+.2f}%){Colors.END}")
    print()

def scrape_gold_prices() -> Dict:
    """Scrape gold prices using yfinance"""
    print(f"{Colors.GOLD}📊 Mengambil data harga emas...{Colors.END}")
    
    try:
        # Gold Spot Price (XAU/USD)
        gold = yf.Ticker("XAUUSD=X")
        gold_info = gold.history(period="1d")
        
        if len(gold_info) > 0:
            latest = gold_info.iloc[-1]
            prev_close = gold_info.iloc[0]['Close'] if len(gold_info) > 1 else latest['Close']
            change = latest['Close'] - prev_close
            change_pct = (change / prev_close) * 100
            
            return {
                'name': 'Emas (XAU/USD)',
                'price': float(latest['Close']),
                'change': float(change),
                'change_pct': float(change_pct),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'volume': int(latest['Volume']),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    except Exception as e:
        print(f"{Colors.RED}Error mengambil data emas: {e}{Colors.END}")
    
    return None

def scrape_silver_prices() -> Dict:
    """Scrape silver prices using yfinance"""
    print(f"{Colors.SILVER}📊 Mengambil data harga perak...{Colors.END}")
    
    try:
        # Silver Spot Price (XAG/USD)
        silver = yf.Ticker("XAGUSD=X")
        silver_info = silver.history(period="1d")
        
        if len(silver_info) > 0:
            latest = silver_info.iloc[-1]
            prev_close = silver_info.iloc[0]['Close'] if len(silver_info) > 1 else latest['Close']
            change = latest['Close'] - prev_close
            change_pct = (change / prev_close) * 100

            return {
                'name': 'Perak (XAG/USD)',
                'price': float(latest['Close']),
                'change': float(change),
                'change_pct': float(change_pct),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'volume': int(latest['Volume']),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    except Exception as e:
        print(f"{Colors.RED}Error mengambil data perak: {e}{Colors.END}")
    
    return None


def scrape_etfs(symbols: List[str]) -> List[Dict]:
    """Scrape ETF information for a list of ticker symbols.
    Returns a list of dictionaries containing price and basic metrics.
    """
    results = []
    print(f"{Colors.BLUE}📊 Mengambil data ETF...{Colors.END}")

    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            info = ticker.info
            hist = ticker.history(period="1y")

            if hist.empty:
                continue

            latest = hist.iloc[-1]
            prev_close = hist.iloc[-2]['Close'] if len(hist) > 1 else latest['Close']
            change = latest['Close'] - prev_close
            change_pct = (change / prev_close) * 100 if prev_close != 0 else 0

            # calculate returns
            def pct_return(period: str):
                h = ticker.history(period=period)
                if len(h) < 2:
                    return None
                start = h['Close'].iloc[0]
                end = h['Close'].iloc[-1]
                return (end - start) / start * 100 if start != 0 else None

            results.append({
                'symbol': sym,
                'name': info.get('shortName', sym),
                'price': float(latest['Close']),
                'change': float(change),
                'change_pct': float(change_pct),
                'expense_ratio': info.get('expenseRatio'),
                'aum': info.get('totalAssets'),
                '1mo_return': pct_return('1mo'),
                '3mo_return': pct_return('3mo'),
                '6mo_return': pct_return('6mo'),
                '1y_return': pct_return('1y'),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        except Exception as e:
            print(f"{Colors.RED}Gagal mengambil data untuk {sym}: {e}{Colors.END}")
    return results


def recommend_etfs(etf_list: List[Dict]) -> List[Dict]:
    """Simple recommendation: pick ETFs with positive 1mo return and reasonable volume/AUM."""
    recommendations = []
    for etf in etf_list:
        score = 0
        # positive returns increase score
        for key in ('1mo_return','3mo_return','6mo_return','1y_return'):
            val = etf.get(key)
            if val is not None and val > 0:
                score += 1
        # lower expense ratio adds value
        er = etf.get('expense_ratio')
        if er is not None and er < 0.01:
            score += 1
        # larger AUM adds value
        aum = etf.get('aum')
        if aum is not None and aum > 1e9:
            score += 1
        if score >= 3:
            recommendations.append({**etf, 'score': score})
    # sort by score desc then 1mo_return
    recommendations.sort(key=lambda x: (x['score'], x.get('1mo_return',0)), reverse=True)
    return recommendations


def print_etf_card(etf: Dict):
    """Print a summary card for an ETF"""
    print(f"{Colors.BOLD}{etf['symbol']} - {etf.get('name','')}{Colors.END}")
    print(f"  Harga : ${etf['price']:,.2f} ({etf['change_pct']:+.2f}%)")
    for k in ('1mo_return','3mo_return','6mo_return','1y_return'):
        v = etf.get(k)
        if v is not None:
            print(f"  {k.replace('_',' ')} : {v:+.2f}%")
    if etf.get('expense_ratio') is not None:
        print(f"  Expense Ratio : {etf['expense_ratio']:.4f}")
    if etf.get('aum') is not None:
        print(f"  AUM : {etf['aum']:,}")
    if 'score' in etf:
        print(f"  Score : {etf['score']}")
    print()


def main():
    print_header("Gold, Silver & ETF Analyzer")
    gold = scrape_gold_prices()
    silver = scrape_silver_prices()

    if gold:
        print_price_card(gold['name'], gold['price'], gold['change'], gold['change_pct'], Colors.GOLD)
    if silver:
        print_price_card(silver['name'], silver['price'], silver['change'], silver['change_pct'], Colors.SILVER)

    # default ETF list
    etfs = ["GLD","SLV","SPY","IVV","VOO","QQQ","IWM","EEM","VNQ","GDX","GDXJ","USO","UNG"]
    etf_data = scrape_etfs(etfs)

    print_header("ETF Summary")
    for etf in etf_data:
        print_etf_card(etf)

    print_header("Recommended ETFs")
    recs = recommend_etfs(etf_data)
    if recs:
        for r in recs:
            print_etf_card(r)
    else:
        print("Tidak ada ETF yang memenuhi kriteria rekomendasi saat ini.")

if __name__ == '__main__':
    main()
