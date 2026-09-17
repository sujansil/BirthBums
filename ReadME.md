# BirthBums 🎈

A full-stack web application designed to chronologically track and manage upcoming birthdays, deployed on custom cloud infrastructure.

[![Live Demo](https://img.shields.io/badge/Live_Demo-messycode.duckdns.org-brightgreen.svg?style=for-the-badge)](https://messycode.duckdns.org)

## 🏗️ System Architecture & Deployment

This project leverages a robust, self-hosted deployment strategy rather than relying on standard managed hosting providers:

* **Core Backend:** Completely coded by me from the ground up using **Python (Flask)**. It handles server-side routing, database transactions, and the chronological sorting logic required to surface the most imminent birthdays.
* **Frontend Presentation:** Honestly, it's vibecoded. A lightweight, rapidly prototyped user interface focused on responsive design and a clean, minimalist user experience.
* **Cloud Infrastructure:** Provisioned and hosted on an **Oracle Cloud Infrastructure (OCI) Compute Instance**, operating within a dedicated Linux server environment.
* **Networking & Security:** The application is served behind an **Nginx** reverse proxy. Domain resolution is handled via **DuckDNS**, and the connection is fully encrypted with automated SSL certificates provisioned through **Let's Encrypt (Certbot)**.

## ✨ Key Features

* **Dynamic Chronological Dashboard:** Algorithmically calculates the nearest upcoming dates and sorts entries so the next celebration is always front and center.
* **Persistent Data Storage:** Securely manages and retrieves birthday records via the backend database.
* **Continuous Uptime & Security:** Hosted 24/7 on a self-managed cloud server with enforced HTTPS encryption.

## 🚀 Local Development Setup

To run a development server locally, follow the steps below:

### Prerequisites
* Python 3.x
* Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/sujansil/birthbums.git](https://github.com/sujansil/birthbums.git)
   cd birthbums

2. **Initialize a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate

3.**Install dependencies:**
  ```bash
  pip install -r requirements.txt

4.**Launch the application:**
  ```bash
  python app.py  # Update this if your main entry file is named differently

The application will initialize on http://localhost:5000
