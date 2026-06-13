import logging

logger = logging.getLogger("Rebalancer")

class PortfolioRebalancer:
    """
    Computes portfolio rebalancing actions to match target asset allocation metrics.
    """
    def __init__(self, target_weights=None):
        """
        :param target_weights: Dict representing target percentages, e.g.:
                               {
                                   'CRYPTO': 15.0,
                                   'B3_STOCK': 25.0,
                                   'FII': 20.0,
                                   'FIXED_INCOME': 40.0
                               }
        """
        # Default allocation strategy: 40% CDBs (low risk), 20% FIIs (yield), 25% B3, 15% Crypto
        self.target_weights = target_weights or {
            'CRYPTO': 15.0,
            'B3_STOCK': 25.0,
            'FII': 20.0,
            'FIXED_INCOME': 40.0
        }
        
    def calculate_rebalancing(self, current_balances):
        """
        Calculates the buy/sell orders or asset transfers required to realign
        the current asset balances to target weights.
        
        :param current_balances: Dict of {asset_class: balance_value}
        :return: Dict containing target allocations, deviations, and recommended operations.
        """
        total_value = sum(current_balances.values())
        if total_value == 0:
            return {"error": "Portfolio is empty."}
            
        rebalancing_actions = {}
        
        for asset_class, target_pct in self.target_weights.items():
            current_val = current_balances.get(asset_class, 0.0)
            current_pct = (current_val / total_value) * 100.0
            
            target_val = (target_pct / 100.0) * total_value
            deviation_val = target_val - current_val
            deviation_pct = target_pct - current_pct
            
            rebalancing_actions[asset_class] = {
                "current_value": current_val,
                "current_percentage": current_pct,
                "target_value": target_val,
                "target_percentage": target_pct,
                "deviation_value": deviation_val,
                "deviation_percentage": deviation_pct,
                "action": "BUY / DEPOSIT" if deviation_val > 0 else ("SELL / WITHDRAW" if deviation_val < 0 else "HOLD")
            }
            
        return {
            "total_portfolio_value": total_value,
            "rebalancing_details": rebalancing_actions
        }
