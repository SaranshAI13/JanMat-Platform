# Product Requirement Document (PRD)
## Project Name: **JanMat — Citizen Sentiment & Campaign Telemetry Platform**
**Author:** Staff Technical Product Manager, Campaign Analytics & Technology Group  
**Organization:** Nation with NaMo (Flagship Strategic Technology Division)  
**Document Status:** Approved & Baseline V1.0 (Production Blueprint)  
**Target Release:** General Availability (GA) — 2024–2029 Electoral Operational Cycles  
**Target Audience:** Central Campaign Strategists, War-Room Directors, State Campaign In-Charges, District Observers, Booth Adhyakshas & Karyakartas  

---

## 1. Executive Summary & Problem Statement

### 1.1 Executive Summary
Elections in India represent the world’s largest democratic exercise, encompassing over 960 million registered voters, 1 million+ polling stations, and 543 parliamentary constituencies. Traditional political consulting models face a chronic operational bottleneck: **the ground-to-command information gap**. 

While central leadership develops national narratives and welfare scheme manifestos (e.g., PM-KISAN, Ayushman Bharat, PMAY, Jal Jeevan Mission), frontline political realities shift hourly at the booth level. Ground volunteers (*karyakartas* and *panna pramukhs*) observe hyper-local public friction—such as delays in seed subsidies, localized water shortages, or regional anti-incumbency—weeks before it surfaces in monthly sample surveys.

**JanMat** is an enterprise-grade citizen sentiment ingestion and campaign telemetry platform. It bridges the critical divide between **50,000+ grassroots field volunteers** across 50 pivotal constituencies and the **Central War Room Data Intelligence Group**. By combining lightweight, offline-first mobile telemetry with natural language sentiment parsing and macro-spatial intelligence, JanMat slashes operational reporting lag from 48 hours to under 28 hours (a 40% reduction), speeds critical bottleneck resolution to under 24 hours, and aligns high-level electioneering with ground truth.

```
       [ Grassroots Karyakartas & Citizens ]
                        │
                        ▼ (Offline-First / Vernacular Telemetry)
         [ JanMat Mobile Telemetry Engine ]
                        │
        (Async SQLite Sync / REST Ingestion)
                        │
                        ▼
      [ JanMat Real-Time NLP & Processing Core ]
           ├── Sentiment Engine (VADER + TF-IDF)
           ├── Issue Categorization & SLA Engine
           └── Geographic & Demographic Aggregator
                        │
                        ▼
     [ Central Campaign Command War Room (App) ]
           ├── High-Level Strategic Heatmaps & Trends
           ├── Demographic Cohort & Scheme Sentiment
           ├── Rapid Escalation & Bottleneck Resolution
           └── Telemetry Adoption & Latency Analytics
```

---

### 1.2 Core Problem Statement

1. **Information Asymmetry & Asynchronous Telemetry**: 
   Historically, ground feedback collected by booth workers traveled through a hierarchical, multi-tiered paper or WhatsApp chain (Booth -> Mandal -> District -> State -> Central). This created an average **48–72 hour lag**. By the time central strategists detected localized dissatisfaction with a welfare policy implementation, public resentment had already crystallized.

2. **Unstructured & Anecdotal Feedback**:
   Field reports often arrive as fragmented qualitative observations ("Farmers in Vidarbha are unhappy with procurement prices"). Without structured cohort tagging (Youth vs. Farmers vs. Women), scheme attribution (PM-KISAN vs. MSP), or quantified sentiment telemetry, leadership cannot separate vocal minority noise from broad electoral sentiment.

3. **Lack of Closed-Loop Issue Resolution SLA**:
   Field workers routinely complain that once local issues are escalated to district or state cells, they enter a "black hole." Lacking ticket tracking and service-level agreements (SLAs), volunteer morale drops, leading to an attrition rate of over 35% among active booth workers before election week.

