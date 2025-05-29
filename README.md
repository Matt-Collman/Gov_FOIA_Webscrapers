# gov_foia_webscrapers

This repository contains Python-based web scrapers designed to automate the downloading and organization of public documents from various U.S. government FOIA reading rooms.

## 🛠️ Features

- Agency-specific scrapers (CIA, DoD, DHS, SSA, etc.)
- PDF downloading and sorting
- Support for folder-based organization
- Handles paginated or nested page structures
- Designed for long-term archiving projects

## 📂 Structure

- `scrapers/` — Scripts for scraping different FOIA reading rooms
- `utils/` — Helpers for downloading, sorting, or converting PDFs
- `README.md` — Overview of how to use the tools

## 🚀 Getting Started

1. Clone the repo:
   ```bash
   git clone https://github.com/Matt-Collman/gov_foia_webscrapers.git
   cd gov_foia_webscrapers

 Requirements

    Python 3.10+

    Libraries: requests, beautifulsoup4, tqdm, selenium

Notes

    Scrapers are tailored to specific FOIA websites

    Output folders are automatically created and named after the agency

    Designed to be modular and easily extended