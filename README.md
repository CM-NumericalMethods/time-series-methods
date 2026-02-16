# GJR-GARCH Volatility Validator and Capital Risk Forecast Engine

**Craig Masters, Ph.D.**

**December 2025**

## 1 Project Overview and Value

The primary aim of this particular project is to provide superior, conditional forecasts of Value-at-Risk (VaR) and volatility using a custom GJR-GARCH time series model, though it can be adapted to any domain where extreme events (shocks) have an asymmetric and persistent influence. As a few examples, besides the stock market forecast demonstrated here, the model could be easily applied to:

* **Healthcare and Insurance:** Volatility is typically increased more dramatically as a result of negative shocks such as a major regulatory audit finding or a new public health crisis than it is by positive shocks like new drug approvals, consistent with the asymmetry of the GJR-GARCH model.
* **Energy and Utilities:** The GJR-GARCH model could be applied to optimize operational reserves and manage real-time load balancing to help prevent catastrophic blackouts, since the asymmetry accounts for greater volatility impact of heatwaves and deep freezes as versus to planned outages for maintenance, while "standard" GARCH does not.
* **E-commerce and Supply Chain:** Negative shocks such as shipping disasters or factory closures tend to impact volatility more than positive shocks such as routine, expected increases in successful fulfillment.
* **IT Operations and Cybersecurity:** Scheduled maintanence and software updates do not tend to impact volatility in system health metrics as much as negative shocks such as a major data center failure. This custom GJR-GARCH model could be used to better allocate resources for response teams, and to forecast the risk-adjusted cost of system failure insurance.

Apart from the variety of domain applications, this custom model includes the advantage of explicitly modeling leverage effects (i.e., negative shocks increase volatility more than positive shocks) by use of the GJR-GARCH ($\gamma\$) parameter, increased regulatory validation via the Ljung-Box white noise test (which throws a custom exception if the model fails the test), and conservative forecasting by use of the heavy-tailed student's ($t$)-distribution, accounting for leptokurtosis (fat tails), and leading to more robust estimates of VaR for capital allocation.

## 2 Methodology and Theoretical Rigor

### 2.1 Volatility Asymmetry

The GJR version of the model, specifically, is distinguished for its ability to capture leveraging, whereas standard GARCH cannot. The GJR-GARCH equation is

$$
\sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \gamma I_{t-1} \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2
$$

where $(\omega)$ stands for the long-run average variance, $(\alpha)$ represents a measure of the impact of positive, lagged shocks, the key asymmetry or leveraging term is represented by $(\gamma)$, and $(\beta)$ measures the persistence of volatility from the previous period.

### 2.2 Maximum Likelihood and Optimization

The GJR-GARCH structure is too complicated to carry out maximum likelihood estimation in closed form, requiring advanced numerical optimization techniques to find the parameters $(\omega, \alpha, \gamma,)$ and $(\beta)$.

1.  **Maximum Likelihood Estimation (MLE):**
    * (a) To estimate the model parameters, the log-likelihood function of the Student's $(t)$ distribution is maximized. This estimation process yields the values for the paramters that make the observed market returns the most probable outcome under the volatility process that has been specified.
    * (b) MLE is used because it is the statistically optimal method for estimating conditional volatility models. This produces efficient and asymptotically normal estimates.

2.  **Numerical Optimization:**
    * (a) The maximization is performed iteratively using the Broyden-Fletcher-Goldfarb-Shanno (BFGS) algorithm.
        * *Update: the initial research phase considered the Log-Likelihood surface through the lens of quasi-Newton methods like BFGS. However, for the production-grade engine, **SLSQP** was verified as the active solver. This is numerically superior for GJR-GARCH because it explicitly respects the parameter bounds necessary to maintain positive-definite variance. The transition from the research version to the production version regarded stabilizing this SLSQP routine through better data conditioning (the 504-day window).*
    * (b) BFGS is a quasi-Newton method that efficiently approximates the second derivatives (the Hessian matrix) of the log-likelihood function to rapidly find the global maximum while maintaining stability. The rapidity and stability of this approximation is critical for production environments.
         * *Update: another reason SLSQP is used instead of BFGS is that BFGS is unconstrained while SLSQP is constrained and is thus suited for GARCH models.*

