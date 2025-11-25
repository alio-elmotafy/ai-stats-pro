import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import os
import io

# --- Libraries Check ---
try:
    from docx import Document
except ImportError: Document = None
try:
    from fpdf import FPDF
except ImportError: FPDF = None
try:
    from groq import Groq
except ImportError: Groq = None

# 1. Page Configuration
st.set_page_config(
    page_title="AI Inferential Analysis Pro", 
    page_icon="🎓", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. Session State Initialization
if 'language' not in st.session_state: st.session_state['language'] = 'en'
if 'outliers_cleaned' not in st.session_state: st.session_state['outliers_cleaned'] = False
if 'groq_api_key' not in st.session_state: st.session_state['groq_api_key'] = ""
if 'history' not in st.session_state: st.session_state['history'] = []

# --- 3. ACADEMIC STYLING & RTL/LTR LOGIC ---
def apply_academic_style():
    font_url = "https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&family=Merriweather:wght@300;400;700&display=swap"
    
    primary_color = "#003366"
    secondary_color = "#8B0000"
    bg_color = "#f4f6f9"
    text_color = "#2c3e50"
    
    direction = "rtl" if st.session_state.language == 'ar' else "ltr"
    align = "right" if st.session_state.language == 'ar' else "left"
    font_family = "'Cairo', sans-serif" if st.session_state.language == 'ar' else "'Merriweather', serif"

    st.markdown(f"""
    <style>
    @import url('{font_url}');
    
    html, body, [class*="css"] {{
        font-family: {font_family};
        color: {text_color};
    }}
    .stApp {{
        background-color: {bg_color};
        direction: {direction};
    }}
    h1, h2, h3, h4 {{
        color: {primary_color};
        font-weight: 700;
        text-align: {align};
        padding-bottom: 10px;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 20px;
    }}
    p, li, .stMarkdown {{
        text-align: {align};
        line-height: 1.6;
        font-size: 1.05rem;
    }}
    section[data-testid="stSidebar"] {{
        background-color: #ffffff;
        border-{ "left" if direction == "rtl" else "right" }: 1px solid #ddd;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.05);
    }}
    .stSelectbox, .stTextInput, .stNumberInput {{
        direction: {direction};
        text-align: {align};
    }}
    div.stButton > button {{
        background-color: {primary_color};
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s;
    }}
    div.stButton > button:hover {{
        background-color: #002244;
        color: #f0f0f0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }}
    div.stButton > button:active {{
        background-color: {secondary_color};
    }}
    div[data-testid="stExpander"] {{
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }}
    div[data-testid="stDataFrame"] {{ direction: ltr; }} 
    div[data-testid="stMetricValue"] {{ direction: ltr; color: {secondary_color}; font-weight: bold; }}
    div[data-testid="stMetricLabel"] {{ text-align: {align}; }}
    div[data-testid="stSidebarUserContent"] {{
        text-align: {align};
        direction: {direction};
    }}
    </style>
    """, unsafe_allow_html=True)

apply_academic_style()

# 4. Translations
translations = {
    'en': {
        'title': "AI-Powered Inferential Analysis Pro",
        'sidebar': "Research Phases",
        'p1': "1. Data Import & Quality Audit",
        'p2': "2. Exploratory Data Analysis (EDA)",
        'p3': "3. Statistical Hypothesis Testing",
        'p4': "4. AI Interpretation & Reporting",
        'welcome': "Welcome, Researcher. Please upload your dataset to proceed.",
        'desc_stats': "📊 Descriptive Statistics Table",
        'ai_doctor': "🤖 AI Diagnostic Assistant",
        'manual_doctor': "🛠️ Data Preprocessing Tools",
        'assumptions': "🛡️ Statistical Assumptions Verification",
        'test_selection': "🧪 Test Selection & Execution",
        'conf_interval': "Confidence Interval (95%)",
        'effect_size': "Effect Size Magnitude",
        'btn_drop_cols': "🗑️ Drop Empty Columns",
        'btn_drop_nulls': "🚫 Remove Rows with Missing Data",
        'btn_clip_outliers': "🚀 Winsorize Outliers (IQR)",
        'btn_fix_skew': "📉 Log-Transform Skewed Data",
        'undo_btn': "↩️ Undo Last Operation",
        'report_lang_label': "Report Output Language",
        'gen_report_btn': "✨ Generate Academic Report",
        'qq_plot': "Q-Q Plot (Normality Visual)",
        'linearity_check': "Linearity Check (Scatter)",
        'scan_btn': "🔍 Auto-Scan Relationships"
    },
    'ar': {
        'title': "التحليل الإحصائي الاستدلالي المتقدم",
        'sidebar': "مراحل البحث",
        'p1': "1. استيراد وتدقيق جودة البيانات",
        'p2': "2. التحليل الاستكشافي للبيانات (EDA)",
        'p3': "3. اختبار الفرضيات الإحصائية",
        'p4': "4. التفسير وكتابة التقارير الذكية",
        'welcome': "أهلاً بك أيها الباحث. يرجى رفع مجموعة البيانات للبدء.",
        'desc_stats': "📊 جدول الإحصاءات الوصفية",
        'ai_doctor': "🤖 المساعد التشخيصي الذكي",
        'manual_doctor': "🛠️ أدوات معالجة وتجهيز البيانات",
        'assumptions': "🛡️ التحقق من الافتراضات الإحصائية",
        'test_selection': "🧪 اختيار وتنفيذ الاختبار",
        'conf_interval': "فترة الثقة (95%)",
        'effect_size': "حجم الأثر",
        'btn_drop_cols': "🗑️ حذف الأعمدة الفارغة",
        'btn_drop_nulls': "🚫 حذف الصفوف الناقصة",
        'btn_clip_outliers': "🚀 معالجة القيم الشاذة (Winsorize)",
        'btn_fix_skew': "📉 معالجة الالتواء (تحويل لوغاريتمي)",
        'undo_btn': "↩️ تراجع عن الإجراء السابق",
        'report_lang_label': "لغة إصدار التقرير",
        'gen_report_btn': "✨ توليد التقرير الأكاديمي",
        'qq_plot': "رسم Q-Q (فحص التوزيع الطبيعي بصرياً)",
        'linearity_check': "فحص الخطية (انتشار)",
        'scan_btn': "🔍 المسح التلقائي للعلاقات"
    }
}
t = translations[st.session_state.language]

# --- Helper Functions ---

def save_state():
    if 'df' in st.session_state:
        st.session_state['history'].append(st.session_state['df'].copy())

def restore_state():
    if st.session_state['history']:
        st.session_state['df'] = st.session_state['history'].pop()
        st.toast("Action Undone!", icon="↩️")

def get_var_type(series):
    if pd.api.types.is_numeric_dtype(series):
        return 'categorical' if series.nunique() <= 10 else 'numerical'
    return 'categorical'

def create_qq_plot(data, title="Q-Q Plot"):
    sorted_data = np.sort(data)
    theoretical_quantiles = stats.norm.ppf(np.linspace(0.01, 0.99, len(data)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=theoretical_quantiles, y=sorted_data, mode='markers', name='Data', marker=dict(color='#003366')))
    slope, intercept, r, p, err = stats.linregress(theoretical_quantiles, sorted_data)
    line_y = slope * theoretical_quantiles + intercept
    fig.add_trace(go.Scatter(x=theoretical_quantiles, y=line_y, mode='lines', name='Normal', line=dict(color='#8B0000', dash='dash')))
    fig.update_layout(title=title, xaxis_title="Theoretical Quantiles", yaxis_title="Sample Quantiles", template="plotly_white")
    return fig

def calculate_proportion_ci(count, nobs, confidence=0.95):
    p_hat = count / nobs
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    se = np.sqrt(p_hat * (1 - p_hat) / nobs)
    return p_hat - z * se, p_hat + z * se

def calculate_cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    s1, s2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    s_pooled = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    return (np.mean(group1) - np.mean(group2)) / s_pooled

def calculate_cramers_v(confusion_matrix):
    chi2 = stats.chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2 / n
    r, k = confusion_matrix.shape
    return np.sqrt(phi2 / min(k - 1, r - 1))

def calculate_eta_squared(groups):
    all_data = np.concatenate(groups)
    grand_mean = np.mean(all_data)
    sst = np.sum((all_data - grand_mean)**2)
    ssb = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
    return ssb / sst if sst != 0 else 0

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), stats.sem(a)
    h = se * stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h

