# 🏦 Multi-Bank Deposito Reconciliation System

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.31.0-FF4B4B.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-green.svg)](https://github.com)

**Sistem rekonsiliasi deposito multi-bank dengan AI-powered analysis untuk BPKH (Badan Pengelola Keuangan Haji).**

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Banks Supported](#-banks-supported)
- [Quick Start](#-quick-start)
- [Installation](#️-installation)
- [Configuration](#️-configuration)
- [Usage Guide](#-usage-guide)
- [Project Structure](#-project-structure)
- [Adding New Bank](#-adding-new-bank)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

Aplikasi web berbasis **Streamlit** untuk melakukan rekonsiliasi otomatis deposito syariah antara data Bank dan BPKH. Dilengkapi dengan **AI-powered analysis** menggunakan **Qwen3** atau **Claude** untuk memberikan insight mendalam tentang variance dan rekomendasi tindakan.

### Key Benefits

✨ **Multi-Bank Support** - Proses 4 bank sekaligus  
🤖 **AI Analysis** - Root cause analysis otomatis  
📊 **Interactive Dashboard** - Real-time visualization  
📈 **Trend Analysis** - Pattern recognition  
⚡ **Fast Processing** - Handle ribuan transaksi  
📥 **Excel Export** - Formatted professional reports  

---

## 🚀 Features

### Core Features

| Feature | Description | Status |
|---------|-------------|---------|
| **Multi-Bank Processing** | Process BTPN, BPS, Mandiri, BNI simultaneously | ✅ |
| **Smart Excel Parser** | Auto-detect headers, formats, sheets | ✅ |
| **AI-Powered Analysis** | Root cause analysis with recommendations | ✅ |
| **Interactive Dashboard** | Real-time KPIs and visualizations | ✅ |
| **Exception Reporting** | Auto-flag high variance items | ✅ |
| **Trend Analysis** | Time-series pattern recognition | ✅ |
| **Professional Export** | Formatted Excel reports with styling | ✅ |
| **Variance Categorization** | Excellent/Good/Warning/Critical levels | ✅ |

### Advanced Features

| Feature | Description | Status |
|---------|-------------|---------|
| **Docker Support** | Containerized deployment | ✅ |
| **CI/CD Pipeline** | Automated testing & deployment | ✅ |
| **API Integration** | RESTful API for automation | ✅ |
| **Multi-format Support** | Excel (.xlsx, .xls), CSV | ✅ |
| **Data Validation** | Comprehensive input validation | ✅ |
| **Error Recovery** | Robust error handling | ✅ |
| **Audit Trail** | Complete logging system | ✅ |
| **Configurable Rules** | Bank-specific configurations | ✅ |

---

## 🏦 Banks Supported

| Bank | Code | Status | Nisbah SA | Nisbah NM | Last Updated |
|------|------|--------|-----------|-----------|--------------|
| **BTPN Syariah** | BTPN | ✅ Production | 9.30% | 8.35% | Sep 2025 |
| **Bank BPS** | BPS | ✅ Production | 4.75% | 5.00% | Sep 2025 |
| **Mandiri Syariah** | MSI | ✅ Production | 4.80% | 5.10% | Sep 2025 |
| **BNI Syariah** | BNIS | ✅ Production | 4.85% | 5.15% | Sep 2025 |

### Deposito Types Supported

- **SA** - Setoran Awal
- **SL** - Setoran Lunas  
- **NM** - Nilai Manfaat
- **LPS** - LPS Program
- **DAU** - DAU (if applicable)

---

## ⚡ Quick Start

### One-Line Setup

```bash
# Create project & install dependencies
git clone <repo-url> && cd deposito-rekon-app && ./scripts/setup.sh
```

### Configure & Run

```bash
# Configure API keys
cp .env.example .env
nano .env  # Add your API keys

# Start application
./scripts/run.sh
```

**🌐 Open**: http://localhost:8501

---

## 🛠️ Installation

### Prerequisites

- **Python 3.10+** (recommended: 3.11)
- **Git** (for cloning)
- **OpenRouter API Key** (for AI features)

### Method 1: Automatic Setup

```bash
# Clone repository
git clone <repository-url>
cd deposito-rekon-app

# Run automatic setup
./scripts/setup.sh

# Configure environment
cp .env.example .env
nano .env  # Edit with your API keys

# Start application
./scripts/run.sh
```

### Method 2: Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate environment
source venv/Scripts/activate  # Windows Git Bash
# source venv/bin/activate     # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env

# 5. Run application
streamlit run app/main.py
```

### Method 3: Docker

```bash
# Using Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop
docker-compose down
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file from template:

```bash
cp .env.example .env
```

**Required Variables:**

```env
# AI Analysis (Choose one)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxx

# Optional: Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=deposito_rekon
DB_USER=postgres
DB_PASSWORD=your_password

# Optional: Email Notifications
SMTP_USER=your-email@domain.com
SMTP_PASSWORD=your-password
FROM_EMAIL=noreply@domain.com
TO_EMAILS=admin@domain.com,team@domain.com
```

### Bank Configuration

Each bank has its own config file in `data/banks/{bank_code}/config.json`:

```json
{
  "bank_code": "BTPN",
  "bank_name": "Bank BTPN Syariah",
  "column_mapping": {
    "nomor_bilyet": "Nomor Bilyet",
    "nomor_rekening": "Nomor Rekening",
    "nominal_deposito": "Nominal Deposito",
    "nominal_imbal_hasil": "Nominal Imbal Hasil"
  },
  "nisbah_rates": {
    "SA": 0.0930,
    "SL": 0.0930,
    "NM": 0.0835,
    "LPS": 0.0450
  },
  "sheet_names": {
    "setoran_awal": "Setoran Awal",
    "setoran_lunas": "Setoran Lunas",
    "nilai_manfaat": "Nilai Manfaat"
  },
  "date_format": "%d/%m/%Y",
  "year_days": 360
}
```

### Streamlit Configuration

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#4F46E5"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F3F4F6"
textColor = "#1F2937"
font = "sans serif"

[server]
port = 8501
enableCORS = false
enableXsrfProtection = false
headless = false
```

---

## 📖 Usage Guide

### 1. Launch Application

```bash
streamlit run app/main.py
```

### 2. Upload Files

**Required Files per Bank:**
- **Bank Data**: Excel file dengan data deposito dari bank
- **BPKH Data**: Excel file dengan data realisasi dari BPKH

**Required Columns:**
- Nomor Bilyet
- Nomor Rekening
- Nominal Deposito
- Nominal Imbal Hasil
- Tanggal Penempatan/Realisasi

### 3. Select Banks

Di sidebar, pilih bank yang akan direkonsiliasi:
- ☑️ BTPN Syariah
- ☑️ Bank BPS
- ☑️ Mandiri Syariah
- ☑️ BNI Syariah

### 4. Process Reconciliation

Klik **"🔄 Process Reconciliation"** button.

### 5. View Results

Navigate through tabs:

#### 📊 Dashboard
- Overall KPIs (Accuracy, Quality, Match Rate)
- Bank comparison charts
- Summary statistics

#### 🔍 Detailed Results  
- Record-by-record reconciliation
- Status: Matched/Difference/Not Found
- Filter by bank, status, deposito type

#### 📈 Analytics
- Trend analysis over time
- Variance patterns
- Performance metrics

#### ⚠️ Exceptions
- High-variance items (>0.5%)
- Priority classification
- Investigation recommendations

#### 📥 Export
- Excel reports with formatting
- CSV data exports
- Consolidated reports

### 6. AI Analysis (Optional)

Configure API key in `.env`, then:
1. Go to **AI Analysis** tab
2. Click **"🔍 Jalankan Analisis AI"**
3. Get comprehensive analysis:
   - Root cause analysis
   - Materialitas assessment
   - Risk evaluation
   - Compliance check
   - Actionable recommendations

---

## 📁 Project Structure

```
deposito-rekon-app/
│
├── 📱 APPLICATION LAYER
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # Main Streamlit application
│   │   ├── dashboard.py               # Dashboard components
│   │   └── ai_agent.py                # AI integration UI
│   │
├── 🏗️ MODEL LAYER
│   ├── models/
│   │   ├── __init__.py
│   │   ├── bank_base.py               # Abstract base class
│   │   ├── bank_btpn.py               # BTPN Syariah implementation
│   │   ├── bank_bps.py                # BPS implementation
│   │   ├── bank_mandiri.py            # Mandiri Syariah implementation
│   │   ├── bank_bni.py                # BNI Syariah implementation
│   │   └── deposito.py                # Data models
│   │
├── 🔧 SERVICE LAYER
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rekon_service.py           # Multi-bank reconciliation
│   │   ├── ai_service.py              # AI analysis service
│   │   ├── excel_service.py           # Excel import/export
│   │   ├── notification_service.py    # Email notifications
│   │   └── report_service.py          # Report generation
│   │
├── 🛠️ UTILITY LAYER
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py              # Data validation
│   │   ├── calculators.py             # Financial calculations
│   │   ├── date_utils.py              # Date operations
│   │   ├── formatters.py              # Data formatting
│   │   └── helpers.py                 # Helper functions
│   │
├── ⚙️ CONFIGURATION & DATA
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                  # Configuration management
│   │   ├── constants.py               # Application constants
│   │   ├── database.py                # Database operations
│   │   └── exceptions.py              # Custom exceptions
│   │
│   ├── data/
│   │   ├── banks/                     # Bank-specific configs
│   │   │   ├── btpn_syariah/
│   │   │   │   ├── config.json
│   │   │   │   └── mapping.json
│   │   │   ├── bps/
│   │   │   ├── mandiri_syariah/
│   │   │   └── bni_syariah/
│   │   ├── templates/                 # Excel templates
│   │   └── uploads/                   # Temporary uploads
│   │
├── 📚 DOCUMENTATION
│   ├── docs/
│   │   ├── USER_GUIDE.md              # User guide
│   │   ├── API.md                     # API documentation
│   │   ├── BANK_INTEGRATION.md        # Adding new banks
│   │   └── TROUBLESHOOTING.md         # Common issues
│   │
├── 🧪 TESTING
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_reconciliation.py
│   │   ├── test_calculators.py
│   │   └── test_validators.py
│   │
├── 🚀 DEPLOYMENT
│   ├── scripts/
│   │   ├── setup.py                   # Automated setup
│   │   ├── setup.sh                   # Linux/Mac setup
│   │   ├── setup.bat                  # Windows setup
│   │   ├── run.sh                     # Run script
│   │   ├── run.bat                    # Windows run
│   │   └── deploy.py                  # Deployment script
│   │
│   ├── Dockerfile                     # Docker image
│   ├── docker-compose.yml             # Multi-container
│   └── .github/workflows/ci.yml       # CI/CD pipeline
│
├── 📄 PROJECT FILES
│   ├── requirements.txt               # Python dependencies
│   ├── requirements-dev.txt           # Development dependencies
│   ├── .env.example                   # Environment template
│   ├── .gitignore                     # Git ignore rules
│   ├── .streamlit/config.toml         # Streamlit configuration
│   ├── README.md                      # This file
│   ├── CHANGELOG.md                   # Version history
│   └── LICENSE                        # MIT License
```

---

## 🏦 Adding New Bank

### Step-by-Step Guide

#### 1. Create Bank Model

Create `models/bank_newbank.py`:

```python
from models.bank_base import BankBase, BankConfig, DepositoRecord, DepositoType

class BankNewBank(BankBase):
    def __init__(self):
        config = BankConfig(
            bank_code="NEWBANK",
            bank_name="New Bank Name",
            column_mapping={
                'nomor_bilyet': 'Bilyet Number',  # Sesuaikan dengan Excel
                'nomor_rekening': 'Account Number',
                'nominal_deposito': 'Deposit Amount',
                'nominal_imbal_hasil': 'Profit Share'
            },
            nisbah_rates={
                'SA': 0.0450,  # 4.50%
                'SL': 0.0450,
                'NM': 0.0480
            },
            sheet_names={
                'detail': 'Detail Sheet'
            },
            year_days=360
        )
        super().__init__(config)
    
    def parse_bank_data(self, file_path: str) -> List[DepositoRecord]:
        # Implementation for parsing bank Excel
        records = []
        df = pd.read_excel(file_path)
        
        for _, row in df.iterrows():
            record = DepositoRecord(
                bank_code=self.bank_code,
                nomor_bilyet=str(row['Bilyet Number']),
                nomor_rekening=str(row['Account Number']),
                nominal_deposito=float(row['Deposit Amount']),
                nominal_imbal_hasil=float(row['Profit Share']),
                jenis_deposito=self._map_type(row['Type']),
                tanggal_penempatan=pd.to_datetime(row['Date']),
                source='bank'
            )
            records.append(record)
        
        return records
    
    def parse_bpkh_data(self, file_path: str) -> List[DepositoRecord]:
        # Implementation for parsing BPKH Excel
        # Similar structure
        pass
    
    def calculate_expected_imbal_hasil(self, record: DepositoRecord) -> float:
        nisbah = self.config.nisbah_rates.get(record.jenis_deposito.value, 0.045)
        return (record.nominal_deposito * nisbah * record.periode_hari) / 360
```

#### 2. Create Configuration

Create `data/banks/newbank/config.json`:

```json
{
  "bank_code": "NEWBANK",
  "bank_name": "New Bank Name",
  "column_mapping": {
    "nomor_bilyet": "Bilyet Number",
    "nomor_rekening": "Account Number",
    "nominal_deposito": "Deposit Amount",
    "nominal_imbal_hasil": "Profit Share"
  },
  "nisbah_rates": {
    "SA": 0.0450,
    "SL": 0.0450,
    "NM": 0.0480
  },
  "sheet_names": {
    "detail": "Detail Sheet"
  },
  "date_format": "%d/%m/%Y",
  "year_days": 360
}
```

#### 3. Register in Service

Edit `services/rekon_service.py`:

```python
from models.bank_newbank import BankNewBank

class MultiRekonService:
    def __init__(self):
        self.banks: Dict[str, BankBase] = {
            'BTPN': BankBTPN(),
            'BPS': BankBPS(),
            'MSI': BankMandiriSyariah(),
            'BNIS': BankBNISyariah(),
            'NEWBANK': BankNewBank()  # Add here
        }
```

#### 4. Test Implementation

```python
# Test the new bank
service = MultiRekonService()
result = service.process_reconciliation(
    'NEWBANK',
    'newbank_data.xlsx',
    'bpkh_data.xlsx'
)
print(result['summary'])
```

---

## 📚 API Documentation

### Core Classes

#### MultiRekonService

Main reconciliation orchestrator:

```python
from services.rekon_service import MultiRekonService

service = MultiRekonService()

# Single bank reconciliation
result = service.process_reconciliation(
    bank_code='BTPN',
    bank_file_path='btpn_bank.xlsx',
    bpkh_file_path='btpn_bpkh.xlsx'
)

# Multi-bank reconciliation
results = service.process_multiple_banks({
    'BTPN': ('btpn_bank.xlsx', 'btpn_bpkh.xlsx'),
    'BPS': ('bps_bank.xlsx', 'bps_bpkh.xlsx')
})

# Generate reports
summary = service.generate_summary_comparison(results)
consolidated = service.generate_consolidated_report(results)

# Export results
service.export_results(results, 'output.xlsx')
```

#### AIService

AI-powered analysis:

```python
from services.ai_service import AIService, AIConfig

config = AIConfig(
    openrouter_api_key="your-key",
    model="qwen/qwen-2.5-72b-instruct"
)

ai_service = AIService(config)

# Analyze reconciliation
analysis = ai_service.analyze_reconciliation(summary_data)

# Analyze specific variance
variance_analysis = ai_service.analyze_variance(variance_data)

# Generate recommendations
recommendations = ai_service.generate_recommendations(exception_items)
```

### Data Models

#### DepositoRecord

```python
@dataclass
class DepositoRecord:
    bank_code: str
    nomor_bilyet: str
    nomor_rekening: str
    nominal_deposito: float
    nominal_imbal_hasil: float
    jenis_deposito: DepositoType
    tanggal_penempatan: datetime
    periode_hari: Optional[int]
    source: str  # 'bank' or 'bpkh'
```

#### RekonResult

```python
@dataclass
class RekonResult:
    bank_code: str
    nomor_bilyet: str
    imbal_hasil_bank: float
    imbal_hasil_bpkh: float
    selisih: float
    persentase_selisih: float
    status: RekonStatus
    jenis_deposito: DepositoType
```

For complete API documentation, see: [docs/API.md](docs/API.md)

---

## 🔧 Troubleshooting

### Common Issues

#### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'models'`

**Solution**:
```bash
# Ensure running from project root
cd deposito-rekon-app

# Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run with module syntax
python -m streamlit run app/main.py
```

#### File Upload Errors

**Problem**: Excel file parsing fails

**Solutions**:
1. **Check column names**: Verify Excel headers match config.json exactly
2. **Check date format**: Ensure dates are in expected format
3. **Check encoding**: Save Excel as UTF-8 if special characters
4. **Check file size**: Max 50MB per file

```bash
# Debug Excel structure
python -c "
import pandas as pd
df = pd.read_excel('your_file.xlsx')
print('Columns:', df.columns.tolist())
print('Shape:', df.shape)
print('Sample:', df.head())
"
```

#### API Key Issues

**Problem**: AI analysis not working

**Solution**:
```bash
# Check .env file exists
cat .env

# Verify API key format
# OpenRouter: sk-or-v1-...
# Anthropic: sk-ant-...

# Test API connection
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen/qwen-2.5-72b-instruct","messages":[{"role":"user","content":"test"}]}'
```

#### Performance Issues

**Problem**: Slow processing for large files

**Solutions**:
```python
# Process in chunks
def process_large_file(file_path, chunk_size=1000):
    chunks = pd.read_excel(file_path, chunksize=chunk_size)
    results = []
    for chunk in chunks:
        chunk_result = process_chunk(chunk)
        results.extend(chunk_result)
    return results

# Use multiprocessing
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(process_bank, bank_code, files) 
               for bank_code, files in bank_files.items()]
    results = [f.result() for f in futures]
```

#### Memory Issues

**Problem**: `MemoryError` with large datasets

**Solutions**:
1. **Reduce file size**: Split by month/quarter
2. **Optimize pandas**: Use `dtype` optimization
3. **Clear cache**: `streamlit cache clear`
4. **Increase system memory**

```python
# Optimize memory usage
df = pd.read_excel(file_path, dtype={
    'nomor_bilyet': 'string',
    'nominal_deposito': 'float32',
    'nominal_imbal_hasil': 'float32'
})

# Clear cache periodically
import gc
gc.collect()
```

For more troubleshooting, see: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## 🧪 Testing

### Run Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=models --cov=services tests/

# Run specific test
pytest tests/test_reconciliation.py::test_btpn_parsing -v
```

### Test Structure

```bash
tests/
├── test_reconciliation.py      # Reconciliation logic tests
├── test_calculators.py         # Financial calculation tests
├── test_validators.py          # Data validation tests
├── test_ai_service.py          # AI service tests
└── fixtures/                   # Test data files
    ├── sample_btpn.xlsx
    ├── sample_bps.xlsx
    └── sample_bpkh.xlsx
```

### Example Test

```python
# tests/test_reconciliation.py
def test_btpn_reconciliation():
    from models.bank_btpn import BankBTPN
    
    bank = BankBTPN()
    
    # Test data parsing
    records = bank.parse_bank_data('tests/fixtures/sample_btpn.xlsx')
    assert len(records) > 0
    assert records[0].bank_code == 'BTPN'
    
    # Test reconciliation
    bank_records = [create_sample_record('bank')]
    bpkh_records = [create_sample_record('bpkh')]
    
    results = bank.reconcile(bank_records, bpkh_records)
    assert len(results) == 1
    assert results[0].status in [RekonStatus.MATCHED, RekonStatus.DIFFERENCE]
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Setup

```bash
# Fork repository
git clone https://github.com/your-username/deposito-rekon-app.git
cd deposito-rekon-app

# Create development branch
git checkout -b feature/your-feature-name

# Install dev dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Code Style

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy models/ services/

# Sort imports
isort .
```

### Pull Request Process

1. **Create Feature Branch**: `git checkout -b feature/amazing-feature`
2. **Make Changes**: Follow coding standards
3. **Add Tests**: Ensure good test coverage
4. **Update Docs**: Update README if needed
5. **Run Tests**: `pytest tests/`
6. **Submit PR**: With clear description

### Bank Implementation Contributions

To contribute a new bank implementation:

1. **Follow Template**: Use existing bank as template
2. **Add Tests**: Include test data and unit tests
3. **Update Config**: Add bank configuration
4. **Update Docs**: Add bank to supported list
5. **Test Thoroughly**: Test with real data

### Issue Reporting

Please include:
- **Environment**: OS, Python version, dependency versions
- **Steps to Reproduce**: Clear reproduction steps
- **Expected vs Actual**: What should happen vs what happens
- **Logs**: Relevant error messages/logs
- **Data**: Sample data (anonymized) if applicable

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 BPKH IT Department

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Support & Contact

### Technical Support

- 📧 **Email**: sopian@bpkh.go.id
- 💬 **Slack**: [#deposito-rekon](https://bpkh.slack.com/channels/deposito-rekon)
- 📚 **Documentation**: [docs/](docs/)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/bpkh/deposito-rekon-app/issues)

### Team

- **Project Lead**: MS Hadianto | Audit Committee Members of BPKH
- **Development**: MS Hadianto | Audit Committee Members of BPKH
- **Support**: Ari Supangat | Noviyansyah | Fauzan | Dewi | Lia

### Community

- 🌟 **Star** this repo if you find it useful
- 🐛 **Report issues** to help improve the system
- 💡 **Suggest features** for future development
- 🤝 **Contribute** code or documentation

---

## 🎉 Acknowledgments

- **BPKH** - For providing requirements and domain expertise
- **Bank Partners** - BTPN Syariah, BPS, Mandiri Syariah, BNI Syariah
- **Open Source Community** - Streamlit, Pandas, OpenAI, Anthropic
- **Contributors** - All developers who contributed to this project

---

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/bpkh/deposito-rekon-app?style=social)
![GitHub forks](https://img.shields.io/github/forks/bpkh/deposito-rekon-app?style=social)
![GitHub issues](https://img.shields.io/github/issues/bpkh/deposito-rekon-app)
![GitHub pull requests](https://img.shields.io/github/issues-pr/bpkh/deposito-rekon-app)

---

**Version**: 2.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: September 23, 2025  
**Maintained by**: MS Hadianto | Audit Committee Members of BPKH

---

<div align="center">

**Made with ❤️ for BPKH**

[⬆ Back to Top](#-multi-bank-deposito-reconciliation-system)

</div>
