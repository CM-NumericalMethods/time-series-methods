# GJR-GARCH Volatility Validator and Capital Risk Forecast Engine

**Craig Masters, Ph.D.**

**December 2025**

## 1 Project Overview and Value

The primary aim of this particular project is to provide superior, conditional forecasts of Value-at-Risk (VaR) and volatility using a custom GJR-GARCH time series model, though it can be adapted to any domain where extreme events (shocks) have an asymmetric and persistent influence. As a few examples, besides the stock market forecast demonstrated here, the model could be easily applied to:

* **Healthcare and Insurance:** Volatility is typically increased more dramatically as a result of negative shocks such as a major regulatory audit finding or a new public health crisis than it is by postive shocks like new drug approvals, consistent with the asymmetry of the GJR-GARCH model.
* **Energy and Utilities:** The GJR-GARCH model could be applied to optimize operational reserves and manage real-time load balancing to help prevent catastrophic blackouts, since the asymmetry accounts for greater volatility impact of heatwaves and deep freezes as versus to planned outages for maintenance, while "standard" GARCH does not.
* **E-commerce and Supply Chain:** Negative shocks such as shipping disasters or factory closures tend to impact volatility more than positive shocks such as routine, expected increases in successful fulfillment.
* **IT Operations and Cybersecurity:** Scheduled maintanence and software updates do not tend to impact volatility in system health metrics as much as negative shocks such as a major data center failure. This custom GJR-GARCH model could be used to better allocate resources for response teams, and to forecast the risk-adjusted cost of system failure insurance.

Apart from the variety of domain applications, this custom model includes the advantage of explicitly modeling leverage effects (i.e., negative shocks increase volatility more than positive shocks) by use of the GJR-GARCH \\(\gamma\\) parameter, increased regulatory validation via the Ljung-Box white noise test (which throws a custom exception if the model fails the test), and conservative forecasting by use of the heavy-tailed student's \\(t\\)-distribution, accounting for leptokurtosis (fat tails), and leading to more robust estimats of VaR for capital allocation.

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
    * (b) BFGS is a quasi-Newton method that efficiently approximates the second derivatives (the Hessian matrix) of the log-likelihood function to rapidly find the global maximum while maintaining stability. The rapidity and stability of this approximation is critical for production environments.

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

To validate the model's predictive power, a one-step-ahead rolling window backtest must be performed. This simulates real-world usage where the model is refitted daily on the most recent data (the estimation window) to forecast the next day's VaR (the forecast horizon). This validation module is currently under development; out-of-sample violation ratios and Kupiec POF test (first line of defence) results will be published here when completed.

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
