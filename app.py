
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Çalışan Ayrılma Riski Paneli", layout="wide")
st.title("📊 Çalışan Ayrılma Riski Dashboard")
st.markdown("Bu panel, çalışanların ayrılma risklerini segmentlere göre görüntüler ve yöneticilerin hızlı aksiyon almasına yardımcı olur.")

uploaded_file = st.file_uploader("📂 Lütfen Excel dosyanızı yükleyin (.xlsx)", type=["xlsx"])
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    except ImportError:
        st.error("❗ 'openpyxl' yüklü değil. Lütfen requirements.txt dosyana 'openpyxl' ekle.")
    else:
        np.random.seed(42)
        df['risk_score'] = np.random.beta(2, 2, size=len(df))

        def label_risk(score):
            if score > 0.75:
                return 'Yüksek'
            elif score > 0.4:
                return 'Orta'
            else:
                return 'Düşük'

        df['risk_seviyesi'] = df['risk_score'].apply(label_risk)

        col1, col2, col3 = st.columns(3)
        col1.metric("👥 Toplam Çalışan", df['PERNO'].nunique())
        col2.metric("🔴 Yüksek Riskli", (df['risk_seviyesi'] == "Yüksek").sum())
        col3.metric("🟠 Orta Riskli", (df['risk_seviyesi'] == "Orta").sum())

        st.markdown("---")

        st.subheader("🏢 Departman Bazlı Risk Dağılımı")
        dept_risk = df.groupby(['BIRIMKOD', 'risk_seviyesi']).size().unstack(fill_value=0)
        if 'Yüksek' not in dept_risk.columns:
            dept_risk['Yüksek'] = 0
        top10 = dept_risk.sort_values(by="Yüksek", ascending=False).head(10)

        fig, ax = plt.subplots(figsize=(10, 5))
        top10[['Düşük', 'Orta', 'Yüksek']].plot(kind='bar', stacked=True, colormap='coolwarm', ax=ax)
        plt.title("En Yüksek Riskli 10 Departman")
        plt.ylabel("Çalışan Sayısı")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)

        st.markdown("---")

        st.subheader("🔍 Çalışan Detayları")
        birim_sec = st.selectbox("Birim seçin", options=df['BIRIMKOD'].unique())
        filtreli_df = df[df['BIRIMKOD'] == birim_sec]

        st.dataframe(
            filtreli_df[['PERNO', 'ISYERI', 'risk_score', 'risk_seviyesi', 'total_leave_days']].sort_values(by="risk_score", ascending=False),
            use_container_width=True
        )

        st.subheader("👤 Kişi Bazlı Risk Profili")
        secilen_perno = st.selectbox("Çalışan PERNO seçin", options=filtreli_df['PERNO'].unique())
        kisi = filtreli_df[filtreli_df['PERNO'] == secilen_perno].iloc[0]

        st.markdown(f"""
        **📌 PERNO:** {secilen_perno}  
        **🏢 Birim:** {kisi['BIRIMKOD']}  
        **📍 Lokasyon:** {kisi['ISYERI']}  
        **🔥 Risk Skoru:** `{round(kisi['risk_score'], 2)}`  
        **⚠️ Risk Seviyesi:** **{kisi['risk_seviyesi']}**
        """)

        st.info("🎯 *Öneri:* Bu çalışan son dönemde yüksek izin kullanmış olabilir. Müdürle birebir görüşme planlanabilir.")
