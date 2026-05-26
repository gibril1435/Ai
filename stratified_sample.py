import pandas as pd
import numpy as np

# --- Configuration ---
filename = "Instagram_Analytics.csv"
encoding = "latin1"
sample_size = 500
strata_columns = ["media_type", "content_category"]
numeric_column = "engagement_rate"   # set to None or "" to skip binning
n_bins = 4
bin_labels = ["low", "medium", "high", "viral"]
method = "proportional"              # "proportional" or "equal"
output_filename = "Instagram_Analytics_500.csv"

# --- Load CSV ---
df = pd.read_csv(filename, encoding=encoding)
print(f"Total rows loaded: {len(df)}")

# --- Bin numeric column into quantile tiers and append as an additional stratum ---
active_strata = list(strata_columns)
if numeric_column:
    bin_col = f"_bin_{numeric_column}"
    df[bin_col] = pd.qcut(
        df[numeric_column], q=n_bins, labels=bin_labels, duplicates="drop"
    )
    active_strata.append(bin_col)

# --- Build composite strata key by joining all stratification columns ---
df["_strata"] = df[active_strata].astype(str).agg("__".join, axis=1)
strata_counts = df["_strata"].value_counts()
n_strata = len(strata_counts)
print(f"Number of strata: {n_strata}")

# --- Compute per-stratum row allocation based on chosen method ---
if method == "proportional":
    # Each stratum gets a share proportional to its population weight
    allocations = (strata_counts / len(df) * sample_size).round().astype(int)
elif method == "equal":
    # Every stratum receives the same base allocation
    per_stratum = sample_size // n_strata
    allocations = pd.Series(per_stratum, index=strata_counts.index)
else:
    raise ValueError(f"Unknown method: {method!r}. Use 'proportional' or 'equal'.")

alloc_dict = allocations.to_dict()


def _sample_group(g: pd.DataFrame) -> pd.DataFrame:
    # Cap allocation at actual stratum size so we never request more than available
    key = g.name  # Use .name to safely get the current group key
    n = min(alloc_dict.get(key, 0), len(g))
    return g.sample(n=n, random_state=42)


# --- Sample each stratum via groupby; over-allocated strata are capped automatically ---
sampled = df.groupby("_strata", group_keys=False).apply(_sample_group)

# --- Trim randomly if the total exceeds sample_size (rounding artefacts) ---
if len(sampled) > sample_size:
    sampled = sampled.sample(n=sample_size, random_state=42)

# --- Pad from unused rows if total falls short of sample_size ---
if len(sampled) < sample_size:
    deficit = sample_size - len(sampled)
    remainder = df.drop(index=sampled.index)
    pad = remainder.sample(n=min(deficit, len(remainder)), random_state=42)
    sampled = pd.concat([sampled, pad])

# --- Drop all helper columns (_strata, _bin_*) before writing output ---
helper_cols = [c for c in sampled.columns if c == "_strata" or c.startswith("_bin_")]
sampled = sampled.drop(columns=helper_cols)

# --- Save stratified sample; preserve original column structure, no row index ---
sampled.to_csv(output_filename, index=False)
print(f"Final sample size: {len(sampled)}")

# --- Verification: distribution of each strata column in the final sample ---
for col in strata_columns:
    print(f"\nValue counts for '{col}':")
    print(sampled[col].value_counts())

if numeric_column:
    print(f"\nValue counts for '{numeric_column}' (binned into {n_bins} tiers):")
    rebin = pd.qcut(sampled[numeric_column], q=n_bins, labels=bin_labels, duplicates="drop")
    print(rebin.value_counts().sort_index())
