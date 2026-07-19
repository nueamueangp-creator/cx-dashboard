import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าแดชบอร์ด
st.set_page_config(page_title="1577 CX Performance Control", layout="wide", initial_sidebar_state="expanded")

# 🔗 ลิงก์ CSV ของคุณ
sheet_csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRSLXaX4OFmcO8xhcoKllNThw3tFBbVCRETb5X9n6Q4gTc4Rudd9d5_wS7UZXKHm8BVVtzzq1sWgxAN/pub?output=csv"

try:
    # 2. ดึงข้อมูลและจัดการประเภทข้อมูล
    df = pd.read_csv(sheet_csv_url)
    if "วันที่ประเมิน" in df.columns:
        df["วันที่ประเมิน"] = pd.to_datetime(df["วันที่ประเมิน"])
        df = df.sort_values(by="วันที่ประเมิน")
    
    # คำนวณค่าคงที่สำหรับโพยพรีเซ็นต์ (คำนวณจากข้อมูลดิบก่อนฟิลเตอร์)
    agent_means_all = df.groupby("ชื่อ")["Table5.คะแนน"].mean()
    lowest_agent = agent_means_all.idxmin()
    lowest_score = agent_means_all.min()
    highest_agent = agent_means_all.idxmax()
    highest_score = agent_means_all.max()
    TARGET_SCORE = 20
    failed_percentage_all = (len(df[df["Table5.คะแนน"] < TARGET_SCORE]) / len(df)) * 100

except Exception as e:
    st.error("❌ เกิดข้อผิดพลาดในการโหลดข้อมูล")
    st.stop()

# =========================================================================
# 🎛️ ส่วนที่ 2: ระบบตัวกรองข้อมูล (SIDEBAR FILTERS)
# =========================================================================
st.sidebar.header("🔍 ตัวกรองแดชบอร์ด")
st.sidebar.markdown("---")

# ฟิลเตอร์รายชื่อพนักงาน
all_agents = sorted(df["ชื่อ"].dropna().unique())
selected_agents = st.sidebar.multiselect("👤 เลือกพนักงาน:", all_agents, default=all_agents)

# ฟิลเตอร์เกรดผลงาน
all_grades = sorted(df["Performance by personal"].dropna().unique())
selected_grades = st.sidebar.multiselect("🏅 เลือกเกรดประเมิน:", all_grades, default=all_grades)

# ตัวกรองช่วงคะแนน
min_score, max_score = int(df["Table5.คะแนน"].min()), int(df["Table5.คะแนน"].max())
score_range = st.sidebar.slider("📊 ช่วงคะแนนที่ต้องการดู:", min_score, max_score, (min_score, max_score))

# บังคับใช้ฟิลเตอร์ลงในข้อมูล
df_filtered = df[
    (df["ชื่อ"].isin(selected_agents)) & 
    (df["Performance by personal"].isin(selected_grades)) &
    (df["Table5.คะแนน"] >= score_range[0]) &
    (df["Table5.คะแนน"] <= score_range[1])
]

# คำนวณค่าสถิติตามตัวกรอง
total_records = len(df_filtered)
if total_records > 0:
    avg_score = df_filtered["Table5.คะแนน"].mean()
    avg_percentage = (avg_score / 25) * 100
    failed_cases = len(df_filtered[df_filtered["Table5.คะแนน"] < TARGET_SCORE])
    need_improve_count = len(df_filtered[df_filtered["Performance by personal"] == "Need Improve"])
else:
    st.warning("⚠️ ไม่พบข้อมูลที่ตรงกับตัวกรองของคุณ กรุณาปรับตัวกรองใหม่ที่แถบด้านข้าง")
    st.stop()

# =========================================================================
# 🎨 ส่วนที่ 3: หน้าตาแดชบอร์ด (UI)
# =========================================================================
st.markdown(
    f"""
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@400;600;700&family=Sarabun:wght@400;500;700&display=swap" rel="stylesheet">
    <style> * {{ font-family: 'Sarabun', sans-serif; }} h1, h2, h3, h4 {{ font-family: 'Prompt', sans-serif; }} </style>
    
    <header class="bg-slate-900 text-white rounded-2xl p-5 mb-6 flex items-center justify-between border border-slate-800 shadow-lg">
        <div>
            <h1 class="text-xl font-bold text-white">1577 CX Performance Control & Quality Radar</h1>
            <p class="text-xs text-slate-400 mt-0.5">แดชบอร์ดวิเคราะห์และควบคุมคุณภาพงานบริการลูกค้า (Interactive Version)</p>
        </div>
        <div class="text-xs bg-slate-800 px-3 py-1.5 rounded-xl border border-slate-700 text-slate-300">
            📊 แสดงข้อมูลตามตัวกรอง: <b>{total_records} เคส</b>
        </div>
    </header>
    """,
    unsafe_allow_html=True
)

# 🤫 1) โพยย่อสำหรับพรีเซ็นต์ (ซ่อนไว้ คลิกเปิดได้ตอนจะพูด)
with st.expander("💡 [คลิกเพื่อเปิด] โพยย่อข้อมูลเชิงลึกสำหรับใช้พูดพรีเซ็นต์ (Presenter Cheatsheet)"):
    st.markdown(f"""
    * **จุดวิกฤตสูงสุดของแผนก:** ภาพรวมทั้งระบบมีเคสตกเกณฑ์มาตรฐาน (ต่ำกว่า 20 คะแนน) สูงถึง **{failed_percentage_all:.1f}%**
    * **การจัดการรายบุคคล:** คุณ **{lowest_agent}** คะแนนเฉลี่ยต่ำสุด (**{lowest_score:.2f}**) ต้องเข้า Coaching / คุณ **{highest_agent}** สูงสุด (**{highest_score:.2f}**) เหมาะเป็นหัวหน้าทีมคู่หู
    * *โน้ตเพิ่มเติม:* คุณสามารถกดติ๊กเลือกชื่อ หรือเกรดที่แถบเมนูด้านซ้ายมือ เพื่อเจาะลึกข้อมูลสดบนหน้าจอโชว์เจ้านายได้ทันทีระหว่างพรีเซ็นต์
    """)