4. **Digital Divide & Network Instability**:
   Over 40% of India's polling booths are situated in Tier-3/rural belts with spotty 2G/3G data connectivity or periodic outages. Systems that require persistent high-bandwidth cloud sync fail in the field.

---

## 2. Target User Personas

### Persona 1: Ramesh Kumar — Ground-Level Field Volunteer & Booth Coordinator
* **Age:** 28  
* **Location:** Booth 142, Phulpur Assembly Constituency, Prayagraj District, Uttar Pradesh  
* **Role:** Booth Adhyaksha / Field Volunteer (Nation with NaMo Grassroots Cadre)  
* **Device Profile:** Budget Android smartphone (2GB RAM, intermittent 4G/2G connection, regional Hindi language preference).  
* **Jobs To Be Done (JTBD):**
  1. Record citizen sentiment and grievance reports directly during door-to-door *sampark abhiyan* without being bogged down by complex dropdowns.
  2. Log actionable infrastructure and welfare delivery complaints with clear attribution (e.g., "PMAY installment delayed for 4 months").
  3. Track whether issues he submitted were acknowledged and resolved by the Mandal or District campaign team, so he can report progress back to voters during follow-up visits.
* **Pain Points:**
  - High-bandwidth web apps fail in rural fields with no cellular reception.
  - Complex English-only interfaces create cognitive overload and input fatigue.
  - Frustration when feedback goes into a void with no visibility on action taken.
* **Success Criteria for Ramesh:**
  - Can log a citizen report in under 45 seconds using 3 clicks and voice/text input.
  - Offline mode preserves submissions and syncs automatically when network resumes.
  - Receives live ticket ID and status updates for local escalation.

---

### Persona 2: Dr. Ananya Sharma — Central Campaign Data Strategist & War-Room Director
* **Age:** 39  
* **Location:** Central War Room, Nation with NaMo Headquarters, New Delhi  
* **Role:** Lead Campaign Data Scientist & Political Strategist  
* **Device Profile:** High-performance laptop (MacBook Pro / Dual 4K monitors, high-speed fiber).  
* **Jobs To Be Done (JTBD):**
  1. Monitor macro-level voter sentiment trajectories across 50 battleground constituencies in 5 key states.
  2. Dissect voter sentiment across demographic cohorts (Youth, Women, Farmers, Senior Citizens) to tailor targeted advertising and speeches for leadership.
  3. Identify sudden negative sentiment anomalies around flagship schemes (e.g., Ayushman Bharat coverage gaps or PM-KISAN installment issues) in specific clusters.
  4. Measure operational efficiency: track reporting latency across districts, monitor karyakarta app adoption, and enforce <24h SLAs on high-priority escalations.
* **Pain Points:**
  - Drowning in disconnected spreadsheets, WhatsApp forwarded messages, and delayed monthly polls.
  - Difficulty discerning whether negative feedback is isolated or indicative of a swing trend.
  - Lack of quantifiable metrics to measure whether ground machinery is actively reporting.
* **Success Criteria for Dr. Ananya:**
  - Single-pane-of-glass executive dashboard displaying real-time Net Sentiment Score (NSS), volume, and geographic anomalies.
  - Instant drilldown from National/State level down to individual Assembly Constituency and Polling Booth.
  - Verified reduction of operational reporting latency from 48h to under 28h.

---

## 3. Product Vision, Architecture & Technical Scope

### 3.1 Product Vision
To be the definitive, mission-critical political operating system that empowers grassroots party workers with instant escalation capabilities, while providing central campaign leadership with real-time, cohort-specific, and policy-attributed strategic clarity.

### 3.2 High-Level Architecture
The JanMat platform is structured across three decoupled layers:

1. **Telemetry & Capture Layer (Client Tier)**:
   - Optimized for responsive desktop & mobile viewport.
   - Dual-persona interface: Strategist Command Deck & Field Coordinator Console.
   - Built with Streamlit, custom responsive CSS design tokens, and local cache handlers.

