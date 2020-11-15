from pandas_datareader import data
from datetime import datetime, timedelta
import sys
from datetime import datetime, date
from typing import Set, Dict
import logging
from pandas import DataFrame
from numpy.linalg import inv

log = logging.getLogger(__name__)


def calc_kelly_leverages(securities: Set[str],
                         start_date,
                         end_date,
                         risk_free_rate: float = 0.04) -> Dict[str, float]:
    """Calculates the optimal leverages for the given securities and
    time frame. Returns a list of (security, leverage) tuple with the
    calculate optimal leverages.
    Note: risk_free_rate is annualized
    """
    f = {}
    ret = {}
    excess_return = {}

    # Download the historical prices from Yahoo Finance and calculate the
    # excess return (return of security - risk free rate) for each security.
    for symbol in securities:
        try:
            hist_prices = data.DataReader(symbol,
                     start=start_date,
                     end=end_date,
                     data_source='yahoo')
        except IOError as e:
            raise ValueError(f'Unable to download data for {symbol}. '
                             f'Reason: {str(e)}')

        f[symbol] = hist_prices

        ret[symbol] = hist_prices['Close'].pct_change()
        # risk_free_rate is annualized
        excess_return[symbol] = (ret[symbol] - (risk_free_rate / 252))

    # Create a new DataFrame based on the Excess Returns.
    df = DataFrame(excess_return).dropna()

    # Calculate the CoVariance and Mean of the DataFrame
    C = 252 * df.cov()
    M = 252 * df.mean()

    # Calculate the Kelly-Optimal Leverages using Matrix Multiplication
    F = inv(C).dot(M)

    # Return a list of (security, leverage) tuple
    return {security: leverage
            for security, leverage in zip(df.columns.values.tolist(), F)}


def main():
    """Entry point of Kelly Criterion calculation."""
    logging.basicConfig(level=logging.INFO)

    log.info("Kelly Criterion calculation")


    # Calculate the Kelly Optimal leverages
    try:
        investment = [21000, 144600-8955, 35820-900, 15100+100]
        leverages = calc_kelly_leverages(
            ['0175.HK', '0981.HK', '1810.HK', '2800.HK', '6030.HK', '9618.HK', '9633.HK', '9988.HK'],
            # ['0175.HK', '0981.HK', '9618.HK', '9633.HK'],
            datetime.date(datetime.now() - timedelta(6 * 30)),
            datetime.date(datetime.now()),
            0.0047)  # http://www.market-risk-premia.com/hk.html
    except ValueError as e:
        log.error(f"Error during Kelly calculation: {str(e)}")
        sys.exit(-1)

    # Print the results if calculation was successful
    if leverages:
        log.info("No short! Leverages per security:")
        sum_leverage = 0
        for symbol, leverage in leverages.items():
            # We don't short, so only calculate with those leverage > 0
            sum_leverage += leverage

        log.info(f"Sum leverage: {sum_leverage}")

        for symbol, leverage in leverages.items():
            log.info(f"  {symbol}: {leverage:.2f}")

        # log.info(f"Max leverage: {maximum_leverage}, Equities Value: HKD {equity_value}")


if __name__ == '__main__':
    main()