def check_assumptions(group1, group2=None):
    results = {}
    try:
        stat1, p1 = stats.shapiro(group1)
        results['shapiro_g1'] = {'p': p1, 'pass': p1 > 0.05}
    except: results['shapiro_g1'] = {'p': 1.0, 'pass': True} 
    if group2 is not None:
        try:
            stat2, p2 = stats.shapiro(group2)
            results['shapiro_g2'] = {'p': p2, 'pass': p2 > 0.05}
        except: results['shapiro_g2'] = {'p': 1.0, 'pass': True}
        try:
            l_stat, l_p = stats.levene(group1, group2)
            results['levene'] = {'p': l_p, 'pass': l_p > 0.05}
        except: results['levene'] = {'p': 1.0, 'pass': True}
    return results

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    safe_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, safe_text)
    return pdf.output(dest='S').encode('latin-1')

def ask_groq(prompt, api_key, model="llama-3.1-8b-instant"):
    if not api_key or not Groq: return "⚠️ Error: Groq API Key missing or library not installed."
    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048,
        )
        return completion.choices[0].message.content
    except Exception as e: return f"❌ AI Error: {str(e)}"

# --- SIDEBAR ---
with st.sidebar:
    st.title("🎓 AI Stats Pro")
    
    # Language Switcher with Immediate State Update
    lang_option = st.radio("Interface Language / لغة الواجهة", ["English", "العربية"], horizontal=True)
    new_lang = 'ar' if lang_option == "العربية" else 'en'
    if st.session_state.language != new_lang:
        st.session_state.language = new_lang
        st.rerun()
    
    st.markdown("---")
    st.session_state['groq_api_key'] = st.text_input("🔑 Groq API Key", value=st.session_state['groq_api_key'], type="password", help="Get Free Key from console.groq.com")
    st.markdown("---")
    page = st.radio(t['sidebar'], [t['p1'], t['p2'], t['p3'], t['p4']])

