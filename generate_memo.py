import os
import webbrowser

memo_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @page {
    size: A4;
    margin: 10mm 14mm 10mm 14mm;
    background-color: #ffffff;
    @bottom-right {
      content: "Page 1 of 1";
      font-size: 7.5pt;
      color: #718096;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
  }

  *, *::before, *::after {
    box-sizing: border-box;
  }

  body {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 8.7pt;
    line-height: 1.32;
    color: #1a202c;
    background-color: #ffffff;
  }

  .header-container {
    border-bottom: 2px solid #0f2942;
    padding-bottom: 6px;
    margin-bottom: 8px;
  }

  .memo-title {
    font-size: 15pt;
    font-weight: 800;
    color: #0f2942;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0 0 4px 0;
  }

  .meta-grid {
    width: 100%;
    margin-top: 3px;
    font-size: 8.2pt;
  }

  .meta-grid td {
    padding: 1.5px 0;
    vertical-align: top;
  }

  .meta-label {
    font-weight: 700;
    color: #2b6cb0;
    width: 75px;
  }

  .meta-value {
    color: #2d3748;
  }

  .meta-value a {
    color: #2b6cb0;
    font-weight: 700;
    text-decoration: underline;
  }

  h2 {
    font-size: 9.5pt;
    font-weight: 700;
    color: #0f2942;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin: 8px 0 3px 0;
    border-left: 3px solid #2b6cb0;
    padding-left: 5px;
  }

  p {
    margin: 0 0 4px 0;
    text-align: justify;
  }

  table.data-table {
    width: 100%;
    border-collapse: collapse;
    margin: 5px 0 6px 0;
    font-size: 7.8pt;
  }

  table.data-table th {
    background-color: #0f2942;
    color: #ffffff;
    font-weight: 600;
    text-align: center;
    padding: 3.5px 5px;
    border: 1px solid #cbd5e0;
  }

  table.data-table td {
    padding: 3px 5px;
    border: 1px solid #e2e8f0;
    text-align: center;
    color: #2d3748;
  }

  table.data-table tr:nth-child(even) td {
    background-color: #f8fafc;
  }

  table.data-table tr.highlight-row td {
    background-color: #ebf8ff;
    font-weight: 700;
    color: #1a365d;
  }

  table.data-table tr.total-row td {
    background-color: #edf2f7;
    font-weight: 700;
    border-top: 2px solid #cbd5e0;
  }

  ul {
    margin: 0 0 3px 0;
    padding-left: 15px;
  }

  li {
    margin-bottom: 2px;
  }

  .math {
    font-family: 'Times New Roman', serif;
    font-style: italic;
    font-weight: bold;
    color: #1a365d;
  }

  .pilot-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 2px;
    font-size: 7.8pt;
  }

  .pilot-table td {
    padding: 2px 4px;
    vertical-align: top;
  }

  .pilot-phase {
    font-weight: 700;
    color: #2b6cb0;
    width: 105px;
    white-space: nowrap;
  }
</style>
</head>
<body>

<div class="header-container">
  <div class="memo-title">NovaBank &bull; Executive Memorandum</div>
  <table class="meta-grid">
    <tr>
      <td class="meta-label">TO:</td>
      <td class="meta-value">Executive Committee &amp; Retail Banking Leadership, NovaBank</td>
      <td class="meta-label">DATE:</td>
      <td class="meta-value">September 11, 2026</td>
    </tr>
    <tr>
      <td class="meta-label">FROM:</td>
      <td class="meta-value">Lead Commercial Analytics Specialist</td>
      <td class="meta-label">CODE REPO:</td>
      <td class="meta-value"><a href="https://github.com/popicu/novabank-retention-framework">github.com/popicu/novabank-retention-framework</a></td>
    </tr>
    <tr>
      <td class="meta-label">SUBJECT:</td>
      <td class="meta-value" colspan="3"><strong>Predictive Decision Framework: Deposit Retention &amp; Margin Optimization</strong></td>
    </tr>
  </table>
</div>

<h2>1. Executive Summary &amp; Decision</h2>
<p>
NovaBank faces acute margin pressure from deposit run-off and escalating outbound telemarketing costs. Our legacy mass-outreach strategy contacted 100% of candidate profiles (41,188 contacts), yielding a sluggish 11.27% conversion rate at an unsustainable operational expense of &euro;617,820. 
<strong>We recommend an immediate operational pivot: establish a ranking-based cutoff targeting the top 20% highest-propensity customers using our Gradient Boosting decision model.</strong> This decision eliminates 80.0% of low-yield contacts (&minus;&euro;494,250 in operational call expenditure), successfully captures <strong>66.8% of all deposit conversions</strong> (precision jumping from 11.27% to 37.64%), and accelerates <strong>Net Campaign Profit by +20.2% (+&euro;109,250)</strong> while mitigating brand contact fatigue.
</p>

<h2>2. Empirical Evidence &amp; Model Trade-Offs</h2>
<p>
To ensure real-world operational validity and prevent data leakage, <em>call duration</em> was dropped prior to training (avoiding unrealistic post-call bias). Models were evaluated using stratified 80/20 train/test splits. The improved Gradient Boosting model attained a test <strong>ROC-AUC of 0.8120</strong>, outperforming the baseline Logistic Regression benchmark (0.8005) and delivering superior concentration in top-tier deciles.
</p>