## 3 Regulatory and Audit Diagnostics

The model is validated using a falsification structure by way of a custom exception which ensures the model cannot be deployed if diagnostics fail.

1.  **Ljung-Box White Noise Validation:**
    * (a) This test is used to detect remaining autocorrelation in the standard residuals, $(z_t)$. A high p-value confirms the mean equation is correctly specified.
    * (b) Ljung-Box also tests for remaining ARCH effects (volatility clustering) in the squared residuals, $(z_t^2$). A high p-value confirms the GJR-GARCH has fully captured all volatility dynamics.

2.  **Structural Necessity:** An explicit check that $(\gamma > 0$), with p-value below the defined $(\alpha$)-level (0.05) is also included. This confirms that the asymmetric model is structurally necessary.

## 4 Performance Demonstration

As part of demonstrating performance, the model was caibrated using S&P 500 returns from 2019 to 2024.

### 4.1 Static Fit and Conditional Forecast

| Metric | Hist Baseline | GJR-GARCH Forecast | Analysis | 
 | ----- | ----- | ----- | ----- | 
| **99% VaR** | \-3.6590% | \-6.6028% | **Conservative** | 
| **Difference** | N/A | \-2.9438% | GJR-GARCH predicts 2.94% larger loss, worst-case providing a crucial safety margin reflective of recent volatility clusters. | 

### 4.2 Out-of-Sample Performance: Rolling Window Backtesting

<!-- To validate the model's predictive power, a one-step-ahead rolling window backtest must be performed. This simulates real-world usage where the model is refitted daily on the most recent data (the estimation window) to forecast the next day's VaR (the forecast horizon). This validation module is currently under development; out-of-sample violation ratios and Kupiec POF test (first line of defence) results will be published here when completed. -->

To validate the model's predictive power, a one-step-ahead walk-forward (rolling window) bactest was performed. This iterative process refits the model daily to forecast the next day's VaR, ensuring the model can adapt to changing market regimes.

#### 4.2.1 Development of the Backtest (Research to Production)

The initial iteration (the second research version which included the Kupiec test--Python script to be uploaded) of the GJR-GARCH model failed the rigorous Kupiec POF (Proportion of Failures) test. While the model was mathematically sound, it proved to be overly conservative, making it unresponsive in the backtest. This resulted in zero exceedences and a failure to accurately reflect the true risk distribution.

**Research Version Backtest Results (FAIL):**

* **Total Days:** 875 | **Actual Exceedences:** 0 | **Hit Ratio:** 0.00\%
* **Kupiec LR:** 17.5881 | **p-value:** 0.0000
* **Independence LR:** -0.0000 | **Independence p-value:** 1.0000

Two interesting results are exhibited above. The first is the independence LR (for the Christofferesen Independence test) of *negative* 0.000. The negative sign indicates that the optimizer was approaching from the negative side of the number line. This happens because of the subtraction of two nearly identical floating point numbers resulting from the <!-- natural --> logarithms used in the calculation of the Christoffersen test. The result was actually a miniscule finite negative number, but this was output as "-0.0000" because the script said to round to four decimal places. The second interesting aspect is that the Independence test was a perfect pass. The null hypothesis was perfectly accepted. However, this is a "spurious success" because the model already failed the Kupiec test. Because there were no exceedences at all, there were no exceedences to test for "clumping" (e.g., a succession of exceedences as opposed to exceedences scattered throughout the window).

This version of the model is overly conservative. It is setting the VaR too low, such that no actual returns can fall beneath it. If a financial institution were to act on this result, it would tend to reserve too much capital, resulting in a potentially large opportunity cost for not putting more at risk (at least when restricting attention to the VaR threshold and ignoring tail risk metrics such as Expected Shortfall).

**Modifications for the Production Version:**

