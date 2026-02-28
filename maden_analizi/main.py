import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Maden Verileri Analizi", layout="wide")

st.title("Maden Verileri Analizi", text_alignment="center") #sayfa başlığı
st.divider()
@st.cache_data #önbelleğe alma işlemi

def veriyi_getir(): #oluşturulan fonksiyon dataframeleri çağırmak için kullanılacak
    df_fiyat = pd.read_csv("./veriler/maden_fiyatları.csv",encoding="utf-8", sep=";") #csv dosyalarını dataframe olarak kaydediyoruz
    df_lokasyon = pd.read_csv("./veriler/maden_lokasyon_temiz.csv",encoding="utf-8", sep=";") #csv dosyalarını dataframe olarak kaydediyoruz
    df_rezerv = pd.read_csv("./veriler/maden_rezervleri.csv",encoding="utf-8", sep=";") #csv dosyalarını dataframe olarak kaydediyoruz
    df_uretim = pd.read_csv("./veriler/maden_uretim.csv",encoding="utf-8", sep=";") #csv dosyalarını dataframe olarak kaydediyoruz
    return df_fiyat, df_lokasyon, df_rezerv, df_uretim 

df_fiyat, df_lokasyon, df_rezerv, df_uretim = veriyi_getir() #CSV dosyalarını çağırmak için kullanılan fonksiyon

df_fiyat.rename(columns={'maden_adi':'Maden Adı'},inplace=True)
df_fiyat.drop(columns={'id'},inplace=True)


df_lokasyon.drop(columns={'id'},inplace=True)

df_rezerv.drop(columns={'id','kaynak','aciklama'},inplace=True)
df_rezerv.rename(columns={'maden_adi':'Maden Adı','maden_turu':'Maden Türü','ulke':'Ülke','rezerv':'Rezerv', 'uretim_2024':'2024 Üretimi', 'birim':'Birim'},inplace=True)

df_uretim.rename(columns={'maden_adi':'Maden Adı','maden_turu':'Maden Türü'},inplace=True)
df_uretim.drop(columns={'id'},inplace=True)

#------Sidebar Tasarımı
maden_listesi = df_fiyat['Maden Adı'].unique() #Farklı isimleri listeye ekliyoruz
st.sidebar.title("Filtreler")  #sol taraftaki sidebar kısmına başlık eklemek için
secilen_maden = st.sidebar.selectbox("Maden Seçiniz", maden_listesi) #sol taraftaki sidebar kısmında bulunan filtreleme için seçim kutusu

#------ Gerekli Filtrelemeler
df_uretim_filtre = df_uretim[df_uretim['Maden Adı'].str.contains(secilen_maden)]#elimizdeki listeyi seçime göre filtreleme
df_lokasyon_filtre = df_lokasyon[df_lokasyon['Maden Adı'].str.contains(secilen_maden)] #elimizdeki listeyi seçime göre filtreleme
df_fiyat_filtre = df_fiyat[df_fiyat['Maden Adı'] == secilen_maden]  #elimizdeki listeyi seçime göre filtreleme
df_rezerv_filtre = df_rezerv[df_rezerv['Maden Adı'].str.contains(secilen_maden)]

#------ Üstteki Kutular KPI Kartları
a,b,c,d = st.columns(4)

a.metric(label="Madenin Adı", value=secilen_maden, border=True)
b.metric(label=f"2024 Yılı Türkiye Üretim Miktarı ({df_uretim_filtre['birim'].iloc[0]} )", value=f"{df_uretim_filtre['2024'].iloc[0]:,.0f}", border=True)
c.metric(label=f'Türkiye Rezerv Miktarı ({df_rezerv_filtre['Birim'].iloc[0]} )', value=f"{df_rezerv_filtre[df_rezerv_filtre['Ülke'] == 'Türkiye']['Rezerv'].iloc[0]:,.0f}", border=True)
d.metric(label=f'2024 Yılı Fiyatı ({df_fiyat_filtre['birim'].iloc[0]} )', value=df_fiyat_filtre['2024'].iloc[0], border=True)
st.divider()


#------Türkiye Maden Üretim Tablo ve Grafiği
st.subheader(f"{secilen_maden} Madeninin Yıllara Göre Türkiye Üretim Miktarı (MAPEG 2025)") #seçilene göre değşen başlık eklemek için

uretim_yillari = ['2014','2015','2016','2017','2018','2019','2020', '2021', '2022', '2023', '2024']
uretim_grafigi =df_uretim_filtre[uretim_yillari].T
st.dataframe(df_uretim_filtre, hide_index=True)
st.subheader(f"{secilen_maden} Madeninin Yıllara Göre Türkiye Üretim Miktarı Grafiği ") #seçilene göre değşen başlık eklemek için
st.line_chart(uretim_grafigi,x_label="Yıllar", y_label=df_uretim_filtre['birim'].iloc[0], color="#F54927") #sol taraftaki sidebar kısmından seçilen isme göre filtrelenmiş tablonun sütun grafiği
st.divider()

#------Türkiye Maden Üretim Haritası
st.subheader(f"{secilen_maden} Madeninin Türkiye Üretim Haritası")  #grafiğin üstüne seçilene göre değşen başlık eklemek için


