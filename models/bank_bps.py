"""
BPS (Bank Pembangunan Syariah) Implementation
File: models/bank_bps.py
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from models.bank_base import (
    BankBase, BankConfig, DepositoRecord, 
    DepositoType, RekonResult
)


class BankBPS(BankBase):
    """Bank BPS Implementation"""
    
    def __init__(self):
        # Default config for BPS
        config = BankConfig(
            bank_code="BPS",
            bank_name="Bank Pembangunan Syariah",
            column_mapping={
                'nomor_bilyet': 'Nomor Bilyet',
                'nomor_rekening': 'Nomor Rekening',
                'nominal_deposito': 'Nominal Deposito',
                'nominal_imbal_hasil': 'Nominal Imbal Hasil',
                'jenis_deposito': 'Jenis Dana',
                'tanggal_penempatan': 'Tanggal Penempatan',
                'tanggal_cair': 'Tanggal Cair',
                'jadwal_imbal_hasil': 'Jadwal Imbal Hasil',
                'tanggal_imbal_hasil': 'Tanggal Imbal Hasil'
            },
            nisbah_rates={
                'SA': 0.0475,  # 4.75% untuk SA & SL
                'SL': 0.0475,
                'NM': 0.0500,  # 5.00% untuk NM
                'LPS': 0.0450  # 4.50% untuk LPS
            },
            sheet_names={
                'summary': 'Lampiran',
                'detail': 'Monitoring'
            },
            year_days=360
        )
        super().__init__(config)
    
    def parse_bank_data(self, file_path: str) -> List[DepositoRecord]:
        """Parse BPS bank data from Excel"""
        records = []
        
        # Read Excel file - BPS format berbeda dengan BTPN
        xl_file = pd.ExcelFile(file_path)
        
        # BPS biasanya punya sheet "Monitoring" atau "Detail"
        target_sheets = ['Monitoring', 'MONITORING KETEPATAN WAKTU REALISASI IMBAL HASIL', 'Detail', 'Data']
        
        for sheet_name in xl_file.sheet_names:
            # Check if this is a detail sheet
            if any(target in sheet_name.upper() for target in ['MONITORING', 'DETAIL', 'DATA']):
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Clean column names
                df.columns = df.columns.str.strip()
                
                # Find header row (biasanya ada kata "Sumber Dana" atau "Nomor Bilyet")
                header_row = None
                for idx, row in df.iterrows():
                    row_str = ' '.join(str(val) for val in row.values)
                    if any(keyword in row_str for keyword in ['Nomor Bilyet', 'Sumber Dana', 'No']):
                        header_row = idx
                        break
                
                if header_row is not None:
                    df.columns = df.iloc[header_row]
                    df = df.iloc[header_row + 1:].reset_index(drop=True)
                
                # Process each row
                for _, row in df.iterrows():
                    try:
                        # Skip rows without bilyet number
                        nomor_bilyet = str(row.get('Nomor Bilyet', '')).strip()
                        if not nomor_bilyet or nomor_bilyet in ['', 'nan', 'None']:
                            continue
                        
                        # Determine deposito type from "Sumber Dana" or "Jenis Dana"
                        sumber_dana = str(row.get('Sumber Dana', row.get('Jenis Dana', 'SA'))).strip().upper()
                        dep_type = self._map_deposito_type(sumber_dana)
                        
                        # Parse dates
                        tanggal_penempatan = self._parse_date(row.get('Tanggal Penempatan'))
                        tanggal_jatuh_tempo = self._parse_date(row.get('Tanggal Jatuh Tempo', row.get('Tanggal Cair')))
                        
                        # Calculate period
                        periode_hari = None
                        if tanggal_penempatan and tanggal_jatuh_tempo:
                            periode_hari = (tanggal_jatuh_tempo - tanggal_penempatan).days
                        
                        # Get nominal imbal hasil
                        # BPS might have different column names
                        nominal_imbal = self._parse_number(
                            row.get('Nominal Imbal Hasil', 
                                   row.get('Imbal Hasil',
                                          row.get('Jadwal Imbal Hasil', 0)))
                        )
                        
                        record = DepositoRecord(
                            bank_code=self.bank_code,
                            nomor_bilyet=nomor_bilyet,
                            nomor_rekening=str(row.get('Nomor Rekening', nomor_bilyet)).strip(),
                            nominal_deposito=self._parse_number(row.get('Nominal Deposito', 0)),
                            nominal_imbal_hasil=nominal_imbal,
                            jenis_deposito=dep_type,
                            tanggal_penempatan=tanggal_penempatan,
                            tanggal_jatuh_tempo=tanggal_jatuh_tempo,
                            periode_hari=periode_hari,
                            source='bank'
                        )
                        
                        records.append(record)
                    except Exception as e:
                        print(f"Error parsing BPS row: {e}")
                        continue
        
        return records
    
    def parse_bpkh_data(self, file_path: str) -> List[DepositoRecord]:
        """Parse BPKH data for BPS"""
        records = []
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Find header row
        header_row = None
        for idx, row in df.iterrows():
            row_str = ' '.join(str(val) for val in row.values)
            if 'Nomor Bilyet' in row_str or 'Nomor Rekening' in row_str:
                header_row = idx
                break
        
        if header_row is not None:
            df.columns = df.iloc[header_row]
            df = df.iloc[header_row + 1:].reset_index(drop=True)
        
        # Process each row
        for _, row in df.iterrows():
            try:
                nomor_bilyet = str(row.get('Nomor Bilyet', '')).strip()
                if not nomor_bilyet or nomor_bilyet in ['', 'nan', 'None']:
                    continue
                
                # Determine deposito type
                jenis = str(row.get('Jenis Deposito', row.get('Sumber Dana', 'SA'))).strip().upper()
                dep_type = self._map_deposito_type(jenis)
                
                # Parse dates
                tanggal_penempatan = self._parse_date(row.get('Tanggal Penempatan'))
                tanggal_realisasi = self._parse_date(
                    row.get('Tanggal Realisasi', 
                           row.get('Tanggal Imbal Hasil',
                                  row.get('Tanggal Cair')))
                )
                
                record = DepositoRecord(
                    bank_code=self.bank_code,
                    nomor_bilyet=nomor_bilyet,
                    nomor_rekening=str(row.get('Nomor Rekening', nomor_bilyet)).strip(),
                    nominal_deposito=self._parse_number(row.get('Nominal Deposito', 0)),
                    nominal_imbal_hasil=self._parse_number(row.get('Nominal Imbal Hasil', 0)),
                    jenis_deposito=dep_type,
                    tanggal_penempatan=tanggal_penempatan,
                    tanggal_realisasi=tanggal_realisasi,
                    source='bpkh'
                )
                
                records.append(record)
            except Exception as e:
                print(f"Error parsing BPKH row for BPS: {e}")
                continue
        
        return records
    
    def calculate_expected_imbal_hasil(self, record: DepositoRecord) -> float:
        """Calculate expected imbal hasil for BPS"""
        if not record.periode_hari or record.periode_hari <= 0:
            return 0
        
        # Get nisbah rate
        nisbah = self.config.nisbah_rates.get(
            record.jenis_deposito.value if isinstance(record.jenis_deposito, DepositoType) else record.jenis_deposito,
            0.0475  # default
        )
        
        # BPS menggunakan formula yang sama: (Pokok × Nisbah × Hari) / 360
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
            '%d %B %Y',
            '%d-%b-%y',
            '%d-%b-%Y'
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
        
        # Remove thousand separators
        value_str = str(value).replace('.', '').replace(',', '.')
        try:
            return float(value_str)
        except:
            return 0.0
    
    def _map_deposito_type(self, jenis_str: str) -> DepositoType:
        """Map string to DepositoType enum"""
        jenis_upper = jenis_str.upper().strip()
        
        # BPS specific mapping
        mapping = {
            'SA': DepositoType.SETORAN_AWAL,
            'SETORAN AWAL': DepositoType.SETORAN_AWAL,
            'SL': DepositoType.SETORAN_LUNAS,
            'SETORAN LUNAS': DepositoType.SETORAN_LUNAS,
            'NM': DepositoType.NILAI_MANFAAT,
            'NILAI MANFAAT': DepositoType.NILAI_MANFAAT,
            'LPS': DepositoType.LPS,
            'DAU': DepositoType.DAU,
            # Additional BPS specific
            'DANA SETORAN AWAL': DepositoType.SETORAN_AWAL,
            'DANA SETORAN LUNAS': DepositoType.SETORAN_LUNAS,
            'DANA NILAI MANFAAT': DepositoType.NILAI_MANFAAT
        }
        
        return mapping.get(jenis_upper, DepositoType.SETORAN_AWAL)