# 📊 สรุปตัวเลขสำคัญ (KPI Cards)
st.markdown("### 📌 ตัวชี้วัดสำคัญ (Key Metrics)")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("จำนวนเคสที่ตรวจสอบ", f"{total_records} รายการ")
with kpi2:
    st.metric("คะแนนเฉลี่ย (ตัวกรองปัจจุบัน)", f"{avg_score:.2f} / 25")
with kpi3:
    st.metric("เปอร์เซ็นต์ประสิทธิภาพ", f"{avg_percentage:.1f}%")
with kpi4:
    st.metric("เคสวิกฤต Need Improve", f"{need_improve_count} เคส", delta=f"ตกเกณฑ์ {failed_cases} เคส", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

# 📈 โซนกราฟแถวที่ 1: การจัดอันดับและแนวโน้ม
st.markdown("### 📈 อันดับผลงานและแนวโน้มคุณภาพ")
col1, col2 = st.columns(2)

with col1:
    df_agent = df_filtered.groupby("ชื่อ")["Table5.คะแนน"].mean().reset_index().sort_values(by="Table5.คะแนน")
    fig_bar = px.bar(df_agent, x="Table5.คะแนน", y="ชื่อ", orientation='h',
                     title="คะแนนเฉลี่ยรายบุคคล (เปรียบเทียบกับเกณฑ์เป้าหมาย)",
                     color="Table5.คะแนน", color_continuous_scale="RdYlGn")
    fig_bar.add_vline(x=TARGET_SCORE, line_dash="dash", line_color="red", annotation_text="เกณฑ์ผ่าน (20)")
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    if "วันที่ประเมิน" in df_filtered.columns:
        df_trend = df_filtered.groupby("วันที่ประเมิน")["Table5.คะแนน"].mean().reset_index()
        fig_line = px.line(df_trend, x="วันที่ประเมิน", y="Table5.คะแนน", title="แนวโน้มคุณภาพบริการรายวัน (Timeline Trend)", markers=True)
        fig_line.add_hline(y=TARGET_SCORE, line_dash="dash", line_color="red")
        st.plotly_chart(fig_line, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# 📊 โซนกราฟแถวที่ 2: กราฟแบ่งกลุ่ม และ กราฟความเสถียร
st.markdown("### 🔍 เจาะลึกการแบ่งกลุ่มพนักงานและความเสถียรของคุณภาพ")
col3, col4 = st.columns(2)

with col3:
    fig_stack = px.bar(
        df_filtered, y="ชื่อ", color="Performance by personal",
        title="สัดส่วนเกรดประเมินที่ได้รับแบ่งกลุ่มรายบุคคล",
        labels={"Performance by personal": "เกรดผลงาน"},
        category_orders={"Performance by personal": ["Excellent", "Good", "Fair", "Need Improve"]},
        color_discrete_map={"Excellent": "#22c55e", "Good": "#3b82f6", "Fair": "#eab308", "Need Improve": "#ef4444"}
    )
    st.plotly_chart(fig_stack, use_container_width=True)

with col4:
    fig_box = px.box(
        df_filtered, x="ชื่อ", y="Table5.คะแนน", 
        title="วิเคราะห์ความเสถียรของคุณภาพบริการ (ความกว้างกล่อง = คะแนนแกว่ง)", color="ชื่อ"
    )
    st.plotly_chart(fig_box, use_container_width=True)

# =========================================================================
# 🧮 ส่วนที่ 4: ตาราง PIVOT TABLE แบบเดียวกับ Excel (ตามภาพบรีฟชุดใหม่)
# =========================================================================
st.markdown("---")
st.markdown("### 🗂️ ตารางสรุปข้อมูลประเมินผลไขว้รายวัน (Pivot Table แบบ Excel)")

if "วันที่ประเมิน" in df_filtered.columns and not df_filtered.empty:
    # คัดลอกข้อมูลมาทำตารางแยกเพื่อไม่ให้กระทบกราฟ
    df_pivot_prep = df_filtered.copy()
    
    # จัดฟอร์แมตวันที่ให้สวยงามแบบใน Excel (วัน/เดือน/ปี ค.ศ.)
    df_pivot_prep["วันที่ประเมิน"] = df_pivot_prep["วันที่ประเมิน"].dt.strftime('%d/%m/%Y')
    
    # สั่งสร้าง Pivot Table: แถว = ชื่อ, คอลัมน์ = วันที่ประเมิน, ค่า = ผลรวมของคะแนน
    pivot_table = df_pivot_prep.pivot_table(
        index="ชื่อ",
        columns="วันที่ประเมิน",
        values="Table5.คะแนน",
        aggfunc="sum",
        fill_value=0
    )
    
    # ➕ คำนวณหา Grand Total แนวนอน (รวมขวา)
    pivot_table["Grand Total"] = pivot_table.sum(axis=1)
    
    # ➕ คำนวณหา Grand Total แนวตั้ง (รวมล่าง)
    pivot_table.loc["Grand Total"] = pivot_table.sum(axis=0)
    
    # แสดงตาราง Pivot Table ออกมาบนหน้าจอแบบสวยงาม
    st.dataframe(pivot_table, use_container_width=True)
else:
    st.info("💡 ไม่มีข้อมูลแสดงผลในตารางเนื่องจากตัวกรอง")
