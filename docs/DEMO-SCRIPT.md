# Demo Script - "Beyond the Dashboard"

> **Parent**: [PROJECT-MASTER.md](../PROJECT-MASTER.md)  
> **Status**: ⏳ Pending  
> **Duration**: 15 minutes

---

## Overview

This is the presentation script for demonstrating the STIHL Analytics Agent to stakeholders. The demo showcases how AI-powered analytics goes beyond traditional Power BI dashboards.

---

## Demo Structure

| Act | Duration | Content | Key Message |
|-----|----------|---------|-------------|
| **Opening** | 1 min | Set the stage | "AI works FOR you, not the other way around" |
| **Act 1** ⭐ | 2 min | Proactive Greeting | "It told me without asking" |
| **Act 2** | 4 min | Natural Language | "No SQL, no dashboard hunting" |
| **Act 3** | 3 min | Forecasting | "Predictive, not just historical" |
| **Act 4** | 3 min | Recommendations | "Decisions, not just metrics" |
| **Closing** | 2 min | Business Case | "Pilot in 8 weeks" |

---

## Opening (1 minute)

### Slide: Title

**Script:**
> "Today I want to show you something that will change how your team interacts with data. 
> 
> Currently, when your analysts need insights, they have to HUNT for them - clicking through dashboards, writing queries, exporting to Excel. The data doesn't come to them; they have to go to it.
> 
> What if that was reversed? What if your data proactively told you what you need to know?"

### Transition:
> "Let me show you what that looks like..."

---

## Act 1: Proactive Greeting ⭐ (2 minutes)

**This is the HERO MOMENT - the "wow" that differentiates from Power BI**

### Demo Action:
Open new conversation with the agent

### What Happens:
Agent immediately displays proactive insights WITHOUT being asked:

```
Agent: "Good morning! Before we dive in, I've been monitoring your data 
and found 3 things worth your attention:

🚨 ANOMALY: Texas chainsaw sales spiked 340% last week. This correlates 
   with Hurricane [name] landfall. 12 dealers affected, potential restock needed.

📦 ALERT: MS-271 Farm Boss is at 12 days supply in Southwest - below 
   your 30-day safety threshold. Recommend reorder of 200 units.

📈 TREND: Battery products are up 35% vs last quarter. FSA-57 is leading 
   with strongest growth in the Northeast.

What would you like to explore today?"
```

### Script:
> "Notice what just happened. I didn't ask anything yet. The agent analyzed overnight batch data and surfaced the THREE most important things I should know about.
> 
> That hurricane correlation? That would have taken your analyst 4 hours to discover by cross-referencing weather data with sales. The agent did it automatically.
> 
> **This is the difference between reactive dashboards and proactive AI.**"

### Key Point to Emphasize:
> "How long would it take to find that hurricane correlation in Power BI? The answer is: you probably never would, because nobody thinks to look for it."

---

## Act 2: Natural Language Queries (4 minutes)

### Demo Sequence:

#### Query 1: Simple Question
**Type:** "How did chainsaws perform last quarter?"

**Expected Response:**
```
Agent: "Chainsaw sales in Q4 2025:
- Total revenue: $4.2M (+12% vs Q4 2024)
- Units sold: 8,450 
- Top performer: MS-271 Farm Boss (32% of category)
- Regional leader: Southwest ($1.1M)

[Bar chart showing monthly breakdown]

The November spike of 340% in Texas accounts for most of the YoY growth. 
Want me to exclude that anomaly to see underlying trends?"
```

**Script:**
> "Notice I asked in plain English. No SQL, no filters, no dashboard navigation. And the agent didn't just answer - it added context about that Texas anomaly we saw earlier."

#### Query 2: Follow-up Drill Down
**Type:** "Yes, show me without the hurricane impact"

**Expected Response:**
```
Agent: "Excluding Texas November anomaly:
- Adjusted revenue: $3.5M (+3% vs Q4 2024)  
- This suggests organic growth of 3% vs the reported 12%

[Updated chart with Texas anomaly highlighted separately]

The underlying business is healthy, but growth is more modest than 
the headline numbers suggest. Should I factor this into Q1 forecasts?"
```

**Script:**
> "This is conversational analytics. I'm having a dialogue, not clicking through reports. And the agent is thinking ahead - it's already considering implications for forecasting."

#### Query 3: Cross-Domain Question
**Type:** "What products should we be worried about for inventory?"

**Expected Response:**
```
Agent: "Current stockout risks (prioritized by impact):

🔴 CRITICAL (< 7 days supply):
   - MS-271 Farm Boss (Southwest): 5 days, $450K weekly revenue at risk
   - FS-91 Trimmer (Southeast): 6 days, $180K weekly revenue at risk

🟡 HIGH (7-14 days supply):
   - BG-86 Blower (Midwest): 11 days
   - MS-362 (West): 13 days

[Table with details]

Recommend immediate reorder for MS-271 and FS-91. Want me to 
calculate optimal reorder quantities?"
```

**Script:**
> "I switched from sales to inventory seamlessly. The agent understands context and maintains conversation flow. This is how humans actually think about business questions."

---

## Act 3: Forecasting (3 minutes)

### Demo Sequence:

#### Query 4: Forecast Request
**Type:** "What should we expect for chainsaw sales in Q1?"

