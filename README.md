<h1>BearCart: E-Commerce Growth & Conversion Intelligence</h1>

<h2>Project Overview</h2>
<p>
  BearCart is a data-driven analytics and dashboarding project designed to help an e-commerce business
  understand customer behavior, marketing effectiveness, conversion performance, revenue trends,
  and refund impact.
</p>
<p>
  This project was developed as part of a <strong>hackathon case study</strong>, where we act as a
  <strong>data analytics consulting team</strong> supporting BearCart’s leadership with actionable,
  insight-backed decisions.
</p>

<hr />

<h2>Problem Statement</h2>
<p>BearCart collects large volumes of website and transaction data but lacks clear visibility into:</p>
<ul>
  <li>How users interact with the website</li>
  <li>Which marketing channels drive meaningful conversions</li>
  <li>What factors influence revenue and order value</li>
  <li>How refunds impact overall business performance</li>
</ul>
<p>
  Our goal is to <strong>transform raw, noisy data into a clean, interactive intelligence dashboard</strong>
  that supports strategic decision-making.
</p>

<hr />

<h2>Our Approach</h2>
<p>
  We followed a <strong>structured, business-first analytics approach</strong>, combining data engineering,
  analysis, and full-stack dashboard development.
</p>

<h3>1. Data Understanding & Modeling</h3>
<ul>
  <li>Studied all provided datasets (sessions, orders, products, refunds, marketing sources)</li>
  <li>Identified relationships between sessions → orders → refunds</li>
  <li>Defined key business metrics such as conversion rate, AOV, revenue per session, and refund rate</li>
</ul>

<h3>2. Data Cleaning & Preprocessing</h3>
<ul>
  <li>Removed duplicate and inconsistent records</li>
  <li>Handled missing values and incorrect data types</li>
  <li>Validated logical constraints (e.g., refunds not exceeding order value)</li>
</ul>

<h3>3. Exploratory & Business Analysis</h3>
<ul>
  <li>Website traffic and user behavior analysis</li>
  <li>Session-to-order conversion funnel evaluation</li>
  <li>Marketing channel performance comparison</li>
  <li>Revenue growth and Average Order Value (AOV) analysis</li>
  <li>Refund rate and category-level impact assessment</li>
</ul>

<h3>4. Insight Generation</h3>
<ul>
  <li>Identification of high-traffic but low-conversion channels</li>
  <li>High-ROI marketing sources</li>
  <li>Refund-heavy product categories</li>
  <li>Device-based conversion gaps</li>
</ul>

<h3>5. Dashboard-Driven Storytelling</h3>

<h4>Backend</h4>
<ul>
  <li>Python (Pandas, NumPy) for data processing</li>
  <li>Modular scripts for KPI computation and analysis</li>
</ul>

<h4>Frontend</h4>
<ul>
  <li>Interactive dashboard built using Streamlit</li>
  <li>KPI cards, dynamic charts, and filters</li>
  <li>Executive-friendly layout for decision-making</li>
</ul>

<hr />

<h2>Dashboard Features</h2>
<ul>
  <li>Executive KPI overview</li>
  <li>Traffic & marketing channel analysis</li>
  <li>Conversion funnel visualization</li>
  <li>Revenue & AOV trends</li>
  <li>Refund impact analysis</li>
</ul>

<hr />

<h2>Project Architecture</h2>
<pre>
BearCart/
│
├── data/
│   ├── raw/
│   └── cleaned/
│
├── backend/
│   ├── data_cleaning.py
│   ├── analysis.py
│   └── kpis.py
│
├── frontend/
│   └── app.py   (Streamlit Dashboard)
│
├── requirements.txt
└── README.html
</pre>

<hr />

<h2>Business Impact</h2>
<ul>
  <li>Improved visibility into customer behavior</li>
  <li>Better marketing spend optimization</li>
  <li>Identification of revenue-driving channels</li>
  <li>Reduced refund impact through data insights</li>
</ul>

<hr />

<h2>Tools & Technologies</h2>
<ul>
  <li>Python</li>
  <li>Pandas, NumPy</li>
  <li>Streamlit</li>
  <li>Plotly</li>
  <li>SQLite / CSV</li>
</ul>

<hr />

<h2>Future Enhancements</h2>
<ul>
  <li>Machine learning–based conversion prediction</li>
  <li>Customer segmentation</li>
  <li>Real-time data ingestion</li>
  <li>Cloud deployment</li>
</ul>

<hr />

