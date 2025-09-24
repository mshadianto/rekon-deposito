"""
BTPN Syariah Bank Implementation
File: models/bank_btpn.py
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from models.bank_base import (
    BankBase, BankConfig, DepositoRecord, 
    DepositoType, RekonResult
)


class BankBTPN(BankBase):
    """Bank BTPN Syariah Implementation"""
    
    def __init__(self):
        # Default config for BTPN Syariah
        config = BankConfig(
            bank_code="BTPN",
            bank_name="Bank BTPN Syariah",
            column_mapping={
                'nomor_bilyet': 'Nomor Bilyet',
                'nomor_rekening': 'Nomor Rekening',
                'nominal_deposito': 'Nominal Deposito',
                'nominal_imbal_hasil': 'Nominal Imbal Hasil',
                'jenis_deposito': 'Jenis Deposito',
                'tanggal_penempatan': 'Tanggal Penempatan',
                'tanggal_jatuh_tempo': 'Tanggal Jatuh Tempo',
                'nisbah_rate': 'Nisbah Rate'
            },
            nisbah_rates={
                'SA': 0.0930,  # 9.30% untuk Setoran Awal (Apr-May 2025)
                'SL': 0.0930,  # 9.30% untuk Setoran Lunas
                'NM': 0.0835,  # 8.35% untuk Nilai Manfaat
                'LPS': 0.0450  # 4.50% untuk LPS
            },
            sheet_names={
                'setoran_awal': 'Setoran Awal',
                'setoran_lunas': 'Setoran Lunas',
                'nilai_manfaat': 'Nilai Manfaat'
            },
            year_days=360  # Islamic calendar basis
        )
        super().__init__(config)
    
    def parse_bank_data(self, file_path: str) -> List[DepositoRecord]:
        """Parse BTPN bank data from Excel"""
        records = []
        
        # Read Excel file
        xl_file = pd.ExcelFile(file_path)
        
        # Parse each deposito type
        deposito_types = {
            'Setoran Awal': DepositoType.SETORAN_AWAL,
            'Setoran Lunas': DepositoType.SETORAN_LUNAS,
            'Nilai Manfaat': DepositoType.NILAI_MANFAAT
        }
        
        for sheet_name, dep_type in deposito_types.items():
            if sheet_name in xl_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Clean column names
                df.columns = df.columns.str.strip()
                
                # Skip header rows if needed
                # Find the row with "Nomor Bilyet" or similar header
                header_row = None
                for idx, row in df.iterrows():
                    if any('Nomor Bilyet' in str(val) for val in row.values):
                        header_row = idx
                        break
                
                if header_row is not None:
                    df.columns = df.iloc[header_row]
                    df = df.iloc[header_row + 1:].reset_index(drop=True)
                
                # Process each row
                for _, row in df.iterrows():
                    try:
                        # Skip empty rows
                        if pd.isna(row.get('Nomor Bilyet')) or pd.isna(row.get('Nomor Rekening')):
                            continue
                        
                        # Parse dates
                        tanggal_penempatan = self._parse_date(row.get('Tanggal Penempatan'))
                        tanggal_jatuh_tempo = self._parse_date(row.get('Tanggal Jatuh Tempo'))
                        
                        # Calculate period days
                        periode_hari = None
                        if tanggal_penempatan and tanggal_jatuh_tempo:
                            periode_hari = (tanggal_jatuh_tempo - tanggal_penempatan).days
                        
                        record = DepositoRecord(
                            bank_code=self.bank_code,
                            nomor_bilyet=str(row.get('Nomor Bilyet', '')).strip(),
                            nomor_rekening=str(row.get('Nomor Rekening', '')).strip(),
                            nominal_deposito=self._parse_number(row.get('Nominal Deposito', 0)),
                            nominal_imbal_hasil=self._parse_number(row.get('Nominal Imbal Hasil', 0)),
                            jenis_deposito=dep_type,
                            tanggal_penempatan=tanggal_penempatan,
                            tanggal_jatuh_tempo=tanggal_jatuh_tempo,
                            nisbah_rate=self._parse_number(row.get('Nisbah Rate', self.config.nisbah_rates.get(dep_type.value, 0))),
                            periode_hari=periode_hari,
                            source='bank'
                        )
                        
                        records.append(record)
                    except Exception as e:
                        print(f"Error parsing row in {sheet_name}: {e}")
                        continue
        
        return records
    
    def parse_bpkh_data(self, file_path: str) -> List[DepositoRecord]:
        """Parse BPKH data from Excel"""
        records = []
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Find header row
        header_row = None
        for idx, row in df.iterrows():
            if any('Nomor Bilyet' in str(val) or 'Nomor Rekening' in str(val) for val in row.values):
                header_row = idx
                break
        
        if header_row is not None:
            df.columns = df.iloc[header_row]
            df = df.iloc[header_row + 1:].reset_index(drop=True)
        
        # Process each row
        for _, row in df.iterrows():
            try:
                # Skip empty rows
                if pd.isna(row.get('Nomor Bilyet')) or pd.isna(row.get('Nomor Rekening')):
                    continue
                
                # Determine deposito type
                jenis = str(row.get('Jenis Deposito', 'SA')).strip().upper()
                dep_type = self._map_deposito_type(jenis)
                
                # Parse dates
                tanggal_penempatan = self._parse_date(row.get('Tanggal Penempatan'))
                tanggal_realisasi = self._parse_date(row.get('Tanggal Realisasi') or row.get('Tanggal Cair'))
                
                record = DepositoRecord(
                    bank_code=self.bank_code,
                    nomor_bilyet=str(row.get('Nomor Bilyet', '')).strip(),
                    nomor_rekening=str(row.get('Nomor Rekening', '')).strip(),
                    nominal_deposito=self._parse_number(row.get('Nominal Deposito', 0)),
                    nominal_imbal_hasil=self._parse_number(row.get('Nominal Imbal Hasil', 0)),
                    jenis_deposito=dep_type,
                    tanggal_penempatan=tanggal_penempatan,
                    tanggal_realisasi=tanggal_realisasi,
                    source='bpkh'
                )
                
                records.append(record)
            except Exception as e:
                print(f"Error parsing BPKH row: {e}")
                continue
        
        return records
    
    def calculate_expected_imbal_hasil(self, record: DepositoRecord) -> float:
        """Calculate expected imbal hasil based on nisbah"""
        if not record.periode_hari or record.periode_hari <= 0:
            return 0
        
        # Get nisbah rate for this deposito type
        nisbah = record.nisbah_rate or self.config.nisbah_rates.get(
            record.jenis_deposito.value if isinstance(record.jenis_deposito, DepositoType) else record.jenis_deposito,
            0.09  # default 9%
        )
        
        # Calculate: (Pokok × Nisbah × Hari) / 360
        expected = (record.nominal_deposito * nisbah * record.periode_hari) / self.config.year_days
        
        return round(expected, 2)
    
    def _parse_date(self, date_value) -> Optional[datetime]:
        """Parse date from various formats"""
        if pd.isna(date_value):
            return None
        
        if isinstance(date_value, datetime):
            return date_value
        
        # Try common date formats
        formats = [
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y-%m-%d',
            '%d %b %Y',
            '%d %B %Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(date_value), fmt)
            except:
                continue
        
        return None
    
    def _parse_number(self, value) -> float:
        """Parse number from string or numeric value"""
        if pd.isna(value):
            return 0.0
        
        if isinstance(value, (int, float)):
            return float(value)
        
        # Remove thousand separators and convert
        value_str = str(value).replace('.', '').replace(',', '.')
        try:
            return float(value_str)
        except:
            return 0.0
    
    def _map_deposito_type(self, jenis_str: str) -> DepositoType:
        """Map string to DepositoType enum"""
        jenis_upper = jenis_str.upper().strip()
        
        mapping = {
            'SA': DepositoType.SETORAN_AWAL,
            'SETORAN AWAL': DepositoType.SETORAN_AWAL,
            'SL': DepositoType.SETORAN_LUNAS,
            'SETORAN LUNAS': DepositoType.SETORAN_LUNAS,
            'NM': DepositoType.NILAI_MANFAAT,
            'NILAI MANFAAT': DepositoType.NILAI_MANFAAT,
            'LPS': DepositoType.LPS,
            'DAU': DepositoType.DAU
        }
        
        return mapping.get(jenis_upper, DepositoType.SETORAN_AWAL)