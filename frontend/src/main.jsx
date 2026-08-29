import React from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const watchlist = ['NIFTY50', 'BANKNIFTY', 'RELIANCE', 'TCS', 'INFY', 'HDFCBANK'];

function App() {
  return <main className="terminal">
    <header><div><h1>MAHADEV NIFTY TERMINAL</h1><p>FYERS live market intelligence</p></div><span className="status">● PAPER MODE</span></header>
    <section className="grid">
      <div className="panel wide"><h2>Market Scanner</h2><table><thead><tr><th>Symbol</th><th>Price</th><th>RSI</th><th>ATR</th><th>PCR</th><th>Signal</th><th>Confidence</th></tr></thead><tbody>{watchlist.map(s=><tr key={s}><td>{s}</td><td>—</td><td>—</td><td>—</td><td>—</td><td className="muted">WAITING FOR FYERS</td><td>—</td></tr>)}</tbody></table></div>
      <div className="panel"><h2>Risk Engine</h2><div className="metric"><span>Active Signals</span><b>0</b></div><div className="metric"><span>Average R:R</span><b>—</b></div><div className="metric"><span>Live Trading</span><b>OFF</b></div></div>
      <div className="panel wide"><h2>Trade Journal</h2><p className="muted">No signals recorded. Live indicators will appear after FYERS credentials and WebSocket data are configured.</p></div>
      <div className="panel"><h2>System</h2><p>Backend: pending deployment</p><p>Data feed: FYERS</p><p>Execution: disabled</p></div>
    </section>
  </main>
}

createRoot(document.getElementById('root')).render(<App />);
