# Cottage Creek HOA Website

A self-hosted, modern HOA website designed for a 15-home neighborhood. Built with Flask, Docker, and deployed via Portainer, it supports both development and production workflows with AI-assisted coding.

---

## 🔧 Tech Stack

- **Frontend:** HTML + Jinja (via Flask templates)
- **Backend:** Python (Flask)
- **AI Coding:** [Cursor](https://cursor.so) using GPT-4
- **Containerization:** Docker + Docker Compose
- **Dev Environment:** Mac (local dev using Cursor)
- **Prod Hosting:** Portainer on homelab server (Docky)
- **Source Control:** GitHub

---

## 📁 Project Structure

```
hoa-website/
├── flask-app/                     # Flask application source
│   ├── app/                       # Routes, templates, models
│   ├── instance/                  # SQLite DB lives here
│   ├── run.py                     # Entry point
│   └── Dockerfile                 # Flask Docker build
├── .env.dev                       # Development environment variables
├── .env.prod                      # Production environment variables
├── docker-compose.dev.yml        # For local dev testing (Mac or Docky)
├── docker-compose.prod.yml       # For production deployment via Portainer
├── docker-compose.portainer-dev.yml  # Optional: dev stack in Portainer
```

---

## 🚀 Environments

### 🧪 Local Dev (on Mac with Cursor)
- Launch dev container:
  ```bash
  docker compose -f docker-compose.dev.yml up
  ```
- Access at: `http://localhost:5000`
- Uses `.env.dev` for environment variables

---

### 🌐 Production (Deployed via Portainer)
- Stack name: `hoa-website-prod`
- Compose file: `docker-compose.prod.yml`
- Runs on: `http://192.168.68.109:9090`
- Uses inline env vars (no external `.env` file needed)

---

## 💡 Development Tools

| Tool | Purpose |
|------|---------|
| **Cursor IDE** | AI pair programming (GPT-4) |
| **ChatGPT Desktop** | Project-wide insight and refactoring |
| **GitHub** | Source control and backup |
| **Portainer** | Prod stack management on homelab |
| **Docker Compose** | Dev/prod container orchestration |

---

## 🔐 Authentication (Planned)

To be implemented:
- Option A: Flask-Login
- Option B: Reverse proxy auth with Nginx Proxy Manager

---

## 📦 Future Enhancements

- [ ] Add login and role-based access
- [ ] Enable HTTPS with Nginx Proxy Manager
- [ ] Set up automated deployment with GitHub Actions
- [ ] Build public/private section UI
- [ ] Add neighbor forum and Python app launcher

---

## 📌 Notes

- Dev and prod containers use different ports (`5000`, `9090`)
- Only prod runs continuously on Docky via Portainer
- Dev can be run either locally (Mac) or as a stack if needed

---

## 🧠 AI Support

This project was built with extensive help from ChatGPT and Cursor for:
- Dockerizing Flask
- Creating clean folder structures
- Splitting environments
- Git/GitHub workflows
- Portainer deployment and debugging
