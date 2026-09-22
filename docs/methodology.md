# Statistical Index Methodology & Econometric Framework

## 1. Official Context & Scope

The **Experimental Real-time Airfare Price Index (APIx)** is developed to augment official Indian price statistics published by the **Ministry of Statistics and Programme Implementation (MoSPI)**.

In the Consumer Price Index (CPI Base 2012=100), transport services constitute a significant portion of the *Transport and Communication* group (Group Weight: 8.59% in CPI Combined). However, civil aviation pricing in India follows real-time revenue management algorithms. Fares for identical city pairs vary by over 300% depending on the lead time between ticket issuance and scheduled departure.

APIx introduces an **advance-purchase stratified Laspeyres price index** with daily frequency, full provenance, and alignment with **DGCA (Directorate General of Civil Aviation)** statutory reporting.

---

## 2. Laspeyres Price Index Formulation

APIx employs a modified Laspeyres fixed-basket index formula:

$$I_t = \sum_{r=1}^{R} w_r \times \left( \frac{P_{r,t}}{P_{r,0}} \right) \times 100$$

Where:
- $I_t$: Composite National Airfare Price Index on day $t$.
- $R$: Number of monitored trunk routes ($R = 13$).
- $w_r$: Fixed expenditure / passenger traffic weight for route $r$, derived from official DGCA annual city-pair statistics:
  $$\sum_{r=1}^{R} w_r = 1.0$$
- $P_{r,t}$: Representative airfare on route $r$ on day $t$.
- $P_{r,0}$: Fixed base price on route $r$ during the baseline period ($t_0 = \text{2026-01-01}$, where $I_0 \equiv 100.00$).

### Advance Purchase Stratification
To eliminate bias from fluctuating booking horizons, APIx constructs five distinct sub-indices for each advance purchase window $k \in \{1, 7, 15, 30, 45\}$ days:

$$I_{t}^{(k)} = \sum_{r=1}^{R} w_r \times \left( \frac{P_{r,t}^{(k)}}{P_{r,0}^{(k)}} \right) \times 100$$

The Composite National APIx ($I_t^{\text{composite}}$) aggregates across windows using empirical consumer booking weights ($\alpha_k$):

$$I_t^{\text{composite}} = \sum_{k \in \{1, 7, 15, 30, 45\}} \alpha_k \cdot I_{t}^{(k)}$$

Default booking window weights based on DGCA and airline booking distributions:
- $\alpha_{1} = 0.15$ (Emergency / Last-minute travel, $T+1$)
- $\alpha_{7} = 0.25$ (Short-notice business travel, $T+7$)
- $\alpha_{15} = 0.30$ (Standard domestic travel, $T+15$)
- $\alpha_{30} = 0.20$ (Planned leisure / advance travel, $T+30$)
- $\alpha_{45} = 0.10$ (Early-bird vacation travel, $T+45$)

---

## 3. Representative Fare Estimation ($P_{r,t}^{(k)}$)

To insulate the index against extreme pricing quotes and low-frequency charter anomalies, the representative fare $P_{r,t}^{(k)}$ is computed as the **airline market-share weighted trimmed median**:

$$P_{r,t}^{(k)} = \sum_{a=1}^{A} s_a \cdot \text{Median}\left(\{ p_{r,a,f,t}^{(k)} \mid \text{non-outlier} \}\right)$$

Where $s_a$ is airline $a$'s domestic seat capacity share (e.g., IndiGo ~60%, Air India ~24%, SpiceJet ~5%, Akasa ~4%, AIX Connect ~5%, Alliance Air ~2%).

---

## 4. Lead-Time Price Elasticity & Surge Multiplier

A core analytical contribution of AIRFARE-X is the real-time quantification of dynamic pricing steepness.

### 4.1 Advance Purchase Price Elasticity ($\epsilon$)
Measures the percentage change in fare per percentage change in days prior to departure:

$$\epsilon = \frac{\partial \ln(P)}{\partial \ln(d)} \approx \frac{\ln(P_{T+1}) - \ln(P_{T+45})}{\ln(1) - \ln(45)}$$

Because price typically decreases as advance window $d$ increases, $\epsilon < 0$. A steeper negative elasticity reflects intense last-minute price gouging or peak demand periods (festivals, weather disruptions).

### 4.2 Surge Multiplier
The ratio of last-minute ($T+1$) ticket price to early-bird ($T+45$) base price:

