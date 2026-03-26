# [MVR-REF: 2.2] - DATA SOURCING AND FORENSIC CONTROLS
# -------------------------------------------------------------------------
# LAYER: Bronze (raw ingestion)
# PURPOSE: This layer provides verification of S&P 500 Index (^GSPC) closing prices.
# CONTROLS: Controls include a completeness check (Gap Days) & outlier mitigation (3-sigma).
# -------------------------------------------------------------------------

# 1. Install specific libraries.
%pip install arch yfinance

import pandas as pd
import numpy as np
import yfinance as yf
from arch import arch_model
from statsmodels.stats.diagnostic import acorr_ljungbox 
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Injest raw data and save to Databricks file system (DBFS).
TICKER = "^GSPC"
df_raw = yf.download(TICKER, start="2016-01-01",
                     end="2024-01-01", progress=False).reset_index()
df_raw.columns = [c[0] if isinstance(c, tuple) else c for c in
df_raw.columns] # Fix MultiIndex if present

# Simulate messy data (duplicates and outliers).
df_dirty = pd.concat([df_raw, df_raw.sample(n=min(50, len(df_raw)))], axis=0)
df_dirty.loc[df_dirty.sample (frac=0.01).index, 'Close'] *= 100 # Fat fingers

# Save data to Bronze layer path.
spark_df = spark.createDataFrame(df_dirty)
# Use saveAsTable instead of .save() to bypass the DBFS permission issue
spark_df.write.mode("overwrite").format("delta").saveAsTable("bronze_market_data")
print("Bronze layer: raw data ingested with intential corruptions.")
