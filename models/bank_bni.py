# ============================================
# File: models/bank_bni.py
# ============================================

class BankBNISyariah(BankBase):
    """BNI Syariah Implementation"""
    
    def __init__(self):
        config = BankConfig(
            bank_code="BNIS",
            bank_name="BNI Syariah",
            column_mapping={
                'nomor_bilyet': 'Nomor Bilyet',
                'nomor_rekening': 'Nomor Rekening',
                'nominal_deposito': 'Pokok Deposito',
                'nominal_imbal_hasil': 'Bagi Hasil',
                'jenis_deposito': 'Tipe Deposito',
                'tanggal_penempatan': 'Tanggal Mulai',
                'tanggal_jatuh_tempo': 'Tanggal Berakhir'
            },
            nisbah_rates={
                'SA': 0.0485,
                'SL': 0.0485,
                'NM': 0.0515,
                'LPS': 0.0450
            },
            sheet_names={
                'summary': 'Summary',
                'detail': 'Detail Deposito'
            },
            date_format='%d/%m/%Y',
            year_days=360
        )
        super().__init__(config)
    
    def parse_bank_data(self, file_path: str) -> List[DepositoRecord]:
        """Parse BNI bank data"""
        records = []
        
        sheet_name = self.config.sheet_names.get('detail', 'Detail Deposito')
        
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        except:
            df = pd.read_excel(file_path)
        
        df.columns = df.columns.str.strip()
        
        for _, row in df.iterrows():
            try:
                nomor_bilyet = str(row.get('Nomor Bilyet', '')).strip()
                if not nomor_bilyet or nomor_bilyet == 'nan':
                    continue
                
                tanggal_penempatan = self._parse_date(row.get('Tanggal Mulai', row.get('Tanggal Penempatan')))
                tanggal_jatuh_tempo = self._parse_date(row.get('Tanggal Berakhir', row.get('Tanggal Jatuh Tempo')))
                
                periode_hari = None
                if tanggal_penempatan and tanggal_jatuh_tempo:
                    periode_hari = (tanggal_jatuh_tempo - tanggal_penempatan).days
                
                jenis = str(row.get('Tipe Deposito', row.get('Jenis Deposito', 'SA'))).strip().upper()
                dep_type = self._map_deposito_type(jenis)
                
                record = DepositoRecord(
                    bank_code=self.bank_code,
                    nomor_bilyet=nomor_bilyet,
                    nomor_rekening=str(row.get('Nomor Rekening', '')).strip(),
                    nominal_deposito=self._parse_number(row.get('Pokok Deposito', row.get('Nominal Deposito', 0))),
                    nominal_imbal_hasil=self._parse_number(row.get('Bagi Hasil', row.get('Nominal Imbal Hasil', 0))),
                    jenis_deposito=dep_type,
                    tanggal_penempatan=tanggal_penempatan,
                    tanggal_jatuh_tempo=tanggal_jatuh_tempo,
                    periode_hari=periode_hari,
                    source='bank'
                )
                
                records.append(record)
                
            except Exception as e:
                print(f"Error parsing BNI row: {e}")
                continue
        
        return records
    
    def parse_bpkh_data(self, file_path: str) -> List[DepositoRecord]:
        """Parse BPKH data for BNI"""
        records = []
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.strip()
        
        for _, row in df.iterrows():
            try:
                nomor_bilyet = str(row.get('Nomor Bilyet', '')).strip()
                if not nomor_bilyet or nomor_bilyet == 'nan':
                    continue
                
                jenis = str(row.get('Jenis Deposito', 'SA')).strip().upper()
                dep_type = self._map_deposito_type(jenis)
                
                record = DepositoRecord(
                    bank_code=self.bank_code,
                    nomor_bilyet=nomor_bilyet,
                    nomor_rekening=str(row.get('Nomor Rekening', '')).strip(),
                    nominal_deposito=self._parse_number(row.get('Nominal Deposito', 0)),
                    nominal_imbal_hasil=self._parse_number(row.get('Nominal Imbal Hasil', 0)),
                    jenis_deposito=dep_type,
                    tanggal_penempatan=self._parse_date(row.get('Tanggal Penempatan')),
                    tanggal_realisasi=self._parse_date(row.get('Tanggal Realisasi')),
                    source='bpkh'
                )
                
                records.append(record)
                
            except Exception as e:
                print(f"Error parsing BPKH row for BNI: {e}")
                continue
        
        return records
    
    def calculate_expected_imbal_hasil(self, record: DepositoRecord) -> float:
        """Calculate expected imbal hasil"""
        if not record.periode_hari or record.periode_hari <= 0:
            return 0
        
        nisbah = self.config.nisbah_rates.get(
            record.jenis_deposito.value if isinstance(record.jenis_deposito, DepositoType) else record.jenis_deposito,
            0.0485
        )
        
        return (record.nominal_deposito * nisbah * record.periode_hari) / self.config.year_days
    
    def _parse_date(self, date_value) -> Optional[datetime]:
        """Parse date"""
        if pd.isna(date_value):
            return None
        if isinstance(date_value, datetime):
            return date_value
        
        formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d %b %Y']
        for fmt in formats:
            try:
                return datetime.strptime(str(date_value), fmt)
            except:
                continue
        return None
    
    def _parse_number(self, value) -> float:
        """Parse number"""
        if pd.isna(value):
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        value_str = str(value).replace('.', '').replace(',', '.')
        try:
            return float(value_str)
        except:
            return 0.0
    
    def _map_deposito_type(self, jenis_str: str) -> DepositoType:
        """Map to DepositoType"""
        mapping = {
            'SA': DepositoType.SETORAN_AWAL,
            'SL': DepositoType.SETORAN_LUNAS,
            'NM': DepositoType.NILAI_MANFAAT,
            'LPS': DepositoType.LPS
        }
        return mapping.get(jenis_str.upper(), DepositoType.SETORAN_AWAL)