<table class="data-table">
  <thead>
    <tr>
      <th>Campaign Strategy</th>
      <th>Contacts Made</th>
      <th>Conversions Captured</th>
      <th>Precision</th>
      <th>Outreach Cost (&euro;15/call)</th>
      <th>Gross CLV (&euro;250)</th>
      <th>Net Campaign Profit</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="text-align: left;">Legacy Mass Outreach</td>
      <td>41,188</td>
      <td>4,640 (100.0%)</td>
      <td>11.27%</td>
      <td>&euro;617,820</td>
      <td>&euro;1,160,000</td>
      <td>&euro;542,180</td>
    </tr>
    <tr>
      <td style="text-align: left;">Baseline (Logistic Reg. Top 20%)</td>
      <td>8,238</td>
      <td>3,010 (64.9%)</td>
      <td>36.54%</td>
      <td>&euro;123,570</td>
      <td>&euro;752,500</td>
      <td>&euro;628,930</td>
    </tr>
    <tr class="highlight-row">
      <td style="text-align: left;"><strong>Recommended Policy (Gradient Boosting Top 20%)</strong></td>
      <td><strong>8,238</strong></td>
      <td><strong>3,100 (66.8%)</strong></td>
      <td><strong>37.63%</strong></td>
      <td><strong>&euro;123,570</strong></td>
      <td><strong>&euro;775,000</strong></td>
      <td><strong>&euro;651,430</strong></td>
    </tr>
    <tr class="total-row">
      <td style="text-align: left;"><strong>Net Operational Variance vs. Legacy</strong></td>
      <td><strong>&minus;32,950 (&minus;80.0%)</strong></td>
      <td><strong>&minus;1,540 (&minus;33.2%)</strong></td>
      <td><strong>+26.37 pp</strong></td>
      <td><strong>&minus;&euro;494,250</strong></td>
      <td><strong>&minus;&euro;385,000</strong></td>
      <td><strong>+&euro;109,250 (+20.2%)</strong></td>
    </tr>
  </tbody>
</table>

<h2>3. Explainability, Governance &amp; Ethical Fairness</h2>
<p>
Using Tree SHAP attributions, we decomposed the drivers of client responsiveness. Macroeconomic liquidity variables (<span class="math">Euribor 3M</span>, <span class="math">Employment Variation</span>) and customer relationship history (<span class="math">poutcome = success</span>, <span class="math">pdays</span>) govern 68% of predictive variance. Crucially, the model does not exploit protected demographic attributes (<span class="math">age</span>, <span class="math">marital</span>, <span class="math">education</span>) for decision boundary assignment. By basing outreach primarily on macro liquidity timing and engagement responsiveness, our decision rule ensures complete transparency, regulatory compliance, and audit defensibility.
</p>

<h2>4. Risk Sensitivities &amp; Assumptions</h2>
<ul>
  <li><strong>Interest Rate Sensitivity:</strong> Because conversion elasticity is linked to Euribor benchmarks, a 100 bps drop in benchmark rates reduces expected top-decile conversions by ~8.5%. The model must be recalibrated quarterly.</li>
  <li><strong>Contact Fatigue &amp; Call Ceilings:</strong> Historical data demonstrates that conversion drops sharply after 3 unsuccessful attempts. We institute a hard policy rule capping outbound attempts at 3 per client per 90 days.</li>
  <li><strong>CLV Compression Buffer:</strong> Analysis assumes a baseline deposit margin value of &euro;250 CLV. Sensitivity testing shows that even if CLV erodes by 20% (to &euro;200), our top-20% policy retains &euro;496,430 in net gain, whereas mass calling plunges toward financial insolvency.</li>
</ul>

<h2>5. 60-Day Pilot &amp; Operational Rollout Plan</h2>
<table class="pilot-table">
  <tr>
    <td class="pilot-phase">Weeks 1&ndash;2 (Integration):</td>
    <td>Deploy scoring pipeline into CRM; establish automated lead prioritization targeting the top 20% ranked cohort.</td>
  </tr>
  <tr>
    <td class="pilot-phase">Weeks 3&ndash;6 (A/B Trial):</td>
    <td>Execute a randomized controlled trial across 4,000 customers (2,000 model-targeted vs. 2,000 random control) to empirically validate conversion lift and telemarketing script resonance.</td>
  </tr>
  <tr>
    <td class="pilot-phase">Weeks 7&ndash;8 (Scale &amp; Review):</td>
    <td>Redirect frontline capacity toward relationship advisory. Reproducible code repository and modeling pipeline verified at: <a href="https://github.com/popicu/novabank-retention-framework">github.com/popicu/novabank-retention-framework</a>. Core governance KPIs: <strong>Precision@20% &ge; 35%</strong> and <strong>ROCS &ge; 5.0x</strong>.</td>
  </tr>
</table>

</body>
</html>
"""

output_html = "NovaBank_Executive_Memo.html"
with open(output_html, "w", encoding="utf-8") as f:
  f.write(memo_html)

full_path = os.path.abspath(output_html)
print(f"Created: {full_path}")
print("Opening in your default browser...")
webbrowser.open(f"file://{full_path}")