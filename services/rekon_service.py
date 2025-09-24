"""
Multi-Bank Reconciliation Service
File: services/rekon_service.py
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

from models.bank_base import BankBase, DepositoRecord, RekonResult
from models.bank_btpn import BankBTPN
from models.bank_bps import BankBPS


logger = logging.getLogger(__name__)


class MultiRekonService:
    """Service untuk handle rekonsiliasi multi-bank"""
    
    def __init__(self):
        self.banks: Dict[str, BankBase] = {
            'BTPN': BankBTPN(),
            'BPS': BankBPS()
            # Tambahkan bank lain di sini
        }
        self.results_cache: Dict[str, List[RekonResult]] = {}
    
    def add_bank(self, bank_code: str, bank_instance: BankBase):
        """Add new bank to the service"""
        self.banks[bank_code] = bank_instance
        logger.info(f"Added bank: {bank_code}")
    
    def get_available_banks(self) -> List[str]:
        """Get list of available banks"""
        return list(self.banks.keys())
    
    def process_reconciliation(
        self,
        bank_code: str,
        bank_file_path: str,
        bpkh_file_path: str
    ) -> Dict:
        """
        Process reconciliation for a specific bank
        
        Args:
            bank_code: Bank identifier (BTPN, BPS, etc.)
            bank_file_path: Path to bank Excel file
            bpkh_file_path: Path to BPKH Excel file
            
        Returns:
            Dictionary with reconciliation results and summary
        """
        try:
            # Get bank instance
            if bank_code not in self.banks:
                raise ValueError(f"Bank {bank_code} not supported")
            
            bank = self.banks[bank_code]
            
            logger.info(f"Starting reconciliation for {bank.bank_name}")
            
            # Parse bank data
            logger.info("Parsing bank data...")
            bank_records = bank.parse_bank_data(bank_file_path)
            logger.info(f"Loaded {len(bank_records)} records from bank")
            
            # Parse BPKH data
            logger.info("Parsing BPKH data...")
            bpkh_records = bank.parse_bpkh_data(bpkh_file_path)
            logger.info(f"Loaded {len(bpkh_records)} records from BPKH")
            
            # Perform reconciliation
            logger.info("Performing reconciliation...")
            rekon_results = bank.reconcile(bank_records, bpkh_records)
            logger.info(f"Generated {len(rekon_results)} reconciliation results")
            
            # Generate summary
            summary = bank.generate_summary(rekon_results)
            
            # Cache results
            self.results_cache[bank_code] = rekon_results
            
            # Convert to DataFrames
            df_results = bank.results_to_dataframe(rekon_results)
            
            return {
                'success': True,
                'bank_code': bank_code,
                'bank_name': bank.bank_name,
                'summary': summary,
                'results': rekon_results,
                'df_results': df_results,
                'bank_records_count': len(bank_records),
                'bpkh_records_count': len(bpkh_records),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in reconciliation for {bank_code}: {str(e)}")
            return {
                'success': False,
                'bank_code': bank_code,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def process_multiple_banks(
        self,
        bank_files: Dict[str, Tuple[str, str]]
    ) -> Dict[str, Dict]:
        """
        Process reconciliation for multiple banks
        
        Args:
            bank_files: Dict mapping bank_code to (bank_file, bpkh_file) tuple
            
        Returns:
            Dict mapping bank_code to reconciliation results
        """
        results = {}
        
        for bank_code, (bank_file, bpkh_file) in bank_files.items():
            logger.info(f"Processing {bank_code}...")
            result = self.process_reconciliation(bank_code, bank_file, bpkh_file)
            results[bank_code] = result
        
        return results
    
    def generate_consolidated_report(
        self,
        results: Dict[str, Dict]
    ) -> pd.DataFrame:
        """
        Generate consolidated report across all banks
        
        Args:
            results: Reconciliation results from multiple banks
            
        Returns:
            Consolidated DataFrame
        """
        all_dfs = []
        
        for bank_code, result in results.items():
            if result.get('success') and 'df_results' in result:
                all_dfs.append(result['df_results'])
        
        if all_dfs:
            consolidated = pd.concat(all_dfs, ignore_index=True)
            return consolidated
        else:
            return pd.DataFrame()
    
    def generate_summary_comparison(
        self,
        results: Dict[str, Dict]
    ) -> pd.DataFrame:
        """
        Generate summary comparison across banks
        
        Args:
            results: Reconciliation results from multiple banks
            
        Returns:
            Summary comparison DataFrame
        """
        summary_data = []
        
        for bank_code, result in results.items():
            if result.get('success') and 'summary' in result:
                summary = result['summary']
                summary_data.append({
                    'Bank': summary['bank_name'],
                    'Total Records': summary['total_records'],
                    'Matched': summary['matched_records'],
                    'Difference': summary['difference_records'],
                    'Match Rate (%)': round(summary['match_rate'], 2),
                    'Total Deposito': summary['total_deposito'],
                    'Total Bank': summary['total_imbal_hasil_bank'],
                    'Total BPKH': summary['total_imbal_hasil_bpkh'],
                    'Total Selisih': summary['total_selisih'],
                    'Selisih (%)': round(summary['pct_selisih'], 4)
                })
        
        return pd.DataFrame(summary_data)
    
    def get_exception_items(
        self,
        bank_code: str,
        threshold: float = 0.5
    ) -> pd.DataFrame:
        """
        Get exception items (variance > threshold) for a bank
        
        Args:
            bank_code: Bank identifier
            threshold: Variance threshold percentage
            
        Returns:
            DataFrame with exception items
        """
        if bank_code not in self.results_cache:
            return pd.DataFrame()
        
        results = self.results_cache[bank_code]
        bank = self.banks[bank_code]
        
        # Filter exception items
        exceptions = [
            r for r in results 
            if abs(r.persentase_selisih) > threshold
        ]
        
        if exceptions:
            return bank.results_to_dataframe(exceptions)
        else:
            return pd.DataFrame()
    
    def export_results(
        self,
        results: Dict[str, Dict],
        output_path: str
    ) -> bool:
        """
        Export reconciliation results to Excel
        
        Args:
            results: Reconciliation results
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Summary sheet
                summary_df = self.generate_summary_comparison(results)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Individual bank sheets
                for bank_code, result in results.items():
                    if result.get('success') and 'df_results' in result:
                        df = result['df_results']
                        sheet_name = f"{bank_code}_Detail"[:31]  # Excel sheet name limit
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Consolidated sheet
                consolidated = self.generate_consolidated_report(results)
                if not consolidated.empty:
                    consolidated.to_excel(writer, sheet_name='Consolidated', index=False)
            
            logger.info(f"Results exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting results: {str(e)}")
            return False
    
    def get_trend_analysis(
        self,
        bank_code: str,
        group_by: str = 'periode'
    ) -> pd.DataFrame:
        """
        Get trend analysis for a bank
        
        Args:
            bank_code: Bank identifier
            group_by: Group by field (periode, jenis_deposito, etc.)
            
        Returns:
            Trend analysis DataFrame
        """
        if bank_code not in self.results_cache:
            return pd.DataFrame()
        
        results = self.results_cache[bank_code]
        bank = self.banks[bank_code]
        
        # Convert to DataFrame
        df = bank.results_to_dataframe(results)
        
        # Group by specified field
        if group_by == 'periode':
            grouped = df.groupby('Periode').agg({
                'Selisih': ['sum', 'mean', 'count'],
                'Selisih (%)': 'mean'
            }).round(2)
        elif group_by == 'jenis_deposito':
            grouped = df.groupby('Jenis Deposito').agg({
                'Selisih': ['sum', 'mean', 'count'],
                'Selisih (%)': 'mean'
            }).round(2)
        else:
            grouped = df.groupby('Status').agg({
                'Selisih': ['sum', 'mean', 'count'],
                'Selisih (%)': 'mean'
            }).round(2)
        
        return grouped
    
    def calculate_kpis(self, results: Dict[str, Dict]) -> Dict:
        """
        Calculate KPIs across all banks
        
        Args:
            results: Reconciliation results
            
        Returns:
            KPI metrics dictionary
        """
        total_records = 0
        total_matched = 0
        total_selisih = 0
        total_bank = 0
        
        for result in results.values():
            if result.get('success') and 'summary' in result:
                summary = result['summary']
                total_records += summary['total_records']
                total_matched += summary['matched_records']
                total_selisih += summary['total_selisih']
                total_bank += summary['total_imbal_hasil_bank']
        
        match_rate = (total_matched / total_records * 100) if total_records > 0 else 0
        variance_rate = abs(total_selisih / total_bank * 100) if total_bank > 0 else 0
        
        # Calculate scores
        accuracy_score = match_rate
        quality_score = max(0, 100 - variance_rate * 100)
        overall_score = (accuracy_score * 0.6 + quality_score * 0.4)
        
        return {
            'total_records': total_records,
            'total_matched': total_matched,
            'match_rate': round(match_rate, 2),
            'total_selisih': total_selisih,
            'variance_rate': round(variance_rate, 4),
            'accuracy_score': round(accuracy_score, 2),
            'quality_score': round(quality_score, 2),
            'overall_score': round(overall_score, 2),
            'status': 'Excellent' if overall_score >= 95 else 
                     'Good' if overall_score >= 85 else 
                     'Fair' if overall_score >= 70 else 'Poor'
        }