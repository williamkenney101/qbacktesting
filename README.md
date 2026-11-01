# Trading backtesting

A program that tests four trading strategies on the SPY. Each is compared against buy and hold.
Try running it yourself! Change start and end date, then the market in the settings section at the top. (Don't use for trading advice...)

## Requirements
yfinance, pandas, matplotlib, numpy
or run this in terminal:
```
pip install yfinance pandas matplotlib numpy
```

to launch, run this:
```
python qbot.py / python3 qbot.py 
```

## How it works

1. Downloads daily SPY prices from Yahoo Finance using yfinance
2. Each strategy decides each day how much of the portfolio to hold in SPY (0% to 100%), with rest as cash
3. Starts with a given value (base is 10,000), goes through history and checks value of portfolio
4. Reports total return, annual return, Sharpe ratio, and maximum drop, all compared to buy and hold

## Other information

- Avoids lookahead bias. A signal computed from today's closing price is only traded the next day, since in real life you can't trade at a price you haven't seen!
- Miscellanous costs. Every buy or sell is charged 0.1%, so strategies that trade often pay for it.

## The strategies

| Strategy | Rule | Idea |
|---|---|---|
| `crossover` | Hold SPY when the 50-day moving average is above the 200-day | Goes for long-term uptrends |
| `above_200` | Hold SPY when the price is above the 200-day moving average | Same idea as crossover, reacts faster |
| `vol_target` | Hold less SPY when recent volatility is high, more when low | Crashes come with volatility spikes |
| `rsi_dip` | Buy when RSI drops below 30, sell above 70 | Hoping dips bounce back |

## Results: 2010–2026

| Strategy | Annual return | Sharpe ratio | Max drawdown |
|---|---|---|---|
| Buy & hold | 14.3% | 0.88 | -33.7% |
| **vol_target** | 10.6% | **0.94** | **-15.5%** |
| above_200 | 10.1% | 0.88 | -21.6% |
| crossover | 9.6% | 0.71 | -33.7% |
| rsi_dip | 8.3% | 0.68 | -28.4% |

No strategy beat the buy and hold. 2010–2026 was a pretty strong market, so sitting out of it for any amount of time risks profits.

I found that volatility had the best overall. Its worst loss was less than half of the buy and hold, and its Sharpe ratio was a little bit higher. It works because the market crashes come with sudden jumps in volatility.

The moving-average crossover did the worst of the trend strategies, as moving averages lag. In the 2020 COVID crash, the 50-day average did not cross below the 200-day until most of the drop had already happened, so it takes the loss and misses the comeback. 

RSI dip-buying finished last. It sells once the market looks "overbought," which in this market means selling during strong uptrends.

## Out-of-sample test: 1999–2009

Theres also the problem of overfitting. To check, I ran the best strategy (vol target) on a decade it was never tested on, which includes some pivotal moments like the dot-com crash and the 2008 financial crisis.

| Strategy | Annual return | Sharpe ratio | Max drawdown |
|---|---|---|---|
| Buy & hold | 0.6% | 0.14 | -55.2% |
| vol_target | 0.4% | 0.09 | -40.1% |

- The drawdown advantage did hold up, with the worst loss being 27% smaller than buy and hold.
- The Sharpe advantage did not though, vol targeting had a slightly lower Sharpe than buy and hold here, so the small edge in 2010–2026 was probably luck.
- It protected less against the dot-com crash because that decline was slow and grinding over nearly three years. The market did not have any intense volatility, so the strategy stayed partly invested.

## Conclusion

Volatility targeting reduced the worst loss in both periods tested (by 54% in 2010–2026 and by 27% in 1999–2009), but its risk adjusted return advantage did not hold up out of sample. Protects best against sudden crashes rather than slow declines (as stated above).

## Limitations

- Tested on one only one asset (SPY) and only two time periods
- The Sharpe ratio here leaves out the risk-free rate, which makes my calculated Sharpe slightly higher than standard version
- Strategy settings (50/200 days, 12% volatility target, RSI 30/70) were not optimized. Optimization is a whole other issue, as I would want to ensure that the new inputs don't risk overfitting.
- Cash earns 0% in the backtest. Theres interest to consider, which would help the strategies that spend a lot of time out of the market.

## Next steps

- Hold bonds instead of cash when out of the market
- Test on other assets (international stocks, bonds, gold)
- Combine signals, for example trend plus volatility. These strategies only really focused on one parameter
- Run the strategy live with (simulated!) money through a broker API
