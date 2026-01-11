# UI - React Frontend & Visualizations

> **Parent**: [PROJECT-MASTER.md](../PROJECT-MASTER.md)  
> **Status**: ⏳ Pending (Week 2)  
> **Owner**: Frontend Development

---

## Overview

This document covers the frontend interface for the STIHL Analytics Agent, progressing from Week 1 (Playground) to Week 2 (Custom React).

---

## 1. UI Timeline

| Week | Interface | Purpose |
|------|-----------|---------|
| **Week 1** | AI Foundry Playground | Rapid prototyping, agent testing |
| **Week 2** | React + Plotly | Interactive demo, polished UX |

---

## 2. Week 1: AI Foundry Playground

### 2.1 Access

1. Navigate to AI Foundry Studio
2. Select `stihl-analytics-agent` project
3. Open **Playground** tab
4. Select your agent

### 2.2 Features Available

- ✅ Chat interface
- ✅ Code Interpreter (matplotlib charts)
- ✅ File uploads
- ✅ Conversation history
- ❌ Custom styling
- ❌ Interactive charts

### 2.3 Code Interpreter Charts

During Week 1, visualizations are generated via Code Interpreter:

```python
# Agent generates this code internally
import matplotlib.pyplot as plt
import pandas as pd

# Data from query
data = pd.DataFrame(query_results)

plt.figure(figsize=(10, 6))
plt.bar(data['month'], data['revenue'])
plt.title('Monthly Sales Revenue')
plt.xlabel('Month')
plt.ylabel('Revenue ($)')
plt.savefig('chart.png')
```

Output: PNG image in chat

---

## 3. Week 2: React Application

### 3.1 Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.x | UI framework |
| Vite | 5.x | Build tool |
| Tailwind CSS | 3.x | Styling |
| Plotly.js | 2.x | Interactive charts |
| React Query | 5.x | Data fetching |
| Zustand | 4.x | State management |

### 3.2 Project Setup

```powershell
# Navigate to ui folder
cd ui

# Create React app with Vite
npm create vite@latest . -- --template react

# Install dependencies
npm install plotly.js react-plotly.js
npm install @tanstack/react-query
npm install zustand
npm install tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install Azure SDK
npm install @azure/identity @azure/ai-projects
```

### 3.3 Folder Structure

```
ui/
├── public/
│   └── stihl-logo.svg
├── src/
│   ├── components/
│   │   ├── Chat/
│   │   │   ├── ChatContainer.jsx
│   │   │   ├── MessageList.jsx
│   │   │   ├── MessageBubble.jsx
│   │   │   ├── InputBar.jsx
│   │   │   └── ProactiveInsights.jsx
│   │   ├── Charts/
│   │   │   ├── SalesChart.jsx
│   │   │   ├── InventoryChart.jsx
│   │   │   ├── ForecastChart.jsx
│   │   │   └── ChartContainer.jsx
│   │   ├── Layout/
│   │   │   ├── Header.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   └── Footer.jsx
│   │   └── Common/
│   │       ├── Loading.jsx
│   │       └── ErrorBoundary.jsx
│   ├── hooks/
│   │   ├── useAgent.js
│   │   ├── useChat.js
│   │   └── useCharts.js
│   ├── services/
│   │   ├── agentService.js
│   │   └── apiClient.js
│   ├── store/
│   │   └── chatStore.js
│   ├── styles/
│   │   └── globals.css
│   ├── App.jsx
│   └── main.jsx
├── package.json
├── vite.config.js
├── tailwind.config.js
└── .env.local
```

---

## 4. Component Specifications

### 4.1 ChatContainer.jsx

```jsx
import React, { useEffect } from 'react';
import { useChat } from '../hooks/useChat';
import MessageList from './MessageList';
import InputBar from './InputBar';
import ProactiveInsights from './ProactiveInsights';

export default function ChatContainer() {
  const { 
    messages, 
    isLoading, 
    proactiveInsights,
    sendMessage, 
    initializeChat 
  } = useChat();

  useEffect(() => {
    initializeChat();
  }, []);

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Proactive Insights Banner */}
      {proactiveInsights.length > 0 && (
        <ProactiveInsights insights={proactiveInsights} />
      )}
      
      {/* Message List */}
      <div className="flex-1 overflow-y-auto p-4">
        <MessageList messages={messages} isLoading={isLoading} />
      </div>
      
      {/* Input Bar */}
      <div className="border-t bg-white p-4">
        <InputBar onSend={sendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}
```