2. **Intelligence & Processing Layer (Engine Tier)**:
   - Natural Language Sentiment Pipeline: Hybrid lexical and TF-IDF extraction calculating normalized Net Sentiment Scores (-1.00 to +1.00).
   - Automated Issue Categorization Engine: Rules and keyword clustering mapping text into Infrastructure, Healthcare, Agriculture, Employment, and Civic Amenities.
   - Escalation SLA Tracker: Timed lifecycle monitor (Reported -> In Progress -> Resolved).

3. **Data & Persistence Layer (Storage Tier)**:
   - SQLAlchemy ORM with multi-table relational schema:
     * `constituencies`: Master spatial catalog (State, Region, Electorate, Priority Tier).
     * `booths`: Micro-polling station registry with coordinator metadata.
     * `feedback_telemetry`: Granular feedback log with cohort tags, sentiment scores, and timestamps.
     * `issues_log`: Actionable grievance records with priority ratings, assignee IDs, and resolution timestamps.
   - Production SQLite engine with zero-latency in-memory query capabilities, scalable to PostgreSQL for high-concurrency central deployment.

---

## 4. Feature Prioritization Matrix (RICE Framework)

To maximize campaign ROI within fixed election cycle deadlines, feature proposals were evaluated using the standard RICE framework:
$$\text{RICE Score} = \frac{\text{Reach} \times \text{Impact} \times \text{Confidence}}{\text{Effort}}$$
* **Reach (R):** Number of users or records impacted per month (Scale 1–10).
* **Impact (I):** Impact on campaign outcome and reporting efficiency (0.25 = Minimal, 0.5 = Low, 1.0 = Medium, 2.0 = High, 3.0 = Massive).
* **Confidence (C):** Product certainty in requirement and execution (50% = Low, 80% = Medium, 100% = High).
* **Effort (E):** Person-months required to design, build, and deploy (Scale 1–5).

| Priority | Feature Description | Category | Reach (1-10) | Impact (0.25-3) | Confidence (0-100%) | Effort (1-5) | RICE Score | Decision / Roadmap |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **P0 (Rank 1)** | **Real-Time Critical Issue Escalation & SLA Engine** | Operations | 10 | 3.0 (Massive) | 100% | 2.0 | **15.00** | **MVP Release (Immediate Build)** |
| **P0 (Rank 2)** | **Demographic Cohort & Scheme Sentiment Analytics** | Intelligence | 9 | 3.0 (Massive) | 90% | 2.5 | **9.72** | **MVP Release (Immediate Build)** |
| **P0 (Rank 3)** | **Offline-First Low-Bandwidth Telemetry Ingestion** | Field Platform | 10 | 2.0 (High) | 90% | 2.0 | **9.00** | **MVP Release (Immediate Build)** |
| **P1 (Rank 4)** | **Interactive Macro Constituency Heatmap (Choropleth/Bubble)** | War Room UI | 8 | 2.0 (High) | 95% | 2.0 | **7.60** | **MVP Release (Immediate Build)** |
| **P1 (Rank 5)** | **Operational Telemetry & Reporting Lag Tracker** | Management | 7 | 2.0 (High) | 90% | 2.0 | **6.30** | **MVP Release (Immediate Build)** |
| **P2 (Rank 6)** | **Automated WhatsApp Bot Ingestion Integration** | Communication | 8 | 1.0 (Medium) | 70% | 3.0 | **1.87** | **Phase 2 (Post-MVP)** |
| **P3 (Rank 7)** | **Predictive Voter Turnout Forecasting Model** | Data Science | 5 | 1.0 (Medium) | 50% | 4.0 | **0.63** | **Deprioritized (Historical poll data too noisy)** |

### Strategic Rationale for Prioritization:
The RICE analysis strongly demonstrated that **Real-Time Issue Escalation (Score: 15.00)** and **Welfare Scheme Sentiment Attribution (Score: 9.72)** yield vastly superior tactical campaign value compared to **Predictive Voter Turnout (Score: 0.63)**. Turnout forecasting during early campaign phases carries high uncertainty and low operational leverage, whereas fixing local grievance bottlenecks directly wins swing booths.

