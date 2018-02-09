
PoloniexPositionAPI
===================

[![NPM Version][https://img.shields.io/pypi/v/poloniexpositionapi.svg]][https://pypi.python.org/pypi/poloniexpositionapi]
[![TravisCI][https://img.shields.io/travis/siwik75/poloniexpositionapi.svg]][https://travis-ci.org/siwik75/poloniexpositionapi]
[![Documentation Status][https://readthedocs.org/projects/poloniexpositionapi/badge/?version=latest]][https://poloniexpositionapi.readthedocs.io/en/latest/?badge=latest]


Using Poloniex API - gathers your Balance and All trades to determine your gain/loss on current position and per coin basis.


* Free software: GNU General Public License v3
* Documentation: https://poloniexpositionapi.readthedocs.io.


Features
--------

* TODO

Usage
-----

```python
    from poloniexpositionapi import poloniexPosition

    PubKey=<Your Public Key from Poloniex>
    PrivKey=<YOUR SECRET KEY from Poloniex>
    myPol = poloniexPosition(APIKey=PubKey, Secret=PrivKey, flDebug=True, loadTrades=True)

    print "------------- S U M M A R Y -------------------"
    myPol.displayAccount()
    print "-------------Per Coin with Zero Balance Gain/Loss Report-------"
    print "XRP on BTC "
    myPol.displayCoinPairGainLoss(coin='XRP', basecoin='BTC')
    print "XRP on USDT"
    myPol.displayCoinPairGainLoss(coin='XRP', basecoin='USDT')
    print "NEOS"
    myPol.displayCoinPairGainLoss(coin='NEOS')
    print "XMR"
    myPol.displayCoinPairGainLoss(coin='XMR')
```