### 4.2 MessageBubble.jsx

```jsx
import React from 'react';
import ChartContainer from '../Charts/ChartContainer';

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div 
        className={`max-w-3xl rounded-lg p-4 ${
          isUser 
            ? 'bg-orange-500 text-white' 
            : 'bg-white border shadow-sm'
        }`}
      >
        {/* Text Content */}
        <div className="prose prose-sm">
          {message.content}
        </div>
        
        {/* Chart if present */}
        {message.chart && (
          <ChartContainer chartData={message.chart} />
        )}
        
        {/* Timestamp */}
        <div className={`text-xs mt-2 ${isUser ? 'text-orange-200' : 'text-gray-400'}`}>
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}
```

### 4.3 ProactiveInsights.jsx

```jsx
import React from 'react';

const ICONS = {
  ANOMALY: '🚨',
  ALERT: '📦',
  TREND: '📈',
  FORECAST: '🔮'
};

const COLORS = {
  HIGH: 'border-red-500 bg-red-50',
  MEDIUM: 'border-yellow-500 bg-yellow-50',
  LOW: 'border-blue-500 bg-blue-50'
};

export default function ProactiveInsights({ insights }) {
  return (
    <div className="bg-gradient-to-r from-orange-500 to-orange-600 p-4">
      <h3 className="text-white font-semibold mb-3">
        🔔 Insights Requiring Attention
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {insights.slice(0, 3).map((insight) => (
          <div 
            key={insight.id}
            className={`rounded-lg p-3 border-l-4 ${COLORS[insight.priority]}`}
          >
            <div className="flex items-start gap-2">
              <span className="text-xl">{ICONS[insight.type]}</span>
              <div>
                <p className="font-medium text-gray-800">{insight.title}</p>
                <p className="text-sm text-gray-600 mt-1">{insight.summary}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 5. Chart Components

### 5.1 SalesChart.jsx (Plotly)

```jsx
import React from 'react';
import Plot from 'react-plotly.js';

export default function SalesChart({ data, title }) {
  const chartData = [{
    type: 'bar',
    x: data.map(d => d.month),
    y: data.map(d => d.revenue),
    marker: {
      color: '#f97316'  // STIHL orange
    }
  }];

  const layout = {
    title: {
      text: title || 'Sales Revenue',
      font: { size: 16 }
    },
    xaxis: { title: 'Month' },
    yaxis: { 
      title: 'Revenue ($)',
      tickformat: '$,.0f'
    },
    margin: { t: 50, r: 30, b: 50, l: 80 },
    plot_bgcolor: 'white',
    paper_bgcolor: 'white'
  };

  const config = {
    displayModeBar: true,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    responsive: true
  };

  return (
    <Plot
      data={chartData}
      layout={layout}
      config={config}
      className="w-full h-64"
    />
  );
}
```

### 5.2 ForecastChart.jsx (with confidence intervals)

```jsx
import React from 'react';
import Plot from 'react-plotly.js';

export default function ForecastChart({ historical, forecast }) {
  const chartData = [
    // Historical data
    {
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Historical',
      x: historical.map(d => d.date),
      y: historical.map(d => d.value),
      line: { color: '#374151' }
    },
    // Forecast line
    {
      type: 'scatter',
      mode: 'lines',
      name: 'Forecast',
      x: forecast.map(d => d.date),
      y: forecast.map(d => d.value),
      line: { color: '#f97316', dash: 'dash' }
    },
    // Confidence interval
    {
      type: 'scatter',
      mode: 'lines',
      name: 'Upper Bound',
      x: forecast.map(d => d.date),
      y: forecast.map(d => d.upper),
      line: { width: 0 },
      showlegend: false
    },
    {
      type: 'scatter',
      mode: 'lines',
      name: 'Confidence Interval',
      x: forecast.map(d => d.date),
      y: forecast.map(d => d.lower),
      fill: 'tonexty',
      fillcolor: 'rgba(249, 115, 22, 0.2)',
      line: { width: 0 }
    }
  ];

  const layout = {
    title: 'Sales Forecast with 95% Confidence Interval',
    xaxis: { title: 'Date' },
    yaxis: { title: 'Units', tickformat: ',.0f' },
    legend: { orientation: 'h', y: -0.2 }
  };

  return <Plot data={chartData} layout={layout} className="w-full h-80" />;
}
```

---

## 6. Agent Service

### 6.1 agentService.js

```javascript
import { AIProjectClient } from '@azure/ai-projects';
import { DefaultAzureCredential } from '@azure/identity';