$$\text{Surge Multiplier} = \frac{P_{T+1}}{P_{T+45}}$$

In normal market conditions, this multiplier hovers between $1.6\times$ and $2.2\times$. Multipliers exceeding $3.0\times$ trigger automated regulatory scrutiny alerts for potential dynamic pricing exploitation.

---

## 5. Non-Destructive Outlier Detection

Statistical outlier removal must adhere to official auditing standards. Identified outliers are flagged with specific tags and excluded from index calculation, but **never deleted** from the observation repository.

### 5.1 Interquartile Range (IQR) Rule
For route-window partition $\{p_i\}$:
$$\text{IQR} = Q_3 - Q_1$$
$$\text{Fences} = [Q_1 - 1.5 \times \text{IQR}, \; Q_3 + 1.5 \times \text{IQR}]$$

### 5.2 Median Absolute Deviation (MAD) Rule
Particularly robust against asymmetric distributions with heavy tails:
$$\text{MAD} = \text{median}\left( |p_i - \tilde{p}| \right)$$
$$Z_i = \frac{0.6745 \cdot |p_i - \tilde{p}|}{\text{MAD}}$$
$$\text{Outlier if } Z_i > 3.0$$

---

## 6. Data Quality Score (DQS) Formula

To provide MoSPI statisticians with a quantitative reliability index, each ingestion batch receives a composite quality score $DQS \in [0, 100]$:

$$DQS = 100 \times \left( 0.25 C + 0.20 V + 0.20 T + 0.20 U + 0.15 K \right)$$

1. **Completeness ($C$):**
   $$C = 1 - \frac{\sum \text{null mandatory fields}}{N \times \text{mandatory columns}}$$
2. **Validity ($V$):**
   $$V = \frac{1}{N} \sum_{i=1}^N \mathbf{1}\left(1000 \le \text{fare}_i \le 100000 \;\land\; \text{origin}_i \neq \text{dest}_i \;\land\; \text{IATA valid}\right)$$
3. **Timeliness ($T$):**
   $$T = \frac{1}{N} \sum_{i=1}^N \exp\left( -\frac{\Delta t_{\text{latency}}}{24\text{ hours}} \right)$$
4. **Uniqueness ($U$):**
   $$U = \frac{\text{Count of unique SHA-256 fingerprints}}{N}$$
5. **Consistency ($K$):**
   $$K = \frac{1}{N} \sum_{i=1}^N \mathbf{1}\left( |\text{total}_i - (\text{base}_i + \text{fuel}_i + \text{udf}_i + \text{gst}_i + \text{fee}_i)| < 1.00 \right)$$

---

## 7. DGCA Benchmark Backtesting Metrics

AIRFARE-X cross-validates the daily APIx index against monthly passenger yields published by the Directorate General of Civil Aviation (DGCA):

- **Mean Absolute Error (MAE):**
  $$\text{MAE} = \frac{1}{M} \sum_{m=1}^{M} |I_m^{\text{APIx}} - I_m^{\text{DGCA}}|$$
- **Root Mean Squared Error (RMSE):**
  $$\text{RMSE} = \sqrt{\frac{1}{M} \sum_{m=1}^{M} (I_m^{\text{APIx}} - I_m^{\text{DGCA}})^2}$$
- **Mean Absolute Percentage Error (MAPE):**
  $$\text{MAPE} = \frac{100\%}{M} \sum_{m=1}^{M} \left| \frac{I_m^{\text{APIx}} - I_m^{\text{DGCA}}}{I_m^{\text{DGCA}}} \right|$$
- **Pearson Correlation Coefficient ($r$):**
  $$r = \frac{\sum (I_m^{\text{APIx}} - \bar{I}^{\text{APIx}})(I_m^{\text{DGCA}} - \bar{I}^{\text{DGCA}})}{\sqrt{\sum (I_m^{\text{APIx}} - \bar{I}^{\text{APIx}})^2 \sum (I_m^{\text{DGCA}} - \bar{I}^{\text{DGCA}})^2}}$$
- **Directional Accuracy:**
  $$\text{DA} = \frac{1}{M-1} \sum_{m=2}^{M} \mathbf{1}\left( \text{sign}(\Delta I_m^{\text{APIx}}) = \text{sign}(\Delta I_m^{\text{DGCA}}) \right) \times 100\%$$