---

## 5. Core Product Telemetry & Success Metrics

The performance and ROI of JanMat is measured against four foundational North Star metrics:

### 5.1 Operational Reporting Lag
* **Baseline (Pre-JanMat):** 48.0 Hours (Feedback gathered on Day 1 reached Central Dashboard late on Day 3).
* **Target:** $\le$ 28.0 Hours (Minimum 40% reduction in operational reporting turnaround).
* **Telemetry Metric:** Time elapsed between `observation_timestamp` and `central_ingestion_timestamp`.

### 5.2 Grassroots Feature Adoption Rate
* **Baseline:** ~40% adherence to digital logging among volunteers.
* **Target:** $> 85\%$ weekly active booth coordinators logging at least 5 citizen interactions per week.
* **Telemetry Metric:** $\text{Adoption Rate} = \frac{\text{Active Logging Booth Coordinators}}{\text{Total Registered Booth Coordinators}} \times 100$.

### 5.3 Critical Issue Resolution SLA
* **Baseline:** 72–120 Hours for district intervention.
* **Target:** $< 24.0$ Hours for P0/Critical flagged bottlenecks (e.g., voting list omission reports, communal tensions, acute water breakdown).
* **Telemetry Metric:** Duration between `issue_reported_timestamp` and `issue_status = 'Resolved'`.

### 5.4 Net Sentiment Index (NSI) Shift
* **Formula:** $\text{NSI} = \frac{\text{Positive Feedback Count} - \text{Negative Feedback Count}}{\text{Total Feedback Count}} \times 100$
* **Target:** Measure correlation between rapid booth issue resolution and positive NSI trajectory over 14-day rolling windows.

---

## 6. Functional Specifications & System Requirements

### 6.1 Central Campaign Strategist View
1. **Executive KPI Ribbon**:
   - Total Ingested Citizen Feedback Count (with week-over-week % growth).
   - Macro Average Net Sentiment Score (color-coded badge: Bullish/Neutral/Vulnerable).
   - Active Critical Issues Requiring Immediate Intervention.
   - Mean Operational Reporting Lag (Target vs. Actual).
2. **Constituency Spatial Intelligence Matrix**:
   - Multi-state filter (Uttar Pradesh, Maharashtra, Rajasthan, Madhya Pradesh, Karnataka).
   - Scatter/Bubble & Choropleth visualization mapping Constituency vs. Sentiment Score, with bubble size proportional to Citizen Feedback Volume.
   - Instant drilldown displaying Booth-level variance and priority risk rating.
3. **Welfare Scheme Attribution & Demographic Cross-Tabulation**:
   - Policy-level sentiment breakdown across key flagship initiatives:
     * PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)
     * Ayushman Bharat (Health Protection Scheme)
     * PMAY (Pradhan Mantri Awas Yojana)
     * Jal Jeevan Mission (Clean Tap Water Infrastructure)
     * PM Ujjwala Yojana (LPG Access)
   - Demographic cohort segmentations: **Farmers, Youth, Women, Senior Citizens**.
   - Stacked horizontal and heat visualizers displaying satisfaction vs. friction points.
4. **NLP Keyword Cloud & Issue Clustering**:
   - Real-time TF-IDF frequency extraction isolating leading citizen complaints (e.g., "Electricity Tariff", "Fertilizer Shortage", "Paper Leak", "Road Potholes").

### 6.2 Grassroots Field Coordinator View
1. **Quick-Entry Telemetry Ingestion Form**:
   - Constituency & Booth ID auto-population based on coordinator login context.
   - Demographic cohort selector (One-touch buttons).
   - Welfare scheme tagging dropdown.
   - Vernacular / Hinglish natural language feedback field (with voice-to-text readiness).
   - Instant sentiment scoring preview (-1.00 to +1.00) powered by local sentiment inference.