**Expected Response:**
```
Agent: "Q1 2026 Chainsaw Forecast:

📊 Category Level:
- Predicted units: 6,200 (±8% confidence interval)
- Predicted revenue: $2.8M
- YoY change: +7% vs Q1 2025

📈 Key Drivers:
- Seasonal spring demand typically starts in March
- Battery chainsaw adoption continuing (+15% category share)
- MSA-220 launch expected to contribute $200K

[Forecast chart with confidence bands]

⚠️ Risk Factor: If Southwest inventory issues aren't resolved, 
we could see 10-15% revenue impact in that region.

Want me to run a scenario excluding Southwest?"
```

**Script:**
> "This isn't just showing historical data - it's making predictions. And notice it connected the forecast to the inventory alert we saw earlier. The agent thinks holistically."

#### Query 5: What-If Scenario
**Type:** "What if we increase marketing spend 20% in March?"

**Expected Response:**
```
Agent: "Scenario Analysis: +20% March Marketing

Based on historical marketing elasticity:
- Expected additional units: 400-600
- Expected additional revenue: $180K-$270K
- ROI estimate: 2.1x - 3.2x (based on $85K spend increase)

[Comparison chart: baseline vs marketing scenario]

Recommendation: Focus marketing on MS-271 and battery products 
where we have strongest historical response rates.

Note: This assumes inventory constraints are resolved. Current 
Southwest shortage would limit upside by approximately 15%.
```

**Script:**
> "Now we're doing predictive planning. Instead of 'what happened,' we're exploring 'what could happen.' This is the transition from analytics to decision support."

---

## Act 4: Recommendations (3 minutes)

### Demo Sequence:

#### Query 6: Action Recommendation
**Type:** "What should I do about the Southwest inventory situation?"

**Expected Response:**
```
Agent: "Recommended Actions for Southwest Inventory:

📦 IMMEDIATE (This Week):
1. Emergency transfer: 150 MS-271 units from Northeast (10-day oversupply there)
   - Transit time: 3-4 days
   - Cost: ~$2,400 shipping
   - Revenue protected: ~$320K

2. Expedite PO #4521: Request air freight for remaining 100 units
   - Additional cost: ~$3,500
   - Arrival: 5 days faster

💰 Cost/Benefit:
- Total emergency action cost: ~$6,000
- Revenue at risk without action: ~$450K/week
- ROI: 75x

📋 PREVENTIVE (Next 30 Days):
- Increase Southwest safety stock from 30 to 45 days for top 5 SKUs
- Add supplier in Mexico for faster Southwest replenishment

Want me to draft the transfer request or calculate the updated 
safety stock levels?"
```

**Script:**
> "This is the ultimate value. Not just 'here's your data,' but 'here's what you should do and why.' The agent calculated ROI, suggested specific actions, and offered to help execute."

---

## Closing (2 minutes)

### Slide: Value Summary

**Script:**
> "Let's recap what you just saw:
> 
> 1. **Proactive insights** - The agent told us about the hurricane correlation without being asked
> 2. **Natural conversation** - Plain English queries, no training required  
> 3. **Predictive analytics** - Forecasts and scenarios, not just history
> 4. **Actionable recommendations** - Specific actions with ROI calculations
> 
> This isn't replacing your analysts. It's giving them superpowers. They can focus on strategic decisions while the agent handles the data hunting."

### Slide: Technical Architecture

**Script:**
> "From a technical standpoint, this runs entirely on YOUR Azure infrastructure:
> - Your data stays in your Databricks environment
> - The AI models are in your Azure OpenAI instance  
> - We're using your security and governance controls
> 
> There's no data leaving your environment, no third-party dependencies."

### Slide: Next Steps

**Script:**
> "A pilot program can be running in 8 weeks:
> - Weeks 1-2: Connect to your actual data
> - Weeks 3-4: Train custom tools for STIHL-specific metrics
> - Weeks 5-6: User acceptance testing with your analysts
> - Weeks 7-8: Refinement and rollout planning
> 
> The question isn't whether AI analytics is coming - it's whether you want to lead or follow."

---

## Q&A Preparation

### Anticipated Questions:

**Q: "How accurate are the forecasts?"**
> "The system uses Prophet for forecasting, which typically achieves 85-90% accuracy for stable product categories. For new products or unusual events, we combine historical patterns with similar product analogies. The confidence intervals shown are honest about uncertainty."

**Q: "What about data security?"**
> "Everything runs in your Azure tenant. The AI model is Azure OpenAI in your subscription. Data never leaves your environment. We inherit all your existing security controls - RBAC, network restrictions, audit logging."

**Q: "Can it handle our specific metrics and KPIs?"**
> "Absolutely. The custom tools are configurable. During pilot, we'd work with your team to define STIHL-specific calculations like dealer performance scores, seasonal adjustment factors, and regional benchmarks."

**Q: "What training do users need?"**
> "Minimal. If they can describe what they want in English, they can use this. The bigger investment is teaching them to trust conversational analytics and think about questions differently."

**Q: "What happens when it's wrong?"**
> "The agent is designed to show its work and express uncertainty. Users can always drill down to the underlying data. It augments human judgment; it doesn't replace it."

---

## Demo Checklist

### Before Demo:
- [ ] Fresh conversation thread
- [ ] Proactive insights populated (run insight job)
- [ ] Test all queries in sequence
- [ ] Backup screenshots ready
- [ ] Network connectivity verified

### Technical Requirements:
- [ ] AI Foundry Playground access (Week 1)
- [ ] React app running (Week 2)
- [ ] Databricks workspace online
- [ ] Recent data in Gold layer

---

## 🔗 Related Documents

- [PROJECT-MASTER.md](../PROJECT-MASTER.md) - Project overview
- [AGENT.md](../agent/AGENT.md) - Agent capabilities
- [UI.md](../ui/UI.md) - Demo interface

---

**Last Updated**: January 2026