st.map(df_lokasyon_filtre, latitude='latitude', longitude='longitude', zoom=5, color="#F54927") #sol taraftaki sidebar kısmından seçilen isme göre harita gösterimi
st.dataframe(df_lokasyon_filtre,hide_index=True) #sol taraftaki sidebar kısmından seçilen isme göre filtrelenmiş tablonun sütun grafiği
st.divider()

#------Fiyat Değişimi Tablo ve Grafiği
st.subheader(f"{secilen_maden} Madeninin Yıllara Göre Fiyat Değişimi (USGS 2025) ")

fiyat_yillari = ['2020', '2021', '2022', '2023', '2024'] #sadece belirli sütunların değişkene atanması
grafik_verisi = df_fiyat_filtre[fiyat_yillari].T #belirli sütunları seçme ve yönünü değiştirme
maksimum_fiyat = grafik_verisi.iloc[:, 0].max() #maksimum fiyat
maksimum_yil = grafik_verisi.iloc[:, 0].idxmax() #maksimum fiyat olan yıl

st.dataframe(df_fiyat_filtre, hide_index=True) #sol taraftaki sidebar kısmından seçilen isme göre filtrelenmiş tablo
st.subheader(f"{secilen_maden} Madeninin Yıllara Göre Fiyat Değişim Grafiği") #grafiğin üstüne seçilene göre değşen başlık eklemek için

st.bar_chart(grafik_verisi, x_label="Yıllar", y_label=df_fiyat_filtre['birim'].iloc[0], color="#F54927") #sol taraftaki sidebar kısmından seçilen isme göre filtrelenmiş tablonun sütun grafiği
st.divider()

#------Dünya Maden Rezervleri Tablo ve Grafiği
st.subheader(f"{secilen_maden} Madeninin Dünya Rezervleri Tablo ve Grafiği (USGS 2025) ")



# 1. Çift Y eksenli bir tuval (şablon) oluşturuyoruz
fig = make_subplots(specs=[[{"secondary_y": True}]])

# 2. Sol Eksene Üretim Verisini Ekliyoruz (Mavi Çubuklar)
fig.add_trace(
    go.Bar(
        x=df_rezerv_filtre['Ülke'], 
        y=df_rezerv_filtre['2024 Üretimi'], 
        name="2024 Üretimi",
        marker_color='#F54927', # Şık bir mavi
        offsetgroup=1,
        text=df_rezerv_filtre['2024 Üretimi'], 
texttemplate='%{text:.2s}', 
textposition='outside'
    ),
    secondary_y=False, # Sol eksen
)

# 3. Sağ Eksene Rezerv Verisini Ekliyoruz (Turuncu Çubuklar)
fig.add_trace(
    go.Bar(
        x=df_rezerv_filtre['Ülke'], 
        y=df_rezerv_filtre['Rezerv'], 
        name="Rezerv",
        marker_color='#ff7f0e',# Şık bir turuncu
        offsetgroup=2,
        text=df_rezerv_filtre['Rezerv'], 
texttemplate='%{text:.2s}', 
textposition='outside'
    ),
    secondary_y=True, # Sağ eksen
)

# X ekseni (Alt taraf)
fig.update_xaxes(title_text="Ülkeler")

# Sol Y ekseni (Üretim)
fig.update_yaxes(title_text="Yıllık Üretim (Ton)", secondary_y=False)

# Sağ Y ekseni (Rezerv)
fig.update_yaxes(title_text="Toplam Rezerv (Ton)", secondary_y=True)

# 4. Grafiğin tasarımını güncelliyoruz (Çubukları yan yana diziyoruz)
fig.update_layout(
    title_text=f"{secilen_maden} Küresel Rezerv ve Üretim Dağılımı",
    barmode='group',
    template='plotly_dark' # Streamlit temasına uysun diye
)

# 3. Streamlit'e "Bu tuvali ekrana bas" diyoruz
st.plotly_chart(fig)

tablo_rezrv = ['Ülke', 'Rezerv', '2024 Üretimi']
st.subheader(f"{secilen_maden} Madeni Rezerv ve 2024 Üretim Kıyaslama Tablosu")
st.dataframe(df_rezerv_filtre, hide_index=True)

st.divider()

st.header("Genel Özet")
turkiye_uretim = f"{df_rezerv_filtre[df_rezerv_filtre['Ülke'] == 'Türkiye']['2024 Üretimi'].iloc[0]:,.0f}"
turkiye_rezerv = f"{df_rezerv_filtre[df_rezerv_filtre['Ülke'] == 'Türkiye']['Rezerv'].iloc[0]:,.0f}"
birim = f"{df_fiyat_filtre['birim'].iloc[0]}"
st.subheader("        "f"{secilen_maden} madeninin en yüksek satış fiyatı {maksimum_yil} yılında {maksimum_fiyat} {birim} seviyesindedir. USGS(2025) verilerine göre Türkiye 2024 yılı üretim miktarı  {turkiye_uretim} ton ve rezerv miktarı ise {turkiye_rezerv} ton olarak kayıt edilmiştir.") #Genel özet yazısı
st.divider()