class AgentService {
  constructor() {
    this.client = new AIProjectClient(
      process.env.VITE_FOUNDRY_ENDPOINT,
      new DefaultAzureCredential()
    );
    this.agentId = null;
    this.threadId = null;
  }

  async initialize() {
    // Get or create agent
    const agents = await this.client.agents.listAgents();
    const existingAgent = agents.find(a => a.name === 'stihl-analytics-agent');
    
    if (existingAgent) {
      this.agentId = existingAgent.id;
    } else {
      throw new Error('Agent not found. Please create agent first.');
    }

    // Create thread
    const thread = await this.client.agents.createThread();
    this.threadId = thread.id;
    
    return { agentId: this.agentId, threadId: this.threadId };
  }

  async sendMessage(content) {
    // Add message
    await this.client.agents.createMessage({
      threadId: this.threadId,
      role: 'user',
      content
    });

    // Run agent
    const run = await this.client.agents.createAndProcessRun({
      threadId: this.threadId,
      assistantId: this.agentId
    });

    // Get messages
    const messages = await this.client.agents.listMessages({
      threadId: this.threadId
    });

    // Parse response for charts
    const latestMessage = messages[0];
    return this.parseResponse(latestMessage);
  }

  parseResponse(message) {
    const response = {
      content: message.content[0].text.value,
      chart: null,
      timestamp: new Date()
    };

    // Check for chart JSON in response
    const chartMatch = response.content.match(/```plotly\n([\s\S]*?)\n```/);
    if (chartMatch) {
      try {
        response.chart = JSON.parse(chartMatch[1]);
        response.content = response.content.replace(chartMatch[0], '');
      } catch (e) {
        console.error('Failed to parse chart data:', e);
      }
    }

    return response;
  }
}

export default new AgentService();
```

---

## 7. State Management

### 7.1 chatStore.js (Zustand)

```javascript
import { create } from 'zustand';

export const useChatStore = create((set, get) => ({
  messages: [],
  proactiveInsights: [],
  isLoading: false,
  error: null,

  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),

  setProactiveInsights: (insights) => set({ proactiveInsights: insights }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),

  clearChat: () => set({ messages: [], proactiveInsights: [], error: null })
}));
```

---

## 8. Environment Variables

### 8.1 .env.local

```env
VITE_FOUNDRY_ENDPOINT=https://stihl-analytics-agent.cognitiveservices.azure.com/
VITE_AZURE_TENANT_ID=<your-tenant-id>
VITE_AZURE_CLIENT_ID=<your-client-id>
```

---

## 9. Styling (STIHL Brand)

### 9.1 tailwind.config.js

```javascript
module.exports = {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        'stihl-orange': '#f97316',
        'stihl-gray': '#374151',
        'stihl-light': '#f3f4f6'
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif']
      }
    }
  },
  plugins: []
};
```

---

## ✅ UI Checklist

### Week 1 (Playground)
- [ ] Agent accessible in Playground
- [ ] Code Interpreter charts working
- [ ] Proactive insights displaying
- [ ] Basic queries functional

### Week 2 (React)
- [ ] React project scaffolded
- [ ] Tailwind CSS configured
- [ ] Chat components built
- [ ] Agent service connected
- [ ] Plotly charts integrated
- [ ] Proactive insights banner
- [ ] Responsive design
- [ ] STIHL branding applied
- [ ] Error handling
- [ ] Loading states

---

## 🔗 Related Documents

- [AGENT.md](../agent/AGENT.md) - Agent API integration
- [docs/DEMO-SCRIPT.md](../docs/DEMO-SCRIPT.md) - Demo presentation

---

**Last Updated**: January 2026