To resolve the failure of the research version, the optimization algorithm was refined to improve parameter convergence under high-volatility regimes, and the Student's $t$ degrees-of-freedom estimation was adjusted to better capture the excess kurtosis of the returns. Additionally, the window was increased from 252 days to 504 days to allow the optimizer to converge, providing better estimation of the parameters of the GJR-GARCH equation. In other words, the optimizer cannot see enough market events in 252 days to find a stable mathematical solution. Doubling the window size allowed the optimizer to reach numerical convergence and capture the volatility and asymmetry (leverage effect) it could not capture over 252 days. In addition to this, including a rigid scale factor (scale_factor: float = 10.0) made the research version of the model a bit of a blunt instrument that was insensitive to a regime change. In the production model, the dullness was sharpened with rescale=True, allowing the VaR floor to be reactive rather than static.

Regarding the optimizer, initial documentation reflected evaluation of the model through the lens of standard quasi-Newton solvers such as BFGS. However, after moving to the production version of the model, deeper audit of the arch library's underlying mechanics revealed that SLSQP was the actual optimization engine that provided stability for my constraints. The documentation is now updated to be consistent with this realization. This is an important point for regulatory audit trails.

**Production Version Backtest Results (PASS):**

The refined production version of the GJR-GARCH passed both the Kupiec POF and the Christoffersen Independence tests, confirming that exceedences are both infrequent and not clustered (they are independent), which is crucial for institutional risk management.

* **Total Days:** 1507 | **Actual Exceedences:** 13 | **Hit Ratio:** 0.86\% (Target: 1.0\%)
* **Kupiec LR:** 0.3012 | **p-value:** 0.5831 (**SUCCESS**)
* **Independence LR:** 0.2264 | **Independence p-value:** 0.6342 (**SUCCESS**)

<!-- "In my initial documentation and research phase, I was evaluating the model through the lens of standard quasi-Newton solvers like BFGS. However, upon moving to the 'finished' production version (V11), I performed a deeper audit of the arch library's underlying mechanics. I realized that SLSQP was the actual engine providing the stability for the constraints. I've since updated my documentation to reflect this, as accuracy in the 'information layer' of the model is paramount for regulatory audit trails." -->

<!-- "To resolve the convergence failures and Kupiec test failures of the research version, the estimation window was expanded from 252 to 504 days. While the underlying SLSQP optimization algorithm remained consistent, the increased sample size provided a higher density of 'tail events' and negative innovations. This improved the numerical conditioning of the log-likelihood function, allowing the optimizer to successfully converge on stable parameters for the asymmetry ($\gamma$) and the Student’s $t$ degrees-of-freedom—features that were previously unestimable or unstable in the shorter 252-day window." -->

### 4.3 Second Line Audit Summary

The following table reports the in-sample diagnostics for the second line audit summary:

| Diagnostic | Requirement | Result | Status | 
 | ----- | ----- | ----- | ----- | 
| **Ljung-Box Mean (p)** | $(p > 0.05)$ | 0.2678 | **PASS** | 
| **Ljung-Box Variance (p)** | $(p > 0.05)$ | 0.9782 | **PASS** | 
| **Leverage Effect (**$(\gamma)$**)** | Positive & Significant | $(\gamma = 0.2619$) ($(p=0.0000$)) | **CONFIRMED** | 
| **Validation Status** | All Checks Passed | N/A | **PASS** | 

## 5 Usage, Requirements, and MLOps

### Prerequisites

* Python 3.8+
* arch, yfinance, statsmodels, pandas, numpy

### Quick Start

To run the validation script using the default S&P 500 data: `python gjr_garch_validator.py`

### Core Class Integration

The model is encapsulated in a reusable class designed for enterprise integration:

`python from gjr_garch_validator import GJR_GARCHValidator`

#### 1. Instantiate the Validator: 
`validator = GJR_GARCHValidator(p=1, q=1, significance_level=0.05)`

#### 2. Fit and Validate (raises Model Validation Failure on audit failure): 
`validator.fit(returns_series)`

#### 3. Retrieve Key Risk Metrics:
`var_99 = validator.get_value_at_risk(alpha=0.01)`

`conditional_vol = validator.get_conditional_volatility()`

`audit_report = validator.get_audit_report()`
