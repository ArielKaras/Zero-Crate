# ZeroCrate 
### The Autonomous Digital Asset Acquisition Engine

![License](https://img.shields.io/badge/license-Proprietary-red.svg)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Status](https://img.shields.io/badge/status-Production-green.svg)

**ZeroCrate** is an enterprise-grade automated system designed to aggregate, analyze, and secure high-value digital game assets from disparate global marketplaces (Steam, Epic Games, GOG). It serves as a unified "Cinematic" dashboard for the modern digital collector.

---

## 🚀 Key Features

### 💎 The "Hero Rail" Technology
Our proprietary algorithm aggregates time-sensitive opportunities into a single, high-urgency feed.
- **Urgency Detection**: Automatically prioritizes offers ending in < 24 hours.
- **Value Analysis**: Sorts assets by historical collection value.

### 📡 Multi-Vector Mining
Autonomous miners deployed for major distribution platforms:
- **Steam**: Deep scan for 100% off promotions.
- **Epic Games**: Weekly high-value asset acquisition.
- **Scout**: Heuristic scanning of community signals (RSS/Reddit).

### 🖥️ Cinematic Visualization
A premium, dark-mode/glassmorphism interface built for visual clarity.
- **Magnetic Scrolling**: Frictionless asset browsing.
- **Dynamic Hues**: Unique identity generation for every asset.
- **Responsive Design**: Mobile-ready "Safe Peek" architecture.

### 🔒 Military-Grade Security
- **Data Sovereignty**: All user state managed locally via SQLite.
- **Containerized**: Fully Dockerized environment (Distroless/Minimize attack surface).
- **No-Leak Guarantee**: Strict separation of credentials and logic.

---

## 🛠️ Deployment

### Prerequisites
- Docker & Docker Compose
- Git

### Quick Start (Production)

1. **Clone the Secure Vault**
   ```bash
   git clone https://github.com/ArielKaras/Zero-Crate.git
   cd Zero-Crate
   ```

2. **Ignition**
   ```bash
   docker-compose up --build -d
   ```

3. **Access Dashboard**
   Navigate to: `http://localhost:8000`

---

## 🏗️ Architecture

- **Backend**: Python 3.13 (FastAPI, AsyncIO)
- **Database**: SQLite (Ledger), JSON (Inventory Cache)
- **Frontend**: Jinja2 (SSR) + Vanilla JS (Efficiency)
- **DevOps**: Multi-Stage Docker Builds, Feature-Branch Workflow


---

## ⚖️ Legal Disclaimer

**ZeroCrate** is a **Deal Aggregation & Portfolio Tracking** tool. It is not affiliated with, endorsed by, or sponsored by Valve Corporation (Steam), Epic Games, Inc., or CD PROJEKT S.A. (GOG).

- **Data Sources**: All asset data is retrieved from publicly available sources or community signals (e.g., Reddit).
- **Terms of Service**: Users are responsible for complying with the Terms of Service of the respective platforms. This tool does not automate the purchasing or claiming process on third-party stores; it strictly manages a *local* inventory simulation.
- **No Warranty**: The software is provided "as is", without warranty of any kind.

## 📜 License
Copyright © 2025 Arielsv Operations. All Rights Reserved.
