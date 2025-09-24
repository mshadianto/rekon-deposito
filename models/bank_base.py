"""
Base Model untuk semua Bank - Abstract Class
File: models/bank_base.py
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd
from enum import Enum


class DepositoType(Enum):
    """Enum untuk jenis deposito"""
    SETORAN_AWAL = "SA"
    SETORAN_LUNAS = "SL"
    NILAI_MANFAAT = "NM"
    LPS = "LPS"
    DAU = "DAU"


class RekonStatus(Enum):
    """Status rekonsiliasi"""
    MATCHED = "Matched"
    DIFFERENCE = "Difference"
    NOT_FOUND_BANK = "Not Found in Bank"
    NOT_FOUND_BPKH = "Not Found in BPKH"
    PENDING = "Pending"


@dataclass
class BankConfig:
    """Konfigurasi untuk setiap bank"""
    bank_code: str
    bank_name: str
    column_mapping: Dict[str, str]
    nisbah_rates: Dict[str, float]
    sheet_names: Dict[str, str]
    date_format: str = "%d/%m/%Y"
    decimal_separator: str = ","
    thousand_separator: str = "."
    year_days: int = 360  # 360 untuk syariah
    
    @classmethod
    def from_json(cls, config_path: str):
        """Load config dari JSON file"""
        import json
        with open(config_path, 'r') as f:
            data = json.load(f)
        return cls(**data)


@dataclass
class DepositoRecord:
    """Model untuk single deposito record"""
    bank_code: str
    nomor_bilyet: str
    nomor_rekening: str
    nominal_deposito: float
    nominal_imbal_hasil: float
    jenis_deposito: DepositoType
    tanggal_penempatan: datetime
    tanggal_jatuh_tempo: Optional[datetime] = None
    tanggal_realisasi: Optional[datetime] = None
    nisbah_rate: Optional[float] = None
    periode_hari: Optional[int] = None
    source: str = "bank"  # "bank" or "bpkh"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'bank_code': self.bank_code,
            'nomor_bilyet': self.nomor_bilyet,
            'nomor_rekening': self.nomor_rekening,
            'nominal_deposito': self.nominal_deposito,
            'nominal_imbal_hasil': self.nominal_imbal_hasil,
            'jenis_deposito': self.jenis_deposito.value if isinstance(self.jenis_deposito, DepositoType) else self.jenis_deposito,
            'tanggal_penempatan': self.tanggal_penempatan.strftime('%Y-%m-%d') if self.tanggal_penempatan else None,
            'tanggal_jatuh_tempo': self.tanggal_jatuh_tempo.strftime('%Y-%m-%d') if self.tanggal_jatuh_tempo else None,
            'tanggal_realisasi': self.tanggal_realisasi.strftime('%Y-%m-%d') if self.tanggal_realisasi else None,
            'nisbah_rate': self.nisbah_rate,
            'periode_hari': self.periode_hari,
            'source': self.source
        }


@dataclass
class RekonResult:
    """Model untuk hasil rekonsiliasi"""
    bank_code: str
    nomor_bilyet: str
    nomor_rekening: str
    nominal_deposito: float
    imbal_hasil_bank: float
    imbal_hasil_bpkh: float
    selisih: float
    persentase_selisih: float
    status: RekonStatus
    jenis_deposito: DepositoType
    periode: str
    notes: Optional[str] = None
    
    def is_material(self, threshold: float = 0.5) -> bool:
        """Check if variance is material"""
        return abs(self.persentase_selisih) > threshold
    
    def get_priority(self) -> str:
        """Get priority based on variance"""
        abs_pct = abs(self.persentase_selisih)
        if abs_pct < 0.1:
            return "Low"
        elif abs_pct < 0.5:
            return "Medium"
        elif abs_pct < 1.0:
            return "High"
        else:
            return "Critical"


class BankBase(ABC):
    """
    Abstract Base Class untuk semua bank
    Setiap bank harus implement class ini
    """
    
    def __init__(self, config: BankConfig):
        self.config = config
        self.bank_code = config.bank_code
        self.bank_name = config.bank_name
    
    @abstractmethod
    def parse_bank_data(self, file_path: str) -> List[DepositoRecord]:
        """
        Parse data dari file bank
        
        Args:
            file_path: Path ke file Excel bank
            
        Returns:
            List of DepositoRecord
        """
        pass
    
    @abstractmethod
    def parse_bpkh_data(self, file_path: str) -> List[DepositoRecord]:
        """
        Parse data dari file BPKH
        
        Args:
            file_path: Path ke file Excel BPKH
            
        Returns:
            List of DepositoRecord
        """
        pass
    
    @abstractmethod
    def calculate_expected_imbal_hasil(self, record: DepositoRecord) -> float:
        """
        Hitung expected imbal hasil berdasarkan nisbah
        
        Args:
            record: DepositoRecord
            
        Returns:
            Expected imbal hasil
        """
        pass
    
    def reconcile(
        self, 
        bank_records: List[DepositoRecord], 
        bpkh_records: List[DepositoRecord]
    ) -> List[RekonResult]:
        """
        Perform reconciliation between bank and BPKH data
        
        Args:
            bank_records: List of records from bank
            bpkh_records: List of records from BPKH
            
        Returns:
            List of RekonResult
        """
        results = []
        
        # Create lookup dictionary for BPKH records
        bpkh_lookup = {
            (rec.nomor_bilyet, rec.nomor_rekening): rec 
            for rec in bpkh_records
        }
        
        # Match bank records with BPKH
        for bank_rec in bank_records:
            key = (bank_rec.nomor_bilyet, bank_rec.nomor_rekening)
            
            if key in bpkh_lookup:
                bpkh_rec = bpkh_lookup[key]
                selisih = bank_rec.nominal_imbal_hasil - bpkh_rec.nominal_imbal_hasil
                pct_selisih = (selisih / bank_rec.nominal_imbal_hasil * 100) if bank_rec.nominal_imbal_hasil != 0 else 0
                
                status = RekonStatus.MATCHED if abs(selisih) < 1 else RekonStatus.DIFFERENCE
                
                result = RekonResult(
                    bank_code=self.bank_code,
                    nomor_bilyet=bank_rec.nomor_bilyet,
                    nomor_rekening=bank_rec.nomor_rekening,
                    nominal_deposito=bank_rec.nominal_deposito,
                    imbal_hasil_bank=bank_rec.nominal_imbal_hasil,
                    imbal_hasil_bpkh=bpkh_rec.nominal_imbal_hasil,
                    selisih=selisih,
                    persentase_selisih=pct_selisih,
                    status=status,
                    jenis_deposito=bank_rec.jenis_deposito,
                    periode=bank_rec.tanggal_penempatan.strftime('%b-%y') if bank_rec.tanggal_penempatan else "N/A"
                )
                
                results.append(result)
                
                # Remove from lookup to track unmatched BPKH records
                del bpkh_lookup[key]
            else:
                # Bank record not found in BPKH
                result = RekonResult(
                    bank_code=self.bank_code,
                    nomor_bilyet=bank_rec.nomor_bilyet,
                    nomor_rekening=bank_rec.nomor_rekening,
                    nominal_deposito=bank_rec.nominal_deposito,
                    imbal_hasil_bank=bank_rec.nominal_imbal_hasil,
                    imbal_hasil_bpkh=0,
                    selisih=bank_rec.nominal_imbal_hasil,
                    persentase_selisih=100,
                    status=RekonStatus.NOT_FOUND_BPKH,
                    jenis_deposito=bank_rec.jenis_deposito,
                    periode=bank_rec.tanggal_penempatan.strftime('%b-%y') if bank_rec.tanggal_penempatan else "N/A",
                    notes="Record not found in BPKH data"
                )
                results.append(result)
        
        # Add remaining BPKH records (not found in bank)
        for bpkh_rec in bpkh_lookup.values():
            result = RekonResult(
                bank_code=self.bank_code,
                nomor_bilyet=bpkh_rec.nomor_bilyet,
                nomor_rekening=bpkh_rec.nomor_rekening,
                nominal_deposito=bpkh_rec.nominal_deposito,
                imbal_hasil_bank=0,
                imbal_hasil_bpkh=bpkh_rec.nominal_imbal_hasil,
                selisih=-bpkh_rec.nominal_imbal_hasil,
                persentase_selisih=-100,
                status=RekonStatus.NOT_FOUND_BANK,
                jenis_deposito=bpkh_rec.jenis_deposito,
                periode=bpkh_rec.tanggal_penempatan.strftime('%b-%y') if bpkh_rec.tanggal_penempatan else "N/A",
                notes="Record not found in Bank data"
            )
            results.append(result)
        
        return results
    
    def generate_summary(self, rekon_results: List[RekonResult]) -> Dict:
        """
        Generate summary statistics from reconciliation results
        
        Args:
            rekon_results: List of RekonResult
            
        Returns:
            Summary dictionary
        """
        total_records = len(rekon_results)
        matched_records = len([r for r in rekon_results if r.status == RekonStatus.MATCHED])
        diff_records = len([r for r in rekon_results if r.status == RekonStatus.DIFFERENCE])
        
        total_deposito = sum(r.nominal_deposito for r in rekon_results)
        total_bank = sum(r.imbal_hasil_bank for r in rekon_results)
        total_bpkh = sum(r.imbal_hasil_bpkh for r in rekon_results)
        total_selisih = sum(r.selisih for r in rekon_results)
        
        # Group by deposito type
        by_type = {}
        for dep_type in DepositoType:
            type_results = [r for r in rekon_results if r.jenis_deposito == dep_type]
            if type_results:
                by_type[dep_type.value] = {
                    'count': len(type_results),
                    'total_deposito': sum(r.nominal_deposito for r in type_results),
                    'total_bank': sum(r.imbal_hasil_bank for r in type_results),
                    'total_bpkh': sum(r.imbal_hasil_bpkh for r in type_results),
                    'selisih': sum(r.selisih for r in type_results)
                }
        
        return {
            'bank_code': self.bank_code,
            'bank_name': self.bank_name,
            'total_records': total_records,
            'matched_records': matched_records,
            'difference_records': diff_records,
            'match_rate': (matched_records / total_records * 100) if total_records > 0 else 0,
            'total_deposito': total_deposito,
            'total_imbal_hasil_bank': total_bank,
            'total_imbal_hasil_bpkh': total_bpkh,
            'total_selisih': total_selisih,
            'pct_selisih': (total_selisih / total_bank * 100) if total_bank != 0 else 0,
            'by_type': by_type,
            'timestamp': datetime.now().isoformat()
        }
    
    def to_dataframe(self, records: List[DepositoRecord]) -> pd.DataFrame:
        """Convert list of records to DataFrame"""
        return pd.DataFrame([rec.to_dict() for rec in records])
    
    def results_to_dataframe(self, results: List[RekonResult]) -> pd.DataFrame:
        """Convert reconciliation results to DataFrame"""
        data = []
        for result in results:
            data.append({
                'Bank': self.bank_name,
                'Nomor Bilyet': result.nomor_bilyet,
                'Nomor Rekening': result.nomor_rekening,
                'Jenis Deposito': result.jenis_deposito.value if isinstance(result.jenis_deposito, DepositoType) else result.jenis_deposito,
                'Nominal Deposito': result.nominal_deposito,
                'Imbal Hasil Bank': result.imbal_hasil_bank,
                'Imbal Hasil BPKH': result.imbal_hasil_bpkh,
                'Selisih': result.selisih,
                'Selisih (%)': result.persentase_selisih,
                'Status': result.status.value if isinstance(result.status, RekonStatus) else result.status,
                'Priority': result.get_priority(),
                'Periode': result.periode,
                'Notes': result.notes or ''
            })
        
        return pd.DataFrame(data)
    
    @staticmethod
    def load_config(bank_code: str) -> BankConfig:
        """Load bank configuration from JSON file"""
        import json
        import os
        
        config_path = f"data/banks/{bank_code}/config.json"
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        return BankConfig(**config_data)