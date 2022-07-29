#!/usr/bin/env python3

"""
This script is used to download OHLCV data from MT5
using the MetaTrader5 pypi package
MetaTrader 5 application has to be installed
Windows only
"""

import pandas as pd
import shutil
import sys

import MetaTrader5 as mt5

from datetime import datetime
from pathlib import Path


# mt5 directory
mt5dir = 'C:/Program Files/MetaTrader 5 IC Markets (SC) - 1'
# mt5dir = 'C:/Program Files/Pepperstone MetaTrader 5'
# mt5dir = "C:/Program Files/Tickmill MT5 Terminal"
mt5loc = Path(mt5dir) / 'terminal64.exe'

workdir = 'C:/Users/nikki/workspace/algotrading/mt5dl'
workloc = Path(workdir)

# connect to MetaTrader 5
if not mt5.initialize(str(mt5loc)):
    print("initialize() failed")
    mt5.shutdown()
    
# Print connection status
print(
    f'Connected to {mt5.terminal_info().name}',
    f'at {mt5.terminal_info().path}',
    f'with server {mt5.account_info().server}'
)

# Print run timestamp
today = datetime.now()
print(f'Run at {today}')

try:
    # Create list of symbols to download
    symbols = [symbol.name for symbol in mt5.symbols_get("*, !*.*")]

    # How many ohlc data to download
    lookback = 1000000
    # lookback = 10

    # Set which timeframes to download
    tf_dict = {
        'd1': mt5.TIMEFRAME_D1,
        'h4': mt5.TIMEFRAME_H4,
        'h1': mt5.TIMEFRAME_H1,
        'm30': mt5.TIMEFRAME_M30,
        'm15': mt5.TIMEFRAME_M15,
        'm5': mt5.TIMEFRAME_M5,
        'm1': mt5.TIMEFRAME_M1
    }

    cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

    # Create data parent directory
    data_dir = workloc / 'data'

    # Backup directory if it exists
    if data_dir.exists():
        backup_dir = workloc / Path(f'data_bak_{today.strftime("%Y%m%d-%H%M%S")}')
        shutil.move(data_dir, backup_dir)

    try:
        data_dir.mkdir() 
    except FileExistsError:
        print(f'{data_dir} already exists. Check if contains file')
        mt5.shutdown()
        sys.exit()

    for tf, tf_mt5 in tf_dict.items():
        ohlcv = {}
        
        # Create directory for each timeframes
        tf_dir = data_dir / f'{tf}'

        try:
            tf_dir.mkdir() 
        except FileExistsError:
            print(f'{data_dir} already exists. Check if contains file')
            break

        # Create a dictionary where the key is the ticker
        # and the value is a pandas dataframe of the OHLC time series
        for ticker in symbols:
            ohlcv[ticker] = pd.DataFrame(
                mt5.copy_rates_from_pos(
                    ticker,
                    tf_mt5,
                    0,
                    lookback
                )
            )
            try:
                ohlcv[ticker]['time'] = pd.to_datetime(
                    ohlcv[ticker]['time'],
                    unit='s'
                )
                # ohlcv[ticker] = ohlcv[ticker].tz_localize('utc')
                ohlcv[ticker].to_csv(tf_dir / f'{ticker}.csv', index=False)
            except KeyError:
                print(f'KeyError on {ticker}')
            except ValueError:
                print(f'ValueError on {ticker}')
        
        print(f'Finished downloading for {tf}')
    mt5.shutdown()
except KeyboardInterrupt:
    mt5.shutdown()
    sys.exit()