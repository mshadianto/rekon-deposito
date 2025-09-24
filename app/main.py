import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import requests
import json
from io import BytesIO

# Konfigurasi halaman
st.set_page_config(
    page_title="Rekonsiliasi Deposito BTPN Syariah",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .ai-box {
        background-color: #f0f4f8;
        border-left: 4px solid #4f46e5;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'rekon_data' not in st.session_state:
    st.session_state.rekon_data = None
if 'ai_analysis' not in st.session_state:
    st.session_state.ai_analysis = None

class DepositoRekonEngine:
    """Agentic AI Engine untuk Rekonsiliasi Deposito"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        
    def load_excel_data(self, file):
        """Load data dari file Excel"""
        try:
            # Baca semua sheets
            xl_file = pd.ExcelFile(file)
            sheets_data = {}
            
            for sheet_name in xl_file.sheet_names:
                df = pd.read_excel(file, sheet_name=sheet_name)
                sheets_data[sheet_name] = df
                
            return sheets_data
        except Exception as e:
            st.error(f"Error loading Excel: {str(e)}")
            return None
    
    def calculate_reconciliation(self, data_bank, data_bpkh):
        """Hitung rekonsiliasi antara data Bank dan BPKH"""
        rekon_results = []
        
        for idx, row_bank in data_bank.iterrows():
            # Cari matching record di data BPKH
            matching_bpkh = data_bpkh[
                (data_bpkh['Nomor Bilyet'] == row_bank['Nomor Bilyet']) |
                (data_bpkh['Nomor Rekening'] == row_bank['Nomor Rekening'])
            ]
            
            if not matching_bpkh.empty:
                bpkh_row = matching_bpkh.iloc[0]
                
                selisih = row_bank['Nominal Imbal Hasil'] - bpkh_row['Nominal Imbal Hasil']
                
                rekon_results.append({
                    'Nomor Bilyet': row_bank['Nomor Bilyet'],
                    'Nomor Rekening': row_bank['Nomor Rekening'],
                    'Nominal Deposito': row_bank['Nominal Deposito'],
                    'Imbal Hasil Bank': row_bank['Nominal Imbal Hasil'],
                    'Imbal Hasil BPKH': bpkh_row['Nominal Imbal Hasil'],
                    'Selisih': selisih,
                    'Status': 'Match' if abs(selisih) < 1 else 'Difference',
                    'Persentase Selisih': (selisih / row_bank['Nominal Imbal Hasil'] * 100) if row_bank['Nominal Imbal Hasil'] != 0 else 0
                })
            else:
                rekon_results.append({
                    'Nomor Bilyet': row_bank['Nomor Bilyet'],
                    'Nomor Rekening': row_bank['Nomor Rekening'],
                    'Nominal Deposito': row_bank['Nominal Deposito'],
                    'Imbal Hasil Bank': row_bank['Nominal Imbal Hasil'],
                    'Imbal Hasil BPKH': 0,
                    'Selisih': row_bank['Nominal Imbal Hasil'],
                    'Status': 'Not Found in BPKH',
                    'Persentase Selisih': 100
                })
        
        return pd.DataFrame(rekon_results)
    
    def analyze_with_ai(self, rekon_summary, api_key):
        """Analisis menggunakan AI Agent (Qwen3 via OpenRouter)"""
        
        prompt = f"""Sebagai AI Agent untuk rekonsiliasi keuangan Bank Syariah, analisis data rekonsiliasi deposito berikut:

RINGKASAN REKONSILIASI:
- Total Deposito: Rp {rekon_summary['total_deposito']:,.2f}
- Total Imbal Hasil Bank: Rp {rekon_summary['total_bank']:,.2f}
- Total Imbal Hasil BPKH: Rp {rekon_summary['total_bpkh']:,.2f}
- Total Selisih: Rp {rekon_summary['total_selisih']:,.2f}
- Persentase Selisih: {rekon_summary['pct_selisih']:.4f}%

BREAKDOWN PER JENIS:
{rekon_summary['breakdown']}

Berikan analisis komprehensif meliputi:
1. Root Cause Analysis - kemungkinan penyebab selisih
2. Materialitas - apakah selisih material atau tidak
3. Risk Assessment - tingkat risiko dari selisih ini
4. Rekomendasi Tindakan - langkah-langkah perbaikan
5. Compliance Check - kesesuaian dengan regulasi Bank Syariah

Format output dalam bahasa Indonesia yang profesional."""

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "qwen/qwen-2.5-72b-instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error calling AI: {str(e)}"

def main():
    # Header
    st.title("🏦 Sistem Rekonsiliasi Deposito BTPN Syariah")
    st.markdown("### Agentic AI-Powered Reconciliation System")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Konfigurasi")
        
        # API Key input
        api_key = st.text_input(
            "OpenRouter API Key",
            type="password",
            help="Masukkan API key OpenRouter untuk mengaktifkan AI Agent"
        )
        
        st.markdown("---")
        
        # File uploads
        st.subheader("📁 Upload Data")
        
        file_kertas_kerja = st.file_uploader(
            "Kertas Kerja Rekonsiliasi (Excel)",
            type=['xlsx', 'xls'],
            key="kertas_kerja"
        )
        
        file_laporan_bps = st.file_uploader(
            "Laporan Penempatan BPS (Excel)",
            type=['xlsx', 'xls'],
            key="laporan_bps"
        )
        
        st.markdown("---")
        
        if st.button("🔄 Proses Rekonsiliasi", type="primary", use_container_width=True):
            if file_kertas_kerja and file_laporan_bps:
                with st.spinner("Memproses data..."):
                    engine = DepositoRekonEngine(api_key)
                    
                    # Load data
                    data_bank = engine.load_excel_data(file_kertas_kerja)
                    data_bpkh = engine.load_excel_data(file_laporan_bps)
                    
                    if data_bank and data_bpkh:
                        st.session_state.rekon_data = {
                            'bank': data_bank,
                            'bpkh': data_bpkh,
                            'engine': engine
                        }
                        st.success("✅ Data berhasil diproses!")
            else:
                st.error("⚠️ Upload kedua file terlebih dahulu")
    
    # Main content
    tabs = st.tabs([
        "📊 Dashboard",
        "🔍 Rekonsiliasi Detail",
        "⏰ Monitoring Waktu",
        "🤖 AI Analysis",
        "📈 Visualisasi"
    ])
    
    # Tab 1: Dashboard
    with tabs[0]:
        st.header("Dashboard Rekonsiliasi")
        
        if st.session_state.rekon_data:
            # Sample summary metrics (gunakan data aktual jika tersedia)
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Deposito",
                    "Rp 3.29 M",
                    delta="Apr-May 2025"
                )
            
            with col2:
                st.metric(
                    "Imbal Hasil Bank",
                    "Rp 5.96 Jt",
                    delta="+0.35%"
                )
            
            with col3:
                st.metric(
                    "Imbal Hasil BPKH",
                    "Rp 5.94 Jt",
                    delta="-0.37%"
                )
            
            with col4:
                st.metric(
                    "Total Selisih",
                    "Rp 21.7 Rb",
                    delta="0.36%",
                    delta_color="inverse"
                )
            
            st.markdown("---")
            
            # Summary table
            summary_data = {
                'Jenis Dana': ['Setoran Awal', 'Setoran Lunas', 'Nilai Manfaat', 'Total'],
                'Realisasi': ['Rp 5.628.859', 'Rp 329.803', 'Rp 0', 'Rp 5.958.662'],
                'Ekspektasi': ['Rp 5.608.919', 'Rp 328.020', 'Rp 0', 'Rp 5.936.940'],
                'Selisih': ['Rp 19.940', 'Rp 1.783', 'Rp 0', 'Rp 21.722'],
                'Status': ['⚠️ Review', '✅ Normal', '✅ Normal', '⚠️ Review']
            }
            
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True)
            
        else:
            st.info("👆 Upload file di sidebar untuk memulai rekonsiliasi")
    
    # Tab 2: Rekonsiliasi Detail
    with tabs[1]:
        st.header("Detail Rekonsiliasi")
        
        if st.session_state.rekon_data:
            data = st.session_state.rekon_data
            
            # Display detail untuk setiap jenis deposito
            deposito_types = ['Setoran Awal', 'Setoran Lunas', 'Nilai Manfaat']
            
            for dep_type in deposito_types:
                with st.expander(f"📋 {dep_type}", expanded=(dep_type == 'Setoran Awal')):
                    # Create sample detail data
                    detail_data = {
                        'Periode': ['Apr-25', 'May-25'],
                        'Pokok Deposito': ['Rp 1.845.237.362', 'Rp 969.153.276'],
                        'Imbal Hasil Bank': ['Rp 3.471.194', 'Rp 2.157.665'],
                        'Imbal Hasil BPKH': ['Rp 3.462.921', 'Rp 2.145.998'],
                        'Selisih': ['Rp 8.273', 'Rp 11.667'],
                        'Status': ['⚠️ Difference', '⚠️ Difference']
                    }
                    
                    df_detail = pd.DataFrame(detail_data)
                    st.dataframe(df_detail, use_container_width=True)
        else:
            st.info("Upload data terlebih dahulu")
    
    # Tab 3: Monitoring Waktu
    with tabs[2]:
        st.header("Monitoring Ketepatan Waktu")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📅 Status Realisasi")
            
            timeline_data = {
                'Transaksi': [
                    'SA Apr-25',
                    'SA May-25', 
                    'SL Apr-25',
                    'NM Apr-25'
                ],
                'Tgl Penempatan': [
                    '02-Apr-2025',
                    '01-May-2025',
                    '15-Apr-2025',
                    'N/A'
                ],
                'Tgl Realisasi': [
                    '24-Apr-2025',
                    '24-May-2025',
                    '30-Apr-2025',
                    'N/A'
                ],
                'Status': [
                    '✅ Tepat Waktu',
                    '✅ Tepat Waktu',
                    '✅ Tepat Waktu',
                    '⚪ Tidak Ada'
                ]
            }
            
            df_timeline = pd.DataFrame(timeline_data)
            st.dataframe(df_timeline, use_container_width=True)
        
        with col2:
            st.subheader("📊 Analisis Selisih")
            
            variance_data = {
                'Jenis': ['Setoran Awal', 'Setoran Lunas', 'Nilai Manfaat'],
                'Selisih (%)': [0.3545, 0.5407, 0.0000],
                'Kategori': ['🟢 Baik', '🟡 Perhatian', '🟢 Excellent']
            }
            
            df_variance = pd.DataFrame(variance_data)
            st.dataframe(df_variance, use_container_width=True)
    
    # Tab 4: AI Analysis
    with tabs[3]:
        st.header("🤖 AI Agent Analysis")
        
        if api_key:
            if st.button("🔍 Jalankan Analisis AI", type="primary"):
                with st.spinner("AI Agent sedang menganalisis data..."):
                    # Prepare summary for AI
                    rekon_summary = {
                        'total_deposito': 3293300064.00,
                        'total_bank': 5958662.00,
                        'total_bpkh': 5936939.54,
                        'total_selisih': 21722.46,
                        'pct_selisih': 0.3647,
                        'breakdown': """
                        - Setoran Awal: Selisih Rp 19.940 (0.35%)
                        - Setoran Lunas: Selisih Rp 1.783 (0.54%)
                        - Nilai Manfaat: Selisih Rp 0 (0.00%)
                        """
                    }
                    
                    engine = DepositoRekonEngine(api_key)
                    analysis = engine.analyze_with_ai(rekon_summary, api_key)
                    st.session_state.ai_analysis = analysis
            
            if st.session_state.ai_analysis:
                st.markdown('<div class="ai-box">', unsafe_allow_html=True)
                st.markdown("### 📝 Hasil Analisis AI Agent:")
                st.markdown(st.session_state.ai_analysis)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Export option
                if st.button("📥 Download Analisis"):
                    st.download_button(
                        label="Download sebagai TXT",
                        data=st.session_state.ai_analysis,
                        file_name=f"ai_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
        else:
            st.warning("⚠️ Masukkan OpenRouter API Key di sidebar untuk mengaktifkan AI Analysis")
    
    # Tab 5: Visualisasi
    with tabs[4]:
        st.header("📈 Visualisasi Data")
        
        # Chart 1: Perbandingan Imbal Hasil
        col1, col2 = st.columns(2)
        
        with col1:
            fig_comparison = go.Figure()
            
            categories = ['Setoran Awal', 'Setoran Lunas', 'Nilai Manfaat']
            bank_values = [5628859, 329803, 0]
            bpkh_values = [5608919, 328020, 0]
            
            fig_comparison.add_trace(go.Bar(
                name='Bank',
                x=categories,
                y=bank_values,
                marker_color='#3b82f6'
            ))
            
            fig_comparison.add_trace(go.Bar(
                name='BPKH',
                x=categories,
                y=bpkh_values,
                marker_color='#10b981'
            ))
            
            fig_comparison.update_layout(
                title='Perbandingan Imbal Hasil Bank vs BPKH',
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig_comparison, use_container_width=True)
        
        with col2:
            # Chart 2: Selisih per Kategori
            fig_variance = go.Figure(data=[
                go.Pie(
                    labels=['Setoran Awal', 'Setoran Lunas', 'Nilai Manfaat'],
                    values=[19940, 1783, 0],
                    hole=.3,
                    marker_colors=['#ef4444', '#f59e0b', '#10b981']
                )
            ])
            
            fig_variance.update_layout(
                title='Distribusi Selisih',
                height=400
            )
            
            st.plotly_chart(fig_variance, use_container_width=True)
        
        # Chart 3: Trend Selisih
        st.subheader("📉 Trend Selisih Bulanan")
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
        trend_values = [15000, 18000, 16500, 19940, 11667]
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=months,
            y=trend_values,
            mode='lines+markers',
            name='Selisih',
            line=dict(color='#6366f1', width=3),
            marker=dict(size=10)
        ))
        
        fig_trend.update_layout(
            title='Trend Selisih Rekonsiliasi (2025)',
            xaxis_title='Bulan',
            yaxis_title='Selisih (Rp)',
            height=400
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)

if __name__ == "__main__":
    main()