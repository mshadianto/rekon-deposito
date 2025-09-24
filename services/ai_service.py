"""
AI Analysis Service - OpenRouter & Anthropic Integration
File: services/ai_service.py
"""

import requests
import json
import time
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AIConfig:
    """Configuration for AI services"""
    openrouter_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    model: str = "qwen/qwen-2.5-72b-instruct"
    temperature: float = 0.7
    max_tokens: int = 2000
    max_retries: int = 3
    retry_delay: int = 2


class AIService:
    """Service for AI-powered analysis"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        self.anthropic_url = "https://api.anthropic.com/v1/messages"
    
    def analyze_reconciliation(
        self,
        summary_data: Dict,
        use_anthropic: bool = False
    ) -> str:
        """
        Analyze reconciliation results using AI
        
        Args:
            summary_data: Reconciliation summary data
            use_anthropic: Use Anthropic API instead of OpenRouter
            
        Returns:
            AI analysis text
        """
        prompt = self._build_reconciliation_prompt(summary_data)
        
        if use_anthropic and self.config.anthropic_api_key:
            return self._call_anthropic(prompt)
        else:
            return self._call_openrouter(prompt)
    
    def analyze_variance(
        self,
        variance_data: Dict,
        context: Optional[str] = None
    ) -> str:
        """
        Analyze specific variance issues
        
        Args:
            variance_data: Variance details
            context: Additional context
            
        Returns:
            Analysis text
        """
        prompt = self._build_variance_prompt(variance_data, context)
        return self._call_openrouter(prompt)
    
    def generate_recommendations(
        self,
        exception_items: List[Dict],
        historical_data: Optional[Dict] = None
    ) -> str:
        """
        Generate recommendations for exception items
        
        Args:
            exception_items: List of exception items
            historical_data: Historical data for context
            
        Returns:
            Recommendations text
        """
        prompt = self._build_recommendation_prompt(exception_items, historical_data)
        return self._call_openrouter(prompt)
    
    def _build_reconciliation_prompt(self, summary_data: Dict) -> str:
        """Build prompt for reconciliation analysis"""
        
        breakdown_text = ""
        if 'by_type' in summary_data:
            for dep_type, data in summary_data['by_type'].items():
                breakdown_text += f"\n  {dep_type}:"
                breakdown_text += f"\n    - Total Deposito: Rp {data.get('total_deposito', 0):,.2f}"
                breakdown_text += f"\n    - Imbal Hasil Bank: Rp {data.get('total_bank', 0):,.2f}"
                breakdown_text += f"\n    - Imbal Hasil BPKH: Rp {data.get('total_bpkh', 0):,.2f}"
                breakdown_text += f"\n    - Selisih: Rp {data.get('selisih', 0):,.2f}"
        
        prompt = f"""Anda adalah AI Expert dalam rekonsiliasi keuangan untuk Bank Syariah dan BPKH (Badan Pengelola Keuangan Haji).

DATA REKONSILIASI:
==================
Bank: {summary_data.get('bank_name', 'N/A')}
Periode: {summary_data.get('timestamp', 'N/A')}

RINGKASAN:
- Total Records: {summary_data.get('total_records', 0):,}
- Records Matched: {summary_data.get('matched_records', 0):,} ({summary_data.get('match_rate', 0):.2f}%)
- Records Difference: {summary_data.get('difference_records', 0):,}

FINANSIAL:
- Total Deposito: Rp {summary_data.get('total_deposito', 0):,.2f}
- Total Imbal Hasil Bank: Rp {summary_data.get('total_imbal_hasil_bank', 0):,.2f}
- Total Imbal Hasil BPKH: Rp {summary_data.get('total_imbal_hasil_bpkh', 0):,.2f}
- Total Selisih: Rp {summary_data.get('total_selisih', 0):,.2f}
- Persentase Selisih: {summary_data.get('pct_selisih', 0):.4f}%

BREAKDOWN PER JENIS DEPOSITO:
{breakdown_text}

TUGAS ANDA:
===========
Berikan analisis komprehensif dalam format berikut:

1. EXECUTIVE SUMMARY (2-3 kalimat)
   - Status keseluruhan rekonsiliasi
   - Key findings utama

2. ROOT CAUSE ANALYSIS
   - Identifikasi kemungkinan penyebab selisih
   - Analisis per jenis deposito (SA, SL, NM)
   - Pola atau trend yang teridentifikasi
   - Faktor teknis vs sistemik

3. MATERIALITAS ASSESSMENT
   - Apakah selisih material atau tidak material?
   - Threshold yang digunakan (gunakan 0.5% sebagai benchmark)
   - Impact terhadap laporan keuangan
   - Significance level (Critical/High/Medium/Low)

4. RISK EVALUATION
   - Level risiko keseluruhan
   - Potential impact ke operasional
   - Compliance risk (OJK, DSN-MUI)
   - Reputational risk

5. COMPLIANCE CHECK
   - Kesesuaian dengan PSAK 110 (Akuntansi Syariah)
   - Regulasi OJK untuk deposito mudharabah
   - Pedoman DSN-MUI untuk bagi hasil
   - Best practices industri

6. REKOMENDASI TINDAKAN
   - Immediate actions (1-3 hari)
   - Short-term corrections (1-2 minggu)
   - Long-term improvements (1-3 bulan)
   - Preventive controls
   - Suggested PIC (Person in Charge)