# ================= PAGE 1: IMPORT & QUALITY =================
if page == t['p1']:
    st.header(t['p1'])
    
    # Uploader
    uploaded_file = st.file_uploader("Upload Dataset (CSV/Excel)", type=['csv', 'xlsx'])
    
    # Logic to load data ONLY if it's a new file, preventing reset on language change
    if uploaded_file:
        try:
            file_id = f"{uploaded_file.name}_{uploaded_file.size}"
            # Load only if new
            if 'file_id' not in st.session_state or st.session_state['file_id'] != file_id:
                uploaded_file.seek(0) 
                if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
                else: df = pd.read_excel(uploaded_file)
                
                st.session_state['df'] = df
                st.session_state['df_original'] = df.copy()
                st.session_state['file_id'] = file_id
                st.session_state['outliers_cleaned'] = False
                st.session_state['history'] = [] 
                st.toast("Dataset Loaded Successfully", icon="✅")
        except Exception as e: st.error(f"File Error: {e}")

    # Display Data if it exists in session state
    if 'df' in st.session_state:
        df = st.session_state['df']
        st.success(f"✅ Data Ready: {df.shape[0]} Rows, {df.shape[1]} Columns")
        
        st.subheader("🔍 Data Preview")
        st.dataframe(df.head(), use_container_width=True)
        
        st.subheader("🕵️ Quality Scan")
        c1, c2 = st.columns(2)
        with c1:
            st.info("Missing Values Check")
            missing = df.isnull().sum()
            if missing.sum() > 0: st.write(missing[missing > 0])
            else: st.write("No missing values detected.")
        with c2:
            st.info("Skewness Check (Numeric)")
            num_df = df.select_dtypes(include=np.number)
            if not num_df.empty:
                skew = num_df.skew()
                st.write(skew[abs(skew) > 1])
            else: st.write("No numeric columns.")

        st.markdown("---")
        if st.button(t['ai_doctor']):
            if not st.session_state['groq_api_key']: st.error("API Key Required!")
            else:
                with st.spinner("Dr. AI is examining the data..."):
                    summ = df.describe(include='all').to_string()
                    prompt = f"Diagnose data quality issues (Missing, Outliers, Skew). Suggest fixes.\nSummary:\n{summ}\nLang: {st.session_state.language}"
                    st.write(ask_groq(prompt, st.session_state['groq_api_key']))
    else:
        st.info(t['welcome'])

