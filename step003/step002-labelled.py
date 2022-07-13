
# region imports
from AlgorithmImports import *
# endregion

class HyperActiveFluorescentOrangeDog(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2017, 1, 1)
        self.SetEndDate(2017, 4, 1)
        self.SetCash(100000)

        equity = self.AddEquity("IBM", Resolution.Minute)
        equity.SetDataNormalizationMode(DataNormalizationMode.Raw)
        self.underlying = equity.Symbol
        self.SetBenchmark(self.underlying)

        self.call = str()


    def OnData(self, slice):
        #if not self.Portfolio.Invested:
        #    self.SetHoldings("SPY", 0.33)
        #    self.SetHoldings("BND", 0.33)
        #    self.SetHoldings("AAPL", 0.33)
        if not self.Portfolio[self.underlying].Invested:
            self.MarketOrder(self.underlying, 100)
            self.Log("MARKETORDER " + str(self.underlying) + " — 100")
        if not (self.Securities.ContainsKey(self.call) and self.Portfolio[self.underlying].Invested):
            self.call = self.AddContract(slice)
            self.Log("ADD_CONTRACT " + str(self.call) + " — ")
        if self.Securities.ContainsKey(self.call) and not self.Portfolio[self.call].Invested:
            self.Sell(self.call, 1)
            self.Log("SELL " + str(self.call))
    
    def AddContract(self, slice):
        filtered_contracts = self.InitialFilter(-3, 3, 0, 30)
        if len(filtered_contracts) == 0: return str()
        else:
            call = [x for x in filtered_contracts if x.ID.OptionRight == OptionRight.Call]
            contracts = sorted(sorted(call, key=lambda x: abs(self.Securities[self.underlying].Price - x.ID.StrikePrice)),
                key=lambda x: x.ID.Date, reverse=True
            )
            if len(contracts) > 0:
                self.AddOptionContract(contracts[0], Resolution.Minute)
                return contracts[0]
            else:
                return str()
    
    def InitialFilter(self, min_strike_rank, max_strike_rank, min_expiry_date, max_expiry_date):
        contracts = self.OptionChainProvider.GetOptionContractList(self.underlying, self.Time.date())
        if len(contracts) == 0: return []
        contract_list = [i for i in contracts if min_expiry_date < (i.ID.Date.date() - self.Time.date()).days < max_expiry_date]
        atm_strike = sorted(contract_list, key=lambda x:abs(x.ID.StrikePrice - self.Securities[self.underlying].Price))[0].ID.StrikePrice
        strike_list = sorted(set([i.ID.StrikePrice for i in contract_list]))
        atm_strike_rank = strike_list.index(atm_strike)
        try:
            strikes = strike_list[(atm_strike_rank+min_strike_rank):(atm_strike_rank+max_strike_rank)]
        except:
            strikes = strike_list
        filtered_contracts = [i for i in contract_list if i.ID.StrikePrice in strikes]
        return filtered_contracts
    
    def OnOrderEvent(self, orderEvent):
        self.Log(str(orderEvent))


