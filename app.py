"""
股票行情看板 - Flask Backend
获取A股/港股/美股实时行情数据
"""

import os
import yfinance as yf
from flask import Flask, render_template, jsonify, request
from datetime import datetime

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/quote/<symbol>')
def quote(symbol):
    """获取单个股票行情"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return jsonify({
            'symbol': symbol,
            'name': info.get('shortName') or info.get('longName') or symbol,
            'price': info.get('regularMarketPrice') or info.get('currentPrice') or 0,
            'change': info.get('regularMarketChange') or 0,
            'changePercent': info.get('regularMarketChangePercent') or 0,
            'high': info.get('dayHigh') or 0,
            'low': info.get('dayLow') or 0,
            'volume': info.get('regularMarketVolume') or 0,
            'marketCap': info.get('marketCap') or 0,
            'currency': info.get('currency') or 'USD',
            'exchange': info.get('exchange') or 'UNKNOWN',
        })
    except Exception as e:
        return jsonify({'symbol': symbol, 'error': str(e)}), 400

@app.route('/api/history/<symbol>')
def history(symbol):
    """获取股票历史K线数据"""
    period = request.args.get('period', '1mo')
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        if hist.empty:
            return jsonify({'symbol': symbol, 'error': 'No data'}), 404
        
        data = {
            'symbol': symbol,
            'dates': [d.isoformat() for d in hist.index],
            'open': hist['Open'].tolist(),
            'high': hist['High'].tolist(),
            'low': hist['Low'].tolist(),
            'close': hist['Close'].tolist(),
            'volume': hist['Volume'].tolist(),
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({'symbol': symbol, 'error': str(e)}), 400

@app.route('/api/search')
def search():
    """搜索股票（简单实现）"""
    query = request.args.get('q', '').strip().upper()
    if not query:
        return jsonify([])
    
    # 常见股票代码映射
    known = {
        'AAPL': ('Apple Inc.', 'NASDAQ'),
        'GOOGL': ('Alphabet Inc.', 'NASDAQ'),
        'MSFT': ('Microsoft Corp.', 'NASDAQ'),
        'AMZN': ('Amazon.com Inc.', 'NASDAQ'),
        'TSLA': ('Tesla Inc.', 'NASDAQ'),
        'META': ('Meta Platforms', 'NASDAQ'),
        'NVDA': ('NVIDIA Corp.', 'NASDAQ'),
        '0700.HK': ('腾讯控股', '港交所'),
        '9988.HK': ('阿里巴巴', '港交所'),
        '3690.HK': ('美团', '港交所'),
        '600519.SS': ('贵州茅台', '上交所'),
        '600036.SS': ('招商银行', '上交所'),
        '000858.SZ': ('五粮液', '深交所'),
        '300750.SZ': ('宁德时代', '深交所'),
    }
    
    results = [{'symbol': k, 'name': v[0], 'exchange': v[1]} 
               for k, v in known.items() if query in k or query in v[0]]
    return jsonify(results)

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=False)
