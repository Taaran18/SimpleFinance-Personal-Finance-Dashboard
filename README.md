# 💰 Simple Finance Dashboard

**A beautiful, interactive, and modular Streamlit app for effortless personal finance management.**

---

## 🚀 Why This Project Stands Out

- **Modern, Intuitive UI:** Clean, wide-layout dashboard with interactive charts and real-time editing.
- **Smart Categorization:** Auto-categorizes transactions and learns your patterns as you edit.
- **Deep Insights:** Instantly see trends, anomalies, recurring payments, and your net savings.
- **Full Control:** Add new categories, keywords, and drill down into any detail—no code needed.
- **One-Click Exports:** Download any filtered or summarized data instantly.
- **Plug-and-Play:** Just drop in your CSV and go—no setup headaches.

---

## ✨ Features

- 📊 Upload and analyze your bank statement CSV
- 🏷️ Automatic & manual transaction categorization
- 🥧 Visualize expenses/income by category (Pie/Bar)
- 📅 Monthly/yearly trends & running balance
- 🏆 Top N expenses/payments & anomaly detection
- 🔁 Recurring transaction detection
- 🔍 Category drilldown, search, and filtering
- ⬇️ Download filtered or summary data as CSV
- ➕ Add/edit categories and keywords dynamically

---

## ⚡ Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   ```
2. **Navigate to the project directory:**
   ```bash
   cd <project-directory>
   ```
3. **Install dependencies:**
   ```bash
   pip install streamlit pandas plotly
   ```
4. **Launch the dashboard:**
   ```bash
   streamlit run main.py
   ```
5. **Open the app in your browser, upload your CSV, and explore your finances!**

---

## 🗂️ File Structure

| File              | Purpose                                  |
| ----------------- | ---------------------------------------- |
| `main.py`         | Entry point                              |
| `dashboard.py`    | Streamlit UI and dashboard logic         |
| `utils.py`        | Data loading, saving, and categorization |
| `filters.py`      | Filtering and transformation helpers     |
| `categories.json` | Category definitions and keywords        |
| `statements.csv`  | Your bank statement data                 |

---

## 💡 Pro Tips

- **Edit categories and keywords on the fly** to improve auto-categorization.
- **Use the search and filter sidebar** for instant drilldown and insights.
- **Export any view** with a single click for reporting or backup.

---

**Ready to take control of your finances? Try it now!**
