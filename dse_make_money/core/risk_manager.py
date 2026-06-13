import logging
from dse_make_money.config import settings

logger = logging.getLogger("RiskManager")

class RiskManager:
    """
    DSE Make Money Risk Manager Engine.
    Handles capital protection, drawdown limits, and automated treasury sweeps
    (transferring excess high-frequency profits to low-risk fixed income CDBs).
    """

    def __init__(self, current_allocations=None):
        """
        :param current_allocations: Dict containing asset class allocation values
                                    e.g., {'CRYPTO': 10000, 'B3_STOCK': 20000, 'FIXED_INCOME': 15000}
        """
        self.allocations = current_allocations or {}
        
    def evaluate_treasury_sweep(self, high_frequency_profit):
        """
        Evaluates whether a profit sweep from high-frequency/day trade (Crypto/B3)
        to Fixed Income (CDBs) is required to lock in gains and protect capital.
        
        Rule: If high frequency trade profit exceeds DAY_TRADE_PROFIT_TRIGGER_PCT,
        suggest transferring the surplus profit to low-risk Treasury.
        """
        logger.info("Evaluating treasury sweep opportunity...")
        
        # Calculate current total equity
        total_equity = sum(self.allocations.values())
        if total_equity == 0:
            logger.warning("Total portfolio equity is zero. Cannot evaluate sweep.")
            return {"sweep_recommended": False, "reason": "No equity detected"}
            
        fixed_income_val = self.allocations.get("FIXED_INCOME", 0.0)
        fixed_income_pct = (fixed_income_val / total_equity) * 100.0
        
        # Determine if we have excess profits to sweep
        target_profit_trigger = total_equity * (settings.DAY_TRADE_PROFIT_TRIGGER_PCT / 100.0)
        
        if high_frequency_profit >= target_profit_trigger:
            # Recommend sweeping 80% of excess profits to lock in the gains
            sweep_amount = high_frequency_profit * 0.80
            
            logger.warning(
                f"🚨 [SWEEP RECOMMENDED] Profit of R$ {high_frequency_profit:,.2f} "
                f"exceeded trigger threshold of R$ {target_profit_trigger:,.2f}."
            )
            return {
                "sweep_recommended": True,
                "sweep_amount": sweep_amount,
                "reason": f"High Frequency profit exceeded target threshold of {settings.DAY_TRADE_PROFIT_TRIGGER_PCT}%. Locking in 80% of profits.",
                "target_destination": "CDB / Fixed Income Treasury",
                "pix_key": settings.TREASURY_PIX_KEY
            }
            
        # Alternative rule: Rebalance if Fixed Income is below the target allocation
        if fixed_income_pct < settings.TREASURY_ALLOCATION_TARGET:
            deficit_amount = (settings.TREASURY_ALLOCATION_TARGET / 100.0 * total_equity) - fixed_income_val
            logger.info(
                f"Treasury allocation ({fixed_income_pct:.2f}%) is below target "
                f"({settings.TREASURY_ALLOCATION_TARGET}%). Deficit: R$ {deficit_amount:,.2f}."
            )
            return {
                "sweep_recommended": False,
                "reason": "Treasury allocation below target. Future trading profits should be directed to CDBs.",
                "deficit": deficit_amount
            }

        logger.info("Risk evaluation complete. Portfolios are within safe limits. No sweep recommended.")
        return {"sweep_recommended": False, "reason": "Allocations are balanced"}
        
    def calculate_drawdown_limit(self, current_balance, peak_balance):
        """
        Capital preservation logic: If drawdown exceeds 10%, recommend pausing
        automated executions/trading activities.
        """
        if peak_balance <= 0:
            return False
            
        drawdown = (peak_balance - current_balance) / peak_balance
        if drawdown >= 0.10: # 10% Drawdown Limit
            logger.critical(f"⚠️ [DRAWDOWN ALERT] Peak balance: R$ {peak_balance:,.2f} -> Current: R$ {current_balance:,.2f}. Drawdown is {drawdown*100:.2f}%!")
            return True
        return False
