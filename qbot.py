import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

# settings ---
TICKER = "SPY"          # s&p 500
START = "1999-01-01"    
END = "2010-01-01"      # write None for today
SHORT_WINDOW = 50       # fast avg (days)
LONG_WINDOW = 200       # slow avg (days)
COST_PER_TRADE = 0.001  # slippage/comissions factor (kind of an overestimate, but safe in case) (taxes is a whole other problem...)
STARTING_CASH = 10_000 # explanatory

# options ---
#crossover - own SPY when 50 day > 200 day avg
#above_200 - own SPY when price > 200 day avg
#vol_target - own less when volatile, own more when market is stable
#rsi_dip - buy after sharp drop, sell upon recovery
STRATEGY = "vol_target"
TARGET_VOL = 0.12       # what it is aiming for in volatilty target
RSI_WINDOW = 14 
RSI_BUY = 30            # buy when rsi goes below
RSI_SELL = 70           # sell when rsi goes above (i wish i got into rsi)


def get_prices(ticker, start, end):
    data = yf.download(ticker,start=start,end=end,auto_adjust=True,progress=False) # breaks Sometimes (once im not sure)
    prices = data["Close"].squeeze() 
    prices.name = "price"
    return prices.dropna()


def compute_rsi(prices, window):
    change = prices.diff()
    avg_gain = change.clip(lower=0).rolling(window).mean()
    avg_loss = (-change.clip(upper=0)).rolling(window).mean()
    return 100 - 100 / (1 + avg_gain / avg_loss)


def run_backtest(prices):
    df = pd.DataFrame({"price": prices})

    # indicators
    df["short_ma"] = df["price"].rolling(SHORT_WINDOW).mean()
    df["long_ma"] = df["price"].rolling(LONG_WINDOW).mean()
    df["market_return"] = df["price"].pct_change()
    df["volatility"] = df["market_return"].rolling(20).std() * np.sqrt(252)
    df["rsi"] = compute_rsi(df["price"], RSI_WINDOW)
    df = df.dropna()

    # how much money is in the given market -> (1 = all in, 0 = all cash)
    if STRATEGY == "crossover":
        df["signal"] = (df["short_ma"] > df["long_ma"]).astype(float)
    elif STRATEGY == "above_200":
        df["signal"] = (df["price"] > df["long_ma"]).astype(float)
    elif STRATEGY == "vol_target":
        df["signal"] = (TARGET_VOL/df["volatility"]).clip(upper= 1.0)
    elif STRATEGY == "rsi_dip":
        signal = pd.Series(np.nan, index = df.index)
        signal[df["rsi"] < RSI_BUY] = 1.0
        signal[df["rsi"] > RSI_SELL] = 0.0
        df["signal"] = signal.ffill().fillna(0)

    # Trade are done the next day's return cause i cant look in the future
    df["position"] = df["signal"].shift(1).fillna(0)

    # returns
    df["market_return"] = df["market_return"].fillna(0)
    trades = df["position"].diff().abs().fillna(0) 
    df["strategy_return"] = df["position"]*df["market_return"] - trades*COST_PER_TRADE

    # value over time
    df["strategy_value"] = STARTING_CASH*(1 + df["strategy_return"]).cumprod()
    df["buyhold_value"] = STARTING_CASH*(1 + df["market_return"]).cumprod()

    return df,int((trades > 0).sum())


def metrics(returns, values):
    years = len(returns) / 252  # ~252 trading days per year (251...252 doesnt matter)
    total_return = values.iloc[-1]/values.iloc[0] - 1
    cagr = (values.iloc[-1]/values.iloc[0])**(1 / years) - 1
    sharpe = np.sqrt(252) * returns.mean()/returns.std() if returns.std() > 0 else 0
    drawdown = values/values.cummax() - 1
    return {
        "Final value": f"${values.iloc[-1]:,.0f}",
        "Total return": f"{total_return:.1%}",
        "Annual return": f"{cagr:.1%}",
        "Sharpe": f"{sharpe:.2f}",
        "Max drop": f"{drawdown.min():.1%}",
    }


def main():
    print(f"downloading {TICKER} prices") # f strings need to be in all languages
    prices = get_prices(TICKER,START,END)
    df,num_trades = run_backtest(prices)

    strat = metrics(df["strategy_return"],df["strategy_value"])
    hold = metrics(df["market_return"],df["buyhold_value"])

    print(f"\nRun {df.index[0].date()} to {df.index[-1].date()}  |  "f"Strategy: {STRATEGY}  |  {num_trades} trading days\n")
    print(f"{'Metric':<22}{'Strategy':>14}{'Buy & Hold':>14}")
    print("--------------------------------------------------------")
    for key in strat:
        print(f"{key:<22}{strat[key]:>14}{hold[key]:>14}")

    # plotting
    fig, (ax1, ax2) = plt.subplots(2,1,figsize=(11,8),sharex=True)
    ax1.plot(df.index,df["price"],label=f"{TICKER} price",color="black",linewidth=1)
    ax1.plot(df.index,df["short_ma"],label=f"{SHORT_WINDOW}-day MA")
    ax1.plot(df.index,df["long_ma"],label=f"{LONG_WINDOW}-day MA")
    ax1.set_title(f"{TICKER} with moving averages")
    ax1.legend()

    ax2.plot(df.index,df["strategy_value"],label=f"Strategy ({STRATEGY})")
    ax2.plot(df.index,df["buyhold_value"],label="Buy & hold")
    ax2.set_title("Portfolio ($)")
    ax2.legend()

    plt.tight_layout()
    plt.savefig("results.png", dpi=150)
    print("\nresults.png saved")
    plt.show()


if __name__ == "__main__":
    main()