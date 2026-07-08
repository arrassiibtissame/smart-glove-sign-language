# 🧤SignBridge — Smart Glove Sign Language Translator

<div align="center">

<img src="src/assets/Logo.png" alt="SignBridge Logo" width="120"/>


### AI-Powered Smart Glove for Real-Time Sign Language Translation

*Traduction en temps réel de la langue des signes grâce à un gant intelligent IA*

[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat&logo=typescript)](https://typescriptlang.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=flat&logo=supabase)](https://supabase.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Grade](https://img.shields.io/badge/Capstone%20Grade-Excellent-brightgreen)](.)

[English](#english) · [Français](#français)

</div>

---

<a name="english"></a>

## 📖 Overview

**SignBridge** is a capstone project developed at **Cyprus International University** that bridges the communication gap between deaf/hard-of-hearing individuals and the hearing world. A smart glove equipped with flex sensors and an IMU captures hand gestures in real time, which are classified by two deep learning models and instantly displayed as text and speech on a web application.

> *Over 1.5 billion people worldwide live with hearing loss (WHO, 2023). SignBridge aims to make everyday communication seamless — without an interpreter.*

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SIGNBRIDGE SYSTEM                        │
│                                                                 │
│  ┌──────────┐    WebSocket    ┌────────────────────────────┐   │
│  │  Smart   │ ─────────────▶  │      FastAPI Backend        │   │
│  │  Glove   │                 │  ┌──────────────────────┐  │   │
│  │  ESP32   │                 │  │   SessionBuffer       │  │   │
│  │  5 Flex  │                 │  │  (gesture boundary    │  │   │
│  │  MPU6050 │                 │  │   detection)          │  │   │
│  └──────────┘                 │  └──────────┬───────────┘  │   │
│                               │             │               │   │
│                               │  ┌──────────▼───────────┐  │   │
│                               │  │   preprocessing.py    │  │   │
│                               │  │   (normalization)     │  │   │
│                               │  └──────────┬───────────┘  │   │
│                               │             │               │   │
│                               │  ┌──────────▼───────────┐  │   │
│                               │  │   model.py            │  │   │
│                               │  │  Static  │  Dynamic   │  │   │
│                               │  │  Conv1D  │ Conv1D+LSTM│  │   │
│                               │  └──────────┬───────────┘  │   │
│                               └─────────────┼──────────────┘   │
│                                             │ WebSocket         │
│  ┌──────────────────────────────────────────▼──────────────┐   │
│  │                    React Frontend                        │   │
│  │   Dashboard · History · Learning · Settings · Auth      │   │
│  └──────────────────────────┬───────────────────────────────┘   │
│                             │                                   │
│  ┌──────────────────────────▼───────────────────────────────┐  │
│  │              Supabase (PostgreSQL + Auth)                 │  │
│  │   profiles · history · user_settings · feedback          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Patterns Used
| Pattern | Where Applied |
|---|---|
| **N-Tier Layered** | Full system structure (UI → State → Logic → Data → DB) |
| **Event-Driven** | WebSocket real-time gesture streaming |
| **Pipeline** | Backend: Sensor → Buffer → Normalize → Predict → Push |
| **Flux** | Frontend state management via Zustand |
| **Component-Based** | React UI component tree |

---

## ✨ Features

- 🤟 **Real-time ASL translation** — gesture to text in under 100ms
- 🧠 **Dual AI models** — static (Conv1D) for letters/numbers, dynamic (Conv1D+LSTM) for words/phrases
- 🌍 **4-language support** — English, French, Arabic (RTL), Turkish
- 📜 **Translation history** — searchable, star-able, exportable
- 📖 **Learning module** — interactive lessons for alphabet, numbers, colors, greetings, social words
- 🔒 **Secure by default** — Row-Level Security on all database tables
- 🔊 **Text-to-speech** — translations spoken aloud in the selected language
- 📱 **Responsive design** — works on desktop and mobile

---

## 🛠️ Tech Stack

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| React | 18 | UI framework |
| TypeScript | 5 | Type safety |
| Vite | 5 | Build tool |
| Tailwind CSS | 3 | Styling |
| Zustand | 4 | State management |
| React Router | v6 | Client-side routing |
| react-i18next | 13 | Internationalization |
| Supabase JS | 2 | Auth + database client |

### Backend
| Technology | Purpose |
|---|---|
| FastAPI | WebSocket server + REST API |
| Python 3.10 | Backend runtime |
| Keras / TensorFlow | AI model inference |
| NumPy | Sensor data processing |
| WebSockets | Real-time communication |

### Hardware
| Component | Purpose |
|---|---|
| ESP32-S3 | Microcontroller + WiFi |
| 5× Flex Sensors | Finger bend detection |
| MPU-6050 IMU | Accelerometer + Gyroscope |
| LiPo Battery | Portable power |

### Infrastructure
| Service | Purpose |
|---|---|
| Supabase | PostgreSQL + Authentication |
| Vercel | Frontend hosting |
| Railway | Backend hosting |

---

## 📁 Project Structure

```
Smart-Glove-Sign-Translator/
├── src/
│   ├── components/          # Shared UI components
│   │   ├── Layout/          # SideBar, Header
│   │   ├── SplashScreen/    # Animated splash
│   │   └── ui/              # shadcn/ui components
│   ├── features/            # Feature modules
│   │   ├── dashboard/       # ASL input + translation cards
│   │   ├── history/         # Translation history
│   │   ├── learningAlphabet/# Learning module components
│   │   └── learningsP/      # Learning category pages
│   ├── lib/
│   │   └── supabase/        # Database layer (auth, history, gestures)
│   ├── locales/             # i18n translation files
│   │   ├── en/              # English
│   │   ├── fr/              # French
│   │   ├── ar/              # Arabic
│   │   └── tr/              # Turkish
│   ├── pages/               # Page-level components
│   ├── store/               # Zustand global stores
│   │   ├── authStore.ts     # User session
│   │   ├── historyStore.ts  # Translation history
│   │   └── gloveStore.ts    # Live glove state
│   ├── styles/              # Global CSS + design tokens
│   └── Types/               # TypeScript interfaces
├── backend/
│   ├── main.py              # FastAPI server + WebSocket endpoints
│   ├── model.py             # AI model loading + inference
│   ├── preprocessing.py     # Sensor data normalization
│   ├── artifacts/           # Trained models + label maps
│   └── test_client.py       # Glove simulator for testing
├── public/
│   └── images/              # ASL sign reference images
├── vercel.json              # Vercel deployment config
└── README.md
```

---

## 🗄️ Database Schema

```
auth.users (Supabase managed)
    │
    ├── profiles
    │   ├── id (UUID) → auth.users.id
    │   ├── full_name
    │   └── avatar_url
    │
    ├── history
    │   ├── id (UUID)
    │   ├── user_id → auth.users.id
    │   ├── input (gesture label)
    │   ├── output (translated text)
    │   ├── language
    │   ├── starred
    │   ├── model_used (static/dynamic)
    │   └── confidence (float)
    │
    ├── user_settings
    │   ├── user_id → auth.users.id
    │   ├── output_language
    │   └── glove_hand
    │
    └── feedback
        ├── user_id → auth.users.id
        ├── message
        └── rating
```

All tables are protected by **Row-Level Security** — users can only access their own data.

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- A Supabase project ([supabase.com](https://supabase.com))

---

### Frontend Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/Smart-Glove-Sign-Translator.git
cd Smart-Glove-Sign-Translator

# 2. Install dependencies
npm install

# 3. Create environment file
cp .env.example .env
```

Edit `.env`:
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

```bash
# 4. Start development server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

---

### Backend Setup

```bash
# 1. Navigate to backend folder
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
uvicorn main:app --reload --port 8000
```

Backend runs at [http://localhost:8000](http://localhost:8000)

---

### Database Setup

Run this SQL in your **Supabase SQL Editor**:

```sql
-- Profiles table
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name TEXT,
  avatar_url TEXT,
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- History table
CREATE TABLE history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  input TEXT NOT NULL,
  output TEXT NOT NULL,
  language TEXT DEFAULT 'ASL',
  starred BOOLEAN DEFAULT false,
  model_used TEXT,
  confidence FLOAT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- User settings
CREATE TABLE user_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
  output_language TEXT DEFAULT 'en',
  glove_hand TEXT DEFAULT 'right',
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Feedback
CREATE TABLE feedback (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  message TEXT,
  rating INT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS on all tables
ALTER TABLE profiles      ENABLE ROW LEVEL SECURITY;
ALTER TABLE history       ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback      ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users access own profile"  ON profiles      FOR ALL USING (auth.uid() = id);
CREATE POLICY "Users access own history"  ON history       FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users access own settings" ON user_settings FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users access own feedback" ON feedback      FOR ALL USING (auth.uid() = user_id);
```

---

### Test Without Hardware

Use the glove simulator to test the full pipeline without the physical glove:

```bash
cd backend
python test_client.py
```

This sends fake sensor data to `/ws/glove`, triggering the full pipeline from sensor input to frontend display.

---

## 🌍 Deployment

### Frontend → Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

Set environment variables in Vercel dashboard:
```
VITE_SUPABASE_URL
VITE_SUPABASE_ANON_KEY
VITE_API_URL      → https://your-backend.railway.app
VITE_WS_URL       → wss://your-backend.railway.app
```

### Backend → Railway

1. Push backend to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Railway auto-detects Python and runs `Procfile`
4. Copy the Railway URL to your Vercel environment variables

---

## 👥 Team

| Name | Role |
|---|---|
| **Ibtissame Arrassi** |Full Stack Developer |
| **Imane Sayd** |AI / ML Engineer  |
| **Ferdaws Anzer** |Full Stack Developer |
| **Ketsia Winner** |Electric electronic  Engineer |
| **Logance Musese** |Electric electronic Engineer |
| **Chadrack Zeka** |Computer engineer |

**Supervisor:** Prof. Dr. Melike Şah Direkoğlu — Cyprus International University

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

---

<a name="français"></a>

## 📖 Présentation

**SignBridge** est un projet de fin d'études développé à l'**Université Internationale de Chypre** qui vise à éliminer la barrière de communication entre les personnes sourdes/malentendantes et le reste du monde. Un gant intelligent équipé de capteurs de flexion et d'une centrale inertielle (IMU) capture les gestes de la main en temps réel. Ces gestes sont classifiés par deux modèles d'apprentissage profond et affichés instantanément sous forme de texte et de parole sur une application web.

> *Plus de 1,5 milliard de personnes vivent avec une perte auditive dans le monde (OMS, 2023). SignBridge vise à rendre la communication quotidienne fluide — sans interprète.*

---

## ✨ Fonctionnalités

- 🤟 **Traduction ASL en temps réel** — geste vers texte en moins de 100ms
- 🧠 **Double modèle IA** — statique (Conv1D) pour les lettres/chiffres, dynamique (Conv1D+LSTM) pour les mots/phrases
- 🌍 **Support 4 langues** — Anglais, Français, Arabe (RTL), Turc
- 📜 **Historique des traductions** — consultable, marquable, exportable
- 📖 **Module d'apprentissage** — leçons interactives pour l'alphabet, les chiffres, les couleurs, les salutations et les mots sociaux
- 🔒 **Sécurité par défaut** — Row-Level Security sur toutes les tables de la base de données
- 🔊 **Synthèse vocale** — les traductions sont prononcées à voix haute dans la langue sélectionnée

---

## 🚀 Installation

### Frontend

```bash
# Cloner le dépôt
git clone https://github.com/your-username/Smart-Glove-Sign-Translator.git
cd Smart-Glove-Sign-Translator

# Installer les dépendances
npm install

# Créer le fichier d'environnement
cp .env.example .env
```

Modifier `.env` :
```env
VITE_SUPABASE_URL=https://votre-projet.supabase.co
VITE_SUPABASE_ANON_KEY=votre-clé-anon
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

```bash
# Lancer le serveur de développement
npm run dev
```

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

---

## 👥 Équipe

| Nom | Rôle |
|---|---|
| **Ibtissame Arrassi** | Développeuse Full Stack |
| **Imane Sayd** | Ingénieure IA / ML  |
| **Ferdaws Anzer** |Développeuse Full Stack  |
| **Ketsia Winner** | Ingénieure electrique |
| **Logance Musese** | Développeur electrique |
| **Chadrack Zeka** | Ingénieur computer|

**Encadrant :** Prof. Dr. Melike Şah Direkoğlu — Université Internationale de Chypre

---

<div align="center">

Made with ❤️ at Cyprus International University · 2026

</div>
> ⚠️ **Original Repository**: This is the official and original repository of SignBridge, developed by 
the SignBridge Team at Cyprus International University. Any copies or forks are not the original work.

---

## 📜 License

© 2026 SignBridge Team. All rights reserved.
