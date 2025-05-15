# 🔍 Scraper cen konkurencji – JarajTo

## Jak działa:
- Codziennie pobiera ceny produktów z konkurencyjnych sklepów.
- Aktualizuje dane w Twoim Google Sheets.
- Porównuje je z Twoją ceną i zapisuje różnicę + status.

## 📦 Struktura arkusza:
| Nazwa produktu | Link do produktu | Cena u nas | Link Vaporshop | Cena Vaporshop | Różnica Vaporshop | ... |

## 🧩 Dodawanie nowych produktów:
1. Dodaj nowy wiersz.
2. Wpisz nazwę, link do produktu u siebie, oraz linki do konkurencji.
3. Skrypt uzupełni ceny i różnice.

## ➕ Dodawanie nowego konkurenta:
1. Dodaj kolumny:
   - Link [NowySklep]
   - Cena [NowySklep]
   - Różnica [NowySklep]
2. Dodaj nową funkcję scrapującą do `scraper.py`.

## 🚀 Uruchamianie:
1. Wgraj swoje credentials z Google API (plik JSON).
2. Ustaw cron job (Render / GitHub Actions) do odpalenia `main.py`.

