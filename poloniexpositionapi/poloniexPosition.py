from poloniex import poloniex

import time
import json
import io
import os

class poloniexPosition:

    def __init__(self, APIKey, Secret, html=False, tradeFile="poltrades.json", configDir=".",
                 loadTrades=True, flDebug=False):
        """

        :param APIKey: Poloniex priovided API key - Must be enabled or call object with loadTrades=False
        :param Secret: Poloniex secret code to get into your account
        :param html: <Future Development for output using HTML>
        :param tradeFile: tradefile will contain all your trades once downloaded, can specify another one
        :param configDir: the directory in which to look for our trades
        :param loadTrades: whether to load the trades and make the API request towards Poloniex
        :param flDebug: dumps out all sort of info step by step to control how numbers are calculated.
        """

        self.APIKey = APIKey
        self.__secret = Secret

        self.tradeFile = tradeFile
        self.configDir = configDir

        self.flDebug = flDebug
        self.useHtml = html

        self.__polObj = poloniex(APIKey=APIKey, Secret=Secret)

        self.balances = self.__polObj.returnBalances()
        self.completeBalances = self.__polObj.returnBalances(complete=True)

        if 'error' in self.balances:

            print "\nERROR: Could not connect to Poloniex.\n\n\t\t%s\n" % self.balances['error']
            raise Exception('Cannot connect to Poloniex')

        self.tickers = self.__polObj.returnTicker()
        self.debugprint(self.tickers["BTC_BCH"])
        # raise Exception("HALT")

        lending_balances = self.__polObj.returnAvailableAccountBalances("lending")
        available_balances = self.__polObj.returnAvailableAccountBalances("exchange")
        self.debugprint(lending_balances)
        self.debugprint(available_balances)
        self.lendingBalance = float(lending_balances['BTC']) if lending_balances['lending'] else 0.0
        self.debugprint("Lending Bal - {}".format(self.lendingBalance) )
        self.loans = self.__polObj.returnActiveLoans()

        self.activeLoansBTC = 0.0
        for loan in self.loans['provided']:
            self.activeLoansBTC += float(loan['amount'])

        self.TotalValue = None
        self.TotalUSD = None

        self.allMyTrades = None
        self.highestTransaction = dict()
        self.flagNewTradesFound = False

        self.balancesLoadValues = dict()

        if loadTrades:
            if os.path.exists(self.configDir + "/" + self.tradeFile):
                with io.open(self.configDir + "/" + self.tradeFile, "r", encoding='utf-8') as f:
                    self.printout("INFO: Found %s - Loading Trades" % (self.configDir + "/" + self.tradeFile))
                    self.allMyTrades = json.load(f, encoding="utf")
            self.loadTrades()

    def printout(self, *args):

        if self.useHtml:
            pass
        else:
            print " ".join(map(str,args))

    def debugprint(self, *args):

        if self.flDebug:
            if self.useHtml:
                pass
            else:
                print "DEBUG > "," ".join(map(str,args))

    def setLastTradeLoaded(self, doapirequest=True):

        if not self.allMyTrades:
            return

        alltradeslist = list()

        for coinPair in self.allMyTrades:
            alltradeslist.extend(self.allMyTrades[coinPair])

        sorted_alltradeslist = sorted(alltradeslist, key=lambda k: k['globalTradeID'], reverse=True)

        self.highestTransaction['date'] = sorted_alltradeslist[0]['date']
        self.highestTransaction['globalTradeID'] = sorted_alltradeslist[0]['globalTradeID']
        self.highestTransaction['tsdate'] = poloniex.createTimeStamp(sorted_alltradeslist[0]['date'])

        self.debugprint("Highest loaded transaction is GlID: %s date : %s - TS %s" %
                        (sorted_alltradeslist[0]['globalTradeID'],
                         sorted_alltradeslist[0]['date'],
                         self.highestTransaction['tsdate'])
                        )

        if doapirequest:
            self.printout("Asking Poloniex for any newer trading after our last record : %s"
                          % sorted_alltradeslist[0]['date'])
            trades = self.__polObj.returnTradeHistory(currencyPair='all',
                                                      start=self.highestTransaction['tsdate'] + 1)
            self.debugprint(trades)
            if len(trades) > 0:
                self.flagNewTradesFound = True

    def loadTrades(self, currencyPair='all', start=None, end=None, doapirequest=True):

        '''
        :param currencyPair:  Can be specified to limit the API calls to one coinPair i.e. BTC_DASH
        :param start:    Can be specified to indicate start of period for examining trades (poloniex class' format)
        :param end:     Can be specified to indicate end of period for examining trades (poloniex class' format)
        :param doapirequest: When set to False it would inhibit API call and just examing file and allMyTrades(useful when offline)
        :return: None
        '''
        if currencyPair != 'all':
            examiningTickers = {k:v for (k,v) in self.tickers.iteritems() if k == currencyPair}
            calculatingAvgForCoin = {k:v for (k,v) in self.allMyTrades.iteritems() if k == currencyPair}
        else:
            calculatingAvgForCoin = self.allMyTrades # Examining all #
            examiningTickers = self.tickers # Examining all #

        if self.allMyTrades:

            self.setLastTradeLoaded(doapirequest)

            for currencyPairKey in examiningTickers:
                self.debugprint("Examining %s" % currencyPairKey)
                if not self.allMyTrades.has_key(currencyPairKey):
                    self.debugprint("adding list to allMyTrades %s" % currencyPairKey)
                    self.allMyTrades[currencyPairKey] = list()

                start=None
                startTS = start
                if len(self.allMyTrades[currencyPairKey]) > 0:
                    self.debugprint(self.allMyTrades[currencyPairKey][0]['date'])
                    startDate = self.allMyTrades[currencyPairKey][0]['date']
                    startTS = poloniex.createTimeStamp(startDate) + 1
                    self.debugprint("startDate is %s - ts: %s" % (startDate, start))
                else:
                    self.debugprint("No trades were in my trades for %s" % currencyPairKey)

                if startTS is not None and startTS <= self.highestTransaction['tsdate'] + 1:
                    if self.flagNewTradesFound:
                        self.debugprint(
                            "Setting startTS at %s because new Trades has been found above highest Transaction " %
                            self.highestTransaction['date'])
                        startTS = self.highestTransaction['tsdate'] + 1
                    else:
                        self.debugprint("Not calling API , because startTS %s < highest trade %s" %
                                        (startTS,
                                         self.highestTransaction['tsdate'])
                                            )
                        doapirequest = False

                if startTS is None and self.highestTransaction['tsdate']:
                    startTS = self.highestTransaction['tsdate'] + 1
                    self.debugprint("lifting startTS to above highest transaction.")

                if doapirequest:

                    trades = self.__polObj.returnTradeHistory(currencyPair = currencyPairKey, start = startTS)
                    self.debugprint(trades)

                    self.allMyTrades[currencyPairKey].extend(trades)
                    self.debugprint("gotten %s trades" % len(trades))
                    self.debugprint("after loading: %s" % self.allMyTrades[currencyPairKey])

        else:
            if doapirequest:
                self.printout("INFO: Trades were never loaded, loading for currencies: %s" % currencyPair)

                if start or end:
                    self.printout("ERROR: start or end specification not allowed when loading all trades for first time.")
                    raise ValueError("loadTrades(): does not allow start/end when loading all trades.")

                if currencyPair != 'all':
                    self.allMyTrades = dict()
                    self.allMyTrades[currencyPair] = list()
                    self.allMyTrades[currencyPair].extend(self.__polObj.returnTradeHistory(currencyPair=currencyPair
                                                                                           ))
                else:
                    self.allMyTrades = self.__polObj.returnTradeHistory(currencyPair = currencyPair,
                                                                        start = start, end = end)
            else:
                self.printout("WARNING: No Trades have ever been loaded. Should call loadTrades(doapirequest=True).")

        if doapirequest:
            self.printout("Saving all trades to %s" % self.configDir + "/" + self.tradeFile)
            with io.open(self.configDir + "/" + self.tradeFile,'w') as f:
                f.write(unicode(json.dumps(self.allMyTrades, ensure_ascii=True, indent=4, default=poloniex.DATE_FORMAT)))

        '''
            Calling method to determined and store highest(most recent) transaction / to be used with loadTrades
        '''
        self.setLastTradeLoaded(doapirequest=False)

        if not self.allMyTrades:
            self.printout("WARNING: No transactions were loaded from Poloniex.")
            return

        if currencyPair != 'all':
            calculatingAvgForCoin = {k:v for (k,v) in self.allMyTrades.iteritems() if k == currencyPair}
        else:
            calculatingAvgForCoin = self.allMyTrades # Examining all #

        '''
            Sorting and calculating avg price and quantity
        '''
        # sortedTrades = sorted(self.allMyTrades[currencyPair], key=lambda k: k['globalTradeID'])
        # self.debugprint("sorted Trades : %s" % sortedTrades)

        for coinPair in calculatingAvgForCoin:

            self.debugprint("Evaluating %s ..." % coinPair)
            if not self.balancesLoadValues.has_key(coinPair + "_STATS"):
                self.balancesLoadValues[coinPair + "_STATS"] =dict()

            boughtqta = 0.0
            soldqta = 0.0
            totalboughtBTC = 0.0
            balance = 0.0
            gainloss = 0.0
            soldfromtransferredamount = 0.0
            avgprice = 0.0

            for trade in sorted(self.allMyTrades[coinPair], key=lambda k: k['globalTradeID']):

                self.debugprint("\nOP: %s - qta %s - prc %s - dt [%s] - BTC %s" % (trade['type'], trade['amount'],
                                                                                   trade['rate'], trade['date'],
                                                                                   trade['total']))
                factor = 1
                if trade['type'] == 'sell':
                    factor = -1

                if factor == 1:
                    boughtqta += float(trade['amount'])
                else:
                    soldqta += float(trade['amount'])

                if factor == 1: # BUY
                    totalboughtBTC += float(trade['total'])

                balance += float(trade['amount']) * factor

                if boughtqta > 0.0:
                    avgprice = totalboughtBTC / boughtqta
                # elif soldqta - boughtqta < 0.0:
                #         soldfromtransferredamount += soldqta
                #         gainloss += float(trade['total'])
                #
                #         avgprice = 0.0
                if balance < 0.0:

                    if factor == -1:
                        self.debugprint("Sold from transferred-in amount")
                        if balance == 0.0:
                            soldfromtransferredamount += float(trade['amount'])
                        else:
                            soldfromtransferredamount += - balance
                        gainloss += float(trade['total'])
                        avgprice = 0.0
                        balance = 0.0
                    else:
                        None

                elif balance == 0.0:
                    # gainloss += float(trade['total']) - totalboughtBTC
                    gainloss += (float(trade['rate']) - avgprice) * float(trade['amount'])
                    self.debugprint("Cleared position. AvgPrice = %s, Gain/Loss %s" % (avgprice, gainloss))

                    avgprice = 0.0

                self.debugprint("boughtqta %s - soldqta %s [ balance %s ] - gainloss %.8f - totalboughtBTC %s - avgPrice %.8f / soldfromtransferred %s"
                                % (boughtqta, soldqta, balance, gainloss, totalboughtBTC, avgprice,
                                   soldfromtransferredamount))

            '''
            Storing stats
            '''
            self.balancesLoadValues[coinPair + "_STATS"]['bought'] = boughtqta
            self.balancesLoadValues[coinPair + "_STATS"]['sold'] = soldqta
            self.balancesLoadValues[coinPair + "_STATS"]['balance'] = balance
            self.balancesLoadValues[coinPair + "_STATS"]['gainloss'] = gainloss
            self.balancesLoadValues[coinPair + "_STATS"]['avgprice'] = avgprice
            self.balancesLoadValues[coinPair + "_STATS"]['soldtfx'] = soldfromtransferredamount

            self.debugprint("Calculated position for %s - %s" %
                            (coinPair, self.balancesLoadValues[coinPair + "_STATS"]))

        return
        #
        # trades = self.__polObj.returnTradeHistory(currencyPair = currencyPair, start = start, end = end)
        #
        # for currencyPairKey in trades.iterkeys():
        #
        #     currency = currencyPair.split('_')[1]
        #     against = currencyPair.split('_')[0]
        #
        #     pself.printout("Loading %s, currency %s" % (currencyPairKey, currency))
        #
        #     lastTradeTs = poloniex.poloniex.createTimeStamp(trades[currencyPairKey][0]['date'])

    def displayAccount(self, html=False):

        self.printout("\n-------------------------- Poloniex Balance --------------------------\n")

        for loan in self.loans['provided']:
            # print loan
            renewing = 'Yes' if loan['autoRenew'] == 1 else 'No'
            if html:
                pass
            else:
                self.printout("Currency : {0} - Rate {1} % - Duration {2} days - Fees {3} / AutoRenew: {4} ".format(loan['currency'],
                                                                                                        loan['rate'],
                                                                                                        loan['duration'],
                                                                                                        loan['fees'],
                                                                                                        renewing))

        self.printout("-----------------------------\nLoaned BTC {:16.8f}\n-----------------------------".format(self.activeLoansBTC))

        TotalValue = 0.0
        TotalGainLoss = 0.0

        filtered_balances = {k:v for (k,v) in self.balances.iteritems() if v != '0.00000000'}

        for coin in filtered_balances:
            coinValue, coinGainLoss = self.displayCoinPairGainLoss(coin)
            TotalValue += coinValue
            TotalGainLoss += coinGainLoss

        self.TotalValue = TotalValue
        #self.debugprint(self.tickers["USDT_BTC"])
        self.TotalUSD = TotalValue * float(self.tickers["USDT_BTC"]['last'])

        self.printout("----------------------------- ============ +-+-+-+-+-+-+-+-+-\nOverall BTC {:16.8f} - $ {:5.2f}   G/L BTC {:10.8f}\n----------------------------- ============ +-+-+-+-+-+-+-+-+-".format(
            TotalValue, self.TotalUSD, TotalGainLoss))

    def displayCoinPairGainLoss(self, coin, basecoin='BTC'):

        boughtqta = 0.0
        soldqta = 0.0
        balance = 0.0
        gainloss = 0.0
        soldfromtransferredamount = 0.0
        avgprice = 0.0
        currentGainLoss = 0.0
        TotalGainLoss = 0.0

        if self.completeBalances[coin]['onOrders'] != '0.00000000':
            onOrder = float(self.completeBalances[coin]['onOrders'])
        else:
            onOrder = 0.0

        lendingbalanceBTC = None
        activeloansBTC = 0.0

        if coin == 'BTC':
            value = float(self.tickers["USDT_BTC"]['last'])
            percchange = float(self.tickers["USDT_BTC"]['percentChange'])

            BTCValue = float(self.balances[coin]) + onOrder + self.lendingBalance + self.activeLoansBTC
            # print " Value = %s - complete %s" % (balances[coin], complete_balances['BTC'] )
            lendingbalanceBTC = self.lendingBalance
            activeloansBTC = self.activeLoansBTC

        elif coin == 'USDT':
            percchange = float(self.tickers["USDT_BTC"]['percentChange'])
            value = float(self.tickers["USDT_BTC"]['last'])
            value = 1.0 / value
            BTCValue = float(self.balances['USDT']) * value
            lendingbalanceBTC = 0.0

        else:
            try:
                value = float(self.tickers[basecoin + "_" + str(coin)]['last'])

                percchange = float(self.tickers["BTC_" + str(coin)]['percentChange'])
                BTCValue = float(self.balances[coin]) * value
                lendingbalanceBTC = 0.0  # TODO
                activeloansBTC = 0.0  # TODO substitute with currency loan

                tkey = basecoin + "_" + str(coin) + "_STATS"

                if tkey in self.balancesLoadValues:
                    boughtqta = self.balancesLoadValues[tkey]['bought']
                    soldqta = self.balancesLoadValues[tkey]['sold']
                    balance = self.balancesLoadValues[tkey]['balance']
                    gainloss = self.balancesLoadValues[tkey]['gainloss']
                    soldfromtransferredamount = self.balancesLoadValues[tkey]['soldtfx']
                    avgprice = self.balancesLoadValues[tkey]['avgprice']
                else:
                    boughtqta = 0.0
                    soldqta = 0.0
                    balance = 0.0
                    gainloss = 0.0
                    soldfromtransferredamount = 0.0
                    avgprice = 0.0

                currentGainLoss = (value - avgprice) * float(self.balances[coin])
                TotalGainLoss += currentGainLoss
            except KeyError as e:

                self.debugprint("Coin {} is no longer valued - setting it to 0.0".format(coin))
                value = 0.0
                percchange = 0.0
                BTCValue = 0.0
                lendingbalanceBTC = 0.0

        PERCChange = percchange * 100

        try:
            self.printout(
                "{0:>4} - Qta {1:20.8f} (Ord: {5:6.4f})/(LdB: {6:6.4f})/(Loa: {7:6.4f})| Prc : {2:14.8f} - Total BTC = {3:9.8f} - Chg {4:+6.1f}%".format(
                    coin,
                    float(self.balances[coin]),
                    value,
                    BTCValue,
                    PERCChange,
                    onOrder,
                    lendingbalanceBTC,
                    activeloansBTC
                    ) +
                " G/L BTC {:+011.4f}| Bgt {:13.4f} Sld {:13.4f} Blc {:13.4f} GnL {:9.4f} [Avg Prc {:9.8f}]/ Tfx {:9.4f}".format(
                    currentGainLoss,
                    boughtqta, soldqta, balance, gainloss, avgprice, soldfromtransferredamount)
                )
        except ValueError as e:
            print "Error: %s - coin - %s " % (e.message, coin)

        return BTCValue, TotalGainLoss


