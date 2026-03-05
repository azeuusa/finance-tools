/**
 * JAWASC - JavaScript Automated Web Scraper & News Analyzer
 * Node.js Reporter Module
 * Scrapes Google News and saves sentiment data to data.json
 * Runs automatically on schedule
 */

const axios = require('axios');
const cheerio = require('cheerio');
const cron = require('node-cron');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
    outputFile: path.join(__dirname, 'data.json'),
    refreshInterval: '*/10 * * * *', // Every 10 minutes
    maxNewsItems: 20,
    lang: 'id',
    region: 'ID'
};

// Asset keywords for scraping
const ASSETS = {
    gold: {
        name: 'Gold',
        symbol: 'GC=F',
        keywords: ['harga emas', 'gold price', 'GC=F', 'XAU USD', 'emas hari ini'],
        posWords: ['naik', 'melejit', 'untung', 'bullish', 'menguat', 'rekor', 'mahal', 'positif', 'kuat'],
        negWords: ['turun', 'anjlok', 'rugi', 'bearish', 'melemah', 'murah', 'merosot', 'negatif', 'weak']
    },
    silver: {
        name: 'Silver',
        symbol: 'SI=F',
        keywords: ['harga perak', 'silver price', 'SI=F', 'XAG USD', 'perak hari ini'],
        posWords: ['naik', 'melejit', 'untung', 'bullish', 'menguat', 'rekor', 'mahal', 'positif', 'kuat'],
        negWords: ['turun', 'anjlok', 'rugi', 'bearish', 'melemah', 'murah', 'merosot', 'negatif', 'weak']
    },
    stock: {
        name: 'Stock Market',
        symbol: 'INDEX',
        keywords: ['stock market', 'IDX', 'NYSE', 'saham', 'IHSG', 'Bursa efek', 'market review'],
        posWords: ['naik', 'bullish', 'menguat', 'rekor', 'positif', 'kuat', 'gain', 'profit', 'semangat'],
        negWords: ['turun', 'bearish', 'melemah', 'negatif', 'weak', 'loss', 'rugi', 'crash', 'ambles']
    }
};

// Analyze sentiment for a given asset
async function analyzeAsset(assetKey) {
    const asset = ASSETS[assetKey];
    const allResults = [];
    
    console.log(`\n🔍 Analyzing ${asset.name} news...`);
    
    for (const keyword of asset.keywords) {
        try {
            const url = `https://news.google.com/rss/search?q=${encodeURIComponent(keyword)}&hl=${CONFIG.lang}&gl=${CONFIG.region}&ceid=${CONFIG.region}:${CONFIG.lang}`;
            const { data } = await axios.get(url, { timeout: 10000 });
            const $ = cheerio.load(data, { xmlMode: true });
            
            let positiveScore = 0;
            let negativeScore = 0;
            const newsItems = [];
            
            $('item').each((i, el) => {
                if (i >= CONFIG.maxNewsItems) return;
                
                const title = $(el).find('title').text().toLowerCase();
                const link = $(el).find('link').text();
                const pubDate = $(el).find('pubDate').text();
                
                // Count positive words
                asset.posWords.forEach(word => {
                    if (title.includes(word)) positiveScore++;
                });
                
                // Count negative words
                asset.negWords.forEach(word => {
                    if (title.includes(word)) negativeScore++;
                });
                
                newsItems.push({
                    title: $(el).find('title').text(),
                    link: link,
                    pubDate: pubDate
                });
            });
            
            allResults.push({
                keyword: keyword,
                positiveScore: positiveScore,
                negativeScore: negativeScore,
                newsCount: newsItems.length,
                newsItems: newsItems.slice(0, 5)
            });
            
            // Small delay to avoid rate limiting
            await new Promise(resolve => setTimeout(resolve, 1000));
            
        } catch (error) {
            console.error(`  ⚠️ Error fetching ${keyword}: ${error.message}`);
        }
    }
    
    // Aggregate results
    const totalPositive = allResults.reduce((sum, r) => sum + r.positiveScore, 0);
    const totalNegative = allResults.reduce((sum, r) => sum + r.negativeScore, 0);
    const totalNews = allResults.reduce((sum, r) => sum + r.newsCount, 0);
    
    // Determine sentiment
    let sentiment = 'neutral';
    let sentimentScore = 0;
    
    if (totalPositive > totalNegative) {
        sentiment = 'positive';
        sentimentScore = Math.min(100, Math.round((totalPositive / (totalPositive + totalNegative || 1)) * 100));
    } else if (totalNegative > totalPositive) {
        sentiment = 'negative';
        sentimentScore = Math.min(100, Math.round((totalNegative / (totalPositive + totalNegative || 1)) * 100));
    }
    
    // Generate prediction
    let prediction = '';
    if (sentiment === 'positive') {
        prediction = `${asset.name} trending positive. Potential for price increase.`;
    } else if (sentiment === 'negative') {
        prediction = `${asset.name} facing negative sentiment. Potential for price decrease.`;
    } else {
        prediction = `${asset.name} sentiment is neutral. Sideways movement expected.`;
    }
    
    return {
        name: asset.name,
        symbol: asset.symbol,
        sentiment: sentiment,
        sentimentScore: sentimentScore,
        positiveCount: totalPositive,
        negativeCount: totalNegative,
        totalNews: totalNews,
        prediction: prediction,
        details: allResults,
        timestamp: new Date().toISOString()
    };
}

// Main function to scrape all assets
async function scrapeAllAssets() {
    console.log('\n' + '='.repeat(50));
    console.log('🤖 JAWASC - Starting News Analysis');
    console.log('='.repeat(50));
    
    const results = {
        metadata: {
            generatedAt: new Date().toISOString(),
            source: 'Google News RSS',
            version: '1.0.0'
        },
        assets: {}
    };
    
    // Analyze each asset
    for (const assetKey of Object.keys(ASSETS)) {
        try {
            results.assets[assetKey] = await analyzeAsset(assetKey);
        } catch (error) {
            console.error(`Error analyzing ${assetKey}: ${error.message}`);
            results.assets[assetKey] = {
                name: ASSETS[assetKey].name,
                symbol: ASSETS[assetKey].symbol,
                sentiment: 'error',
                sentimentScore: 0,
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }
    
    // Save to JSON file
    try {
        fs.writeFileSync(CONFIG.outputFile, JSON.stringify(results, null, 2));
        console.log(`\n✅ Data saved to: ${CONFIG.outputFile}`);
    } catch (error) {
        console.error(`\n❌ Failed to save data: ${error.message}`);
    }
    
    // Print summary
    console.log('\n📊 SENTIMENT SUMMARY:');
    console.log('-'.repeat(30));
    for (const assetKey of Object.keys(results.assets)) {
        const asset = results.assets[assetKey];
        const emoji = asset.sentiment === 'positive' ? '🟢' : asset.sentiment === 'negative' ? '🔴' : '⚪';
        console.log(`${emoji} ${asset.name}: ${asset.sentiment.toUpperCase()} (${asset.sentimentScore}%)`);
    }
    console.log('='.repeat(50));
    
    return results;
}

// Run immediately on start
scrapeAllAssets();

// Schedule periodic runs
console.log(`\n⏰ Scheduler started. Will refresh every 10 minutes.`);
console.log(`   To change interval, modify CONFIG.refreshInterval`);
cron.schedule(CONFIG.refreshInterval, () => {
    console.log('\n⏰ Scheduled run triggered...');
    scrapeAllAssets();
});

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('\n\n👋 Shutting down gracefully...');
    process.exit(0);
});

