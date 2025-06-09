# LAB Officer Newsletter Generator

A Streamlit-based tool to generate HTML newsletters for Legal Aid Bureau officers, summarizing case statistics and survey ratings for a given period.

## Features

- **Automatic CSV encoding detection** via `chardet` (`encoding.py`)
- **Flexible header parsing** for `case_load.csv` (`data_loader.py`)
- **Dynamic date extraction** from column names to set reporting period
- **Per-officer stats computation**: in-house vs. assigned caseloads, reassignments, clearance rates (`processor.py`)
- **Survey and case-level ratings** rendered as star-based visuals (`processor.py` + `renderer.py`)
- **Jinja2 HTML templating** matching the provided `newsletter.html` layout
- **One-click “Generate All”** with ZIP download of individual HTML files via Streamlit (`app.py`)

## Prerequisites

- Python 3.8+
- Google Chrome (for optional HTML→PNG conversion via `html2image` / `pyppeteer`)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/lab-newsletter-generator.git
   cd lab-newsletter-generator
   ```

2. **Create & activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # Linux / macOS
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## File Structure

```
.
├── app.py                   # Streamlit app entrypoint
├── requirements.txt         # Python dependencies
├── templates/
│   └── newsletter.html      # Jinja2 template matching VL.html design
└── utils/
    ├── __init__.py
    ├── encoding.py          # detect_encoding(file) with chardet
    ├── data_loader.py       # load_all_data() + CSV parsing & date extraction
    ├── processor.py         # compute_officer_stats() logic
    └── renderer.py          # render_newsletters() with Jinja2 + stars
```

## Usage

1. **Launch the Streamlit app**
   ```bash
   streamlit run app.py
   ```

2. **Upload three CSVs** in the sidebar:
   - `ratings.csv`
   - `case_load.csv`
   - `namelist.csv`

3. **(Optional) Select officers** or leave blank to select all.

4. **Click “Generate Newsletters”**
   - HTML files will be written to `./output/<ABBR>.html`
   - A ZIP of all newsletters and individual download buttons appear automatically

## Input File Requirements

- All CSVs should have a **`name`** column (lowercased by the loader) containing the **exact same officer strings** across files.
- `case_load.csv` must contain two columns matching the pattern  
  ```
  …Caseload as at DD/MM/YYYY
  ```
  (e.g. “in-house caseload as at 03/08/2024”)
- `namelist.csv` must include at least:  
  ```
  name, abbreviation, function
  ```
- `ratings.csv` can have any survey question columns; all non-metadata columns will be averaged into star ratings.

## Troubleshooting

- **`'float' object has no attribute 'lower'`**  
  Occurs if a `name` cell is blank → Pandas `NaN`.  
  **Solution:** fill or drop empty names in `data_loader.py`:
  ```python
  nl['name'] = nl['name'].fillna('').astype(str).str.strip()
  nl = nl[nl['name'] != '']
  ```
- **Zero/NA stats for an officer**  
  Usually a name mismatch between CSVs.  
  **Solution:** normalize names (strip + title-case) or provide a mapping:
  ```python
  df['name'] = df['name'].str.strip().str.title()
  ```
- **Missing “Caseload as at …” columns**  
  Update the regex in `extract_dates_from_columns()` to match your exact header text.

## Customization

- **Adjust the HTML layout**  
  Edit `templates/newsletter.html` — it’s pure Jinja2/CSS.
- **Change rating logic**  
  Modify `stars_from_score()` in `utils/renderer.py`.
- **Add an export to PNG/PDF**  
  Use the installed `html2image` or `pyppeteer` libraries in `renderer.py` to snapshot the HTML.

## Contributing

1. Fork this repo  
2. Create a feature branch (`git checkout -b feature/xyz`)  
3. Commit your changes (`git commit -am "Add xyz"`)  
4. Push to the branch (`git push origin feature/xyz`)  
5. Open a Pull Request

---

*Built for the Legal Aid Bureau, Singapore. For questions or issues, please contact the OPDA team.*