2. **Real-Time Issue Escalation Desk**:
   - Priority classification: Critical (P0), High (P1), Medium (P2), Low (P3).
   - Categorization: Infrastructure, Agriculture, Healthcare, Employment, Civic.
   - Submission trigger generating unique tracking Ticket ID.
3. **Local Action Funnel & Status Monitor**:
   - Visual Kanban/Funnel tracking submitted grievances across:
     $$\text{Reported} \longrightarrow \text{In Progress} \longrightarrow \text{Resolved}$$
   - Direct time elapsed counter monitoring compliance with the 24-hour resolution SLA.

### 6.3 Telemetry & Operational Analytics View
1. **Reporting Lag Reduction Comparative Trend**:
   - Time-series tracking historic 48h benchmark vs. JanMat 28h progressive telemetry performance across all 50 constituencies.
2. **Volunteer Adoption Funnel**:
   - Step-by-step conversion funnel: App Installs $\to$ Profile Verification $\to$ First Form Logged $\to$ Daily Active Telemetry Logging ($>85\%$ target).
3. **SLA Compliance & District Performance Scorecards**:
   - Top-performing and laggard district rankings based on resolution speed.

---

## 7. User Acceptance Testing (UAT) & Edge-Case Handling

### 7.1 Offline Connectivity & Asynchronous Data Synchronization
* **Scenario:** Field volunteer operates in a zero-reception rural pocket of Bundelkhand (UP) for 6 hours.
* **Expected Behavior:** 
  - Application caches submissions locally in IndexedDB / SQLite client-side storage with an explicit "Cached Offline" visual pill.
  - Form validation occurs entirely on-device without triggering network timeouts.
  - Upon network restoration, an automatic background handshake batches and flushes queued records to the central database, assigning server timestamp and calculating net lag without loss of original capture time.

### 7.2 Mixed-Language / Hinglish Lexical Parsing
* **Scenario:** Citizen feedback contains mixed colloquial vocabulary: *"Ration card banne me pradhan ji paise maang rahe hain, par road acchi bani hai."*
* **Expected Behavior:** 
  - The NLP tokenizer splits multi-clause statements and correctly identifies conflicting sentiments (Negative on corruption / Civic grievance; Positive on road infrastructure).
  - Sentiment scoring accurately reflects contextual polarity rather than default neutral classification.

### 7.3 High-Volume Ingestion Spikes
* **Scenario:** Immediate post-rally speech by national leadership generates 5,000 feedback submissions within a 15-minute window in a single constituency.
* **Expected Behavior:** 
  - Central ingestion pipeline employs lightweight connection pooling and asynchronous transaction commits.
  - Zero dropped packets, sub-second dashboard refresh rates, and automated outlier smoothing.

### 7.4 Data Integrity & Bot/Spam Guardrails
* **Scenario:** Malicious actor or rogue coordinator submits repetitive synthetic entries to skew constituency sentiment.
* **Expected Behavior:** 
  - Deduplication filter flags duplicate submission hashes originating from the same Booth ID within a 120-second threshold.
  - Anomaly detection alerts war room analysts of statistical spikes deviating $>3\sigma$ from rolling booth averages.

---

## 8. Compliance, Security & Ethical Data Governance

1. **Voter Privacy & PII Protection**: 
   - Strict adherence to Digital Personal Data Protection Act (DPDPA). No citizen Aadhaar numbers, phone numbers, or residential addresses are stored in raw telemetry logs. 
   - Feedback is anonymized into demographic cohorts and spatial coordinates.
2. **Role-Based Access Control (RBAC)**:
   - Field Coordinators can only inspect and log feedback for their assigned Mandal/Booth.
   - Central Strategists possess multi-state macro visibility with export auditing.
3. **Data Residency**:
   - All server clusters and database volumes hosted strictly within Indian sovereign cloud regions (MeitY empaneled data centers).

---
*End of PRD — Approved for Technical Implementation by Nation with NaMo Central Analytics Council.*