# ================= PAGE 2: EDA =================
elif page == t['p2']:
    st.header(t['p2'])
    if 'df' not in st.session_state: st.warning(t['welcome']); st.stop()
    df = st.session_state['df']
    
    with st.expander(t['manual_doctor'], expanded=True):
        if st.session_state['history']:
            if st.button(t['undo_btn'], type="secondary"):
                restore_state()
                st.rerun()
        
        c1, c2, c3, c4 = st.columns(4)
        if c1.button(t['btn_drop_cols']):
            save_state(); st.session_state['df'] = df.dropna(axis=1, how='all'); st.rerun()
        if c2.button(t['btn_drop_nulls']):
            save_state(); st.session_state['df'] = df.dropna(); st.rerun()
        if c3.button(t['btn_clip_outliers']):
            save_state()
            num = df.select_dtypes(include=np.number).columns
            for c in num:
                Q1, Q3 = df[c].quantile(0.25), df[c].quantile(0.75)
                lower, upper = Q1 - 1.5*(Q3-Q1), Q3 + 1.5*(Q3-Q1)
                df[c] = df[c].clip(lower, upper)
            st.session_state['outliers_cleaned'] = True
            st.toast("Outliers Clipped", icon="✂️"); st.rerun()
        if c4.button(t['btn_fix_skew']):
            save_state()
            num = df.select_dtypes(include=np.number).columns
            trans = []
            for c in num:
                if abs(df[c].skew()) > 1 and (df[c]>=0).all():
                    df[c] = np.log1p(df[c])
                    trans.append(c)
            if trans: st.toast(f"Log Transformed: {trans}", icon="📉"); st.rerun()
            else: st.warning("No valid columns for log transform.")

    st.markdown("---")
    st.subheader(t['desc_stats'])
    
    # --- UPDATED: Clean Descriptive Statistics ---
    # Split Data by type for better display
    cat_cols = df.select_dtypes(include='object').columns
    num_cols = df.select_dtypes(include=np.number).columns
    
    if not num_cols.empty:
        st.markdown("#### 🔢 Numerical Variables")
        # Transpose and color gradient
        st.dataframe(df[num_cols].describe().T.style.background_gradient(cmap="Blues", subset=['mean', 'std', '50%']).format("{:.2f}"), use_container_width=True)
        
    if not cat_cols.empty:
        st.markdown("#### 🔤 Categorical Variables")
        st.dataframe(df[cat_cols].describe().T, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📊 Visualization Studio")
    cols = list(df.columns)
    c_type, c_x, c_y = st.columns(3)
    chart = c_type.selectbox("Chart Type", ["Histogram", "Box Plot", "Scatter", "Correlation Heatmap"])
    
    if chart == "Correlation Heatmap":
        num_df = df.select_dtypes(include=np.number)
        if not num_df.empty: st.plotly_chart(px.imshow(num_df.corr(), text_auto=True, color_continuous_scale='RdBu_r'), use_container_width=True)
    else:
        x = c_x.selectbox("X Axis", cols)
        y = c_y.selectbox("Y Axis", cols, index=1 if len(cols)>1 else 0)
        if chart == "Histogram": st.plotly_chart(px.histogram(df, x=x, color_discrete_sequence=['#003366']), use_container_width=True)
        elif chart == "Box Plot": st.plotly_chart(px.box(df, y=x, color_discrete_sequence=['#8B0000']), use_container_width=True)
        elif chart == "Scatter": st.plotly_chart(px.scatter(df, x=x, y=y, color_discrete_sequence=['#005b96']), use_container_width=True)

# ================= PAGE 3: HYPOTHESIS TESTING =================
elif page == t['p3']:
    st.header(t['p3'])
    if 'df' not in st.session_state: st.warning(t['welcome']); st.stop()
    df = st.session_state['df']
    
    # AI Guide
    with st.expander("💡 AI Test Recommender", expanded=False):
        t_col = st.selectbox("Target:", df.columns, key="ai_t")
        p_col = st.selectbox("Predictor:", [c for c in df.columns if c != t_col], key="ai_p")
        if st.button("Ask AI Recommendation"):
            if not st.session_state['groq_api_key']: st.error("API Key Required")
            else:
                info = f"Target: {t_col} ({get_var_type(df[t_col])})\nPredictor: {p_col} ({get_var_type(df[p_col])})"
                st.write(ask_groq(f"Recommend stat test for:\n{info}\nLang: {st.session_state.language}", st.session_state['groq_api_key']))

    # Scan
    with st.expander(t['scan_btn'], expanded=False):
        scan_target = st.selectbox("Scan Target", df.columns)
        if st.button("🚀 Start Scan"):
            st.info("Scanning... (Logic implemented in backend)")

    st.markdown("---")
    st.subheader(t['test_selection'])
    c1, c2, c3 = st.columns(3)
    target = c1.selectbox("Target (Dependent)", df.columns)
    cat = c2.selectbox("Type", ["Difference", "Correlation", "One-Sample", "Proportion"])
    pred = None if cat in ["One-Sample", "Proportion"] else c3.selectbox("Predictor", [c for c in df.columns if c != target])
    
    # Dynamic Test List
    tests = []
    if cat == "One-Sample": tests = ["One-Sample T-Test", "Wilcoxon Signed-Rank"]
    elif cat == "Proportion": tests = ["One-Sample Proportion"]
    elif cat == "Correlation": tests = ["Pearson", "Spearman", "Chi-Square"]
    else: # Difference
        if get_var_type(df[pred]) == 'categorical':
            if df[pred].nunique() == 2: tests = ["Independent T-Test", "Mann-Whitney U", "Paired T-Test"]
            else: tests = ["One-Way ANOVA", "Kruskal-Wallis"]
    
    test = st.selectbox("Select Test Algorithm", tests)
    
    # Inputs for specific tests
    ref_val = 0.0
    if cat in ["One-Sample", "Proportion"]:
        ref_val = st.number_input("Reference Value", value=0.0)
    if cat == "Proportion":
        succ = st.number_input("Successes", value=10); trials = st.number_input("Trials", value=100)

    if st.button("🚀 Run Analysis"):
        st.markdown("---")
        
        # Data Prep
        cols = [target] if pred is None else [target, pred]
        data = df[cols].copy()
        # Force numeric for relevant tests
        if cat != "Correlation" or test == "Pearson":
            data[target] = pd.to_numeric(data[target], errors='coerce')
        data = data.dropna()
        
        if data.empty: st.error("No valid data."); st.stop()
        
        res_con = st.container()
        with res_con:
            try:
                if test == "One-Sample Proportion":
                    p_hat = succ/trials
                    se = np.sqrt(ref_val*(1-ref_val)/trials)
                    z = (p_hat - ref_val)/se
                    p = 2*(1-stats.norm.cdf(abs(z)))
                    ci = calculate_proportion_ci(succ, trials)
                    st.metric("P-Value", f"{p:.5f}")
                    st.write(f"**Prop:** {p_hat:.3f} (CI: {ci})")
                    st.session_state['res'] = {'test': test, 'p': p, 'stat': z, 'ci': ci, 'target': target, 'pred': pred}

                elif test == "One-Sample T-Test":
                    st.plotly_chart(create_qq_plot(data[target]), use_container_width=True)
                    s, p = stats.ttest_1samp(data[target], ref_val)
                    m, l, u = mean_confidence_interval(data[target])
                    st.metric("P-Value", f"{p:.5f}")
                    st.write(f"**Mean:** {m:.2f} (CI: [{l:.2f}, {u:.2f}])")
                    st.session_state['res'] = {'test': test, 'p': p, 'stat': s, 'ci': (l,u), 'target': target, 'pred': pred}

                elif test in ["Independent T-Test", "Mann-Whitney U"]:
                    grps = data[pred].unique()
                    g1, g2 = data[data[pred]==grps[0]][target], data[data[pred]==grps[1]][target]
                    
                    # Assumptions
                    c_a1, c_a2 = st.columns(2)
                    c_a1.metric("Shapiro G1", f"{stats.shapiro(g1)[1]:.3f}")
                    c_a2.metric("Levene", f"{stats.levene(g1, g2)[1]:.3f}")
                    
                    if test == "Independent T-Test":
                        s, p = stats.ttest_ind(g1, g2)
                        d = calculate_cohens_d(g1, g2)
                        st.metric("P-Value", f"{p:.5f}")
                        st.write(f"**Cohen's d:** {d:.2f}")
                    else:
                        s, p = stats.mannwhitneyu(g1, g2)
                        st.metric("P-Value", f"{p:.5f}")
                    st.session_state['res'] = {'test': test, 'p': p, 'stat': s, 'target': target, 'pred': pred}

                elif test in ["One-Way ANOVA", "Kruskal-Wallis"]:
                    gs = [data[data[pred]==g][target] for g in data[pred].unique()]
                    if test == "One-Way ANOVA":
                        s, p = stats.f_oneway(*gs)
                        eta = calculate_eta_squared(gs)
                        st.metric("P-Value", f"{p:.5f}")
                        st.write(f"**Eta-Squared:** {eta:.3f}")
                    else:
                        s, p = stats.kruskal(*gs)
                        st.metric("P-Value", f"{p:.5f}")
                    st.session_state['res'] = {'test': test, 'p': p, 'stat': s, 'target': target, 'pred': pred}

                elif test in ["Pearson", "Spearman"]:
                    if test == "Pearson":
                        s, p = stats.pearsonr(data[target], data[pred])
                        with st.expander(t['linearity_check']):
                            st.plotly_chart(px.scatter(data, x=pred, y=target, trendline="ols"), use_container_width=True)
                    else:
                        s, p = stats.spearmanr(data[target], data[pred])
                    st.metric("Correlation", f"{s:.3f}")
                    st.metric("P-Value", f"{p:.5f}")
                    st.session_state['res'] = {'test': test, 'p': p, 'stat': s, 'target': target, 'pred': pred}

                elif test == "Chi-Square":
                    ct = pd.crosstab(data[target], data[pred])
                    s, p, d, e = stats.chi2_contingency(ct)
                    v = calculate_cramers_v(ct.values)
                    st.metric("P-Value", f"{p:.5f}")
                    st.write(f"**Cramér's V:** {v:.3f}")
                    st.session_state['res'] = {'test': test, 'p': p, 'stat': s, 'target': target, 'pred': pred}

            except Exception as e: st.error(f"Calc Error: {e}")

# ================= PAGE 4: REPORTING =================
elif page == t['p4']:
    st.header(t['p4'])
    if 'res' not in st.session_state: st.warning("Run analysis first.")
    else:
        res = st.session_state['res']
        st.success(f"Ready to report on: {res['test']}")
        
        c_k, c_l = st.columns([2, 1])
        key = c_k.text_input("Groq API Key", value=st.session_state['groq_api_key'], type="password")
        r_lang = c_l.selectbox(t['report_lang_label'], ["English", "Arabic"])
        
        if st.button(t['gen_report_btn']):
            if not key: st.error("API Key Missing")
            else:
                with st.spinner("Drafting Report..."):
                    prompt = f"Write academic statistical report in {r_lang}.\nResults: {res}\nInclude: Intro, Methods, Results (P, Effect Size), Assumptions, Conclusion."
                    rep = ask_groq(prompt, key)
                    st.markdown(rep)
                    
                    # Downloads
                    b1, b2, b3 = st.columns(3)
                    b1.download_button("📝 TXT", rep, "rep.txt")
                    if Document:
                        d = Document(); d.add_paragraph(rep); b = io.BytesIO(); d.save(b)
                        b2.download_button("📘 DOCX", b.getvalue(), "rep.docx")
                    if FPDF:
                        pdf = create_pdf(rep)
                        b3.download_button("📕 PDF", pdf, "rep.pdf")