7. KESIMPULAN
   - Overall assessment
   - Next steps yang prioritas
   - Timeline yang disarankan

FORMAT OUTPUT:
- Gunakan bahasa Indonesia profesional
- Gunakan bullet points untuk clarity
- Berikan angka spesifik jika memungkinkan
- Actionable dan practical
- Hindari jargon yang terlalu teknis
"""
        return prompt
    
    def _build_variance_prompt(self, variance_data: Dict, context: Optional[str]) -> str:
        """Build prompt for variance analysis"""
        
        prompt = f"""Analisis mendalam untuk variance deposito syariah:

VARIANCE DATA:
==============
Jenis Deposito: {variance_data.get('jenis', 'N/A')}
Nomor Bilyet: {variance_data.get('nomor_bilyet', 'N/A')}
Nominal Deposito: Rp {variance_data.get('nominal_deposito', 0):,.2f}
Imbal Hasil Bank: Rp {variance_data.get('imbal_hasil_bank', 0):,.2f}
Imbal Hasil BPKH: Rp {variance_data.get('imbal_hasil_bpkh', 0):,.2f}
Selisih: Rp {variance_data.get('selisih', 0):,.2f}
Persentase: {variance_data.get('pct_selisih', 0):.4f}%
Periode: {variance_data.get('periode', 'N/A')}

CONTEXT TAMBAHAN:
{context if context else 'Tidak ada context tambahan'}

PERTANYAAN:
1. Apakah variance ini wajar untuk deposito syariah?
2. Apa kemungkinan penyebab teknis dari selisih ini?
3. Langkah investigasi apa yang perlu dilakukan?
4. Threshold materialitas yang relevan?
5. Tindakan korektif yang disarankan?

Berikan analisis dalam format yang jelas dan actionable.
"""
        return prompt
    
    def _build_recommendation_prompt(
        self,
        exception_items: List[Dict],
        historical_data: Optional[Dict]
    ) -> str:
        """Build prompt for recommendations"""
        
        exceptions_text = ""
        for idx, item in enumerate(exception_items[:10], 1):  # Top 10
            exceptions_text += f"\n{idx}. {item.get('nomor_bilyet', 'N/A')}"
            exceptions_text += f"\n   Selisih: Rp {item.get('selisih', 0):,.2f} ({item.get('pct_selisih', 0):.2f}%)"
        
        prompt = f"""Berikan rekomendasi untuk menangani exception items berikut:

EXCEPTION ITEMS (Top 10):
========================
{exceptions_text}

HISTORICAL CONTEXT:
{json.dumps(historical_data, indent=2) if historical_data else 'Tidak tersedia'}

Berikan:
1. Prioritisasi exception items (mana yang harus ditangani dulu)
2. Langkah investigasi per item
3. Estimated time untuk resolution
4. Resources yang dibutuhkan
5. Preventive measures untuk masa depan

Format dalam bahasa Indonesia yang actionable dan praktis.
"""
        return prompt
    
    def _call_openrouter(self, prompt: str) -> str:
        """Call OpenRouter API"""
        
        if not self.config.openrouter_api_key:
            return "Error: OpenRouter API key tidak tersedia. Silakan konfigurasi di .env file."
        
        headers = {
            "Authorization": f"Bearer {self.config.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
        
        for attempt in range(self.config.max_retries):
            try:
                response = requests.post(
                    self.openrouter_url,
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                else:
                    logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                    if attempt < self.config.max_retries - 1:
                        time.sleep(self.config.retry_delay)
                        continue
                    return f"Error: API returned {response.status_code}. Please check your API key and try again."
                    
            except Exception as e:
                logger.error(f"Error calling OpenRouter: {str(e)}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay)
                    continue
                return f"Error: {str(e)}"
        
        return "Error: Max retries exceeded"
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API (Claude)"""
        
        if not self.config.anthropic_api_key:
            return "Error: Anthropic API key tidak tersedia."
        
        headers = {
            "x-api-key": self.config.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": self.config.max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        for attempt in range(self.config.max_retries):
            try:
                response = requests.post(
                    self.anthropic_url,
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['content'][0]['text']
                else:
                    logger.error(f"Anthropic API error: {response.status_code}")
                    if attempt < self.config.max_retries - 1:
                        time.sleep(self.config.retry_delay)
                        continue
                    return f"Error: API returned {response.status_code}"
                    
            except Exception as e:
                logger.error(f"Error calling Anthropic: {str(e)}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay)
                    continue
                return f"Error: {str(e)}"
        
        return "Error: Max retries exceeded"
    
    @staticmethod
    def format_analysis(analysis_text: str) -> str:
        """Format AI analysis for display"""
        
        # Add markdown formatting
        formatted = analysis_text
        
        # Bold headers
        headers = [
            'EXECUTIVE SUMMARY', 'ROOT CAUSE ANALYSIS', 
            'MATERIALITAS ASSESSMENT', 'RISK EVALUATION',
            'COMPLIANCE CHECK', 'REKOMENDASI TINDAKAN', 'KESIMPULAN'
        ]
        
        for header in headers:
            formatted = formatted.replace(f"{header}:", f"**{header}:**")
            formatted = formatted.replace(f"{header.lower()}:", f"**{header}:**")
        
        return formatted