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
    
    # 🎯 ตั้งค่าเกณฑ์คะแนน (คะแนนเต็ม 25 | เป้าหมาย 90% = 22.5 คะแนน)
    FULL_SCORE = 25
    TARGET_PERCENTAGE = 90
    TARGET_SCORE = FULL_SCORE * (TARGET_PERCENTAGE / 100) # 22.5 คะแนน

except Exception as e:
    st.error("❌ เกิดข้อผิดพลาดในการโหลดข้อมูล")
    st.stop()

# =========================================================================
# 🎛️ ส่วนที่ 2: ระบบตัวกรองข้อมูลแบบคลีน (CLEAN SIDEBAR FILTERS)
# =========================================================================
st.sidebar.header("🔍 ตัวกรองแดชบอร์ด")
st.sidebar.markdown("---")

# 👤 ตัวกรองรายชื่อพนักงาน
agent_filter_type = st.sidebar.radio("รูปแบบการเลือกพนักงาน:", ["แสดงพนักงานทุกคน (All)", "เลือกเฉพาะบางคน"])
all_agents = sorted(df["ชื่อ"].dropna().unique())

if agent_filter_type == "เลือกเฉพาะบางคน":
    selected_agents = st.sidebar.multiselect("เลือกชื่อพนักงาน:", all_agents, default=all_agents[:2])
    df_filtered = df[df["ชื่อ"].isin(selected_agents)]
else:
    df_filtered = df.copy()

# 🏅 ตัวกรองเกรดผลงาน
all_grades = sorted(df["Performance by personal"].dropna().unique())
selected_grade = st.sidebar.selectbox("🏅 เลือกเกรดประเมิน:", ["ทั้งหมด (All)"] + all_grades)

if selected_grade != "ทั้งหมด (All)":
    df_filtered = df_filtered[df_filtered["Performance by personal"] == selected_grade]

# 📊 ตัวกรองช่วงคะแนน
min_score, max_score = int(df["Table5.คะแนน"].min()), int(df["Table5.คะแนน"].max())
score_range = st.sidebar.slider("📊 ช่วงคะแนนที่ต้องการดู:", min_score, max_score, (min_score, max_score))
df_filtered = df_filtered[(df_filtered["Table5.คะแนน"] >= score_range[0]) & (df_filtered["Table5.คะแนน"] <= score_range[1])]

# คำนวณค่าสถิติตามตัวกรอง
total_records = len(df_filtered)
if total_records > 0:
    avg_score = df_filtered["Table5.คะแนน"].mean()
    avg_percentage = (avg_score / FULL_SCORE) * 100
    above_target_cases = len(df_filtered[df_filtered["Table5.คะแนน"] >= TARGET_SCORE])
    above_target_pct = (above_target_cases / total_records) * 100
else:
    st.warning("⚠️ ไม่พบข้อมูลที่ตรงกับตัวกรองของคุณ กรุณาปรับตัวกรองใหม่ที่แถบด้านข้าง")
    st.stop()

# =========================================================================
# 🎨 ส่วนที่ 3: หน้าตาแดชบอร์ด (UI)
# =========================================================================
header_html = f"""
<div style="background-color: #0f172a; color: white; border-radius: 1rem; padding: 1.25rem; margin-bottom: 1.5rem; border: 1px solid #1e293b; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div>
            <h1 style="font-size: 1.25rem; font-weight: bold; color: white; margin: 0; font-family: sans-serif;">1577 CX Performance Control & Quality Radar</h1>
            <p style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.125rem; margin-bottom: 0;">ระบบวิเคราะห์และควบคุมคุณภาพงานบริการลูกค้าตามเป้าหมาย 90%</p>
        </div>
        <div style="font-size: 0.75rem; background-color: #1e293b; padding: 0.375rem 0.75rem; border-radius: 0.75rem; border: 1px solid #334155; color: #cbd5e1;">
            📊 ข้อมูลตามตัวกรอง: <b>{total_records} เคส</b>
        </div>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# 📊 สรุปตัวเลขสำคัญเปรียบเทียบกับเป้าหมาย 90% (KPI Cards)
st.markdown("### 📌 ตัวชี้วัดประสิทธิภาพเทียบกับเป้าหมาย 90%")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("คะแนนเต็มต่อเคส", f"{FULL_SCORE} คะแนน")
with kpi2:
    st.metric("คะแนนเฉลี่ยปัจจุบันที่ทำได้", f"{avg_score:.2f} / {FULL_SCORE}", delta=f"คิดเป็น {avg_percentage:.1f}% ของเต็ม")
with kpi3:
    st.metric(f"คะแนนเป้าหมาย ({TARGET_PERCENTAGE}%)", f"{TARGET_SCORE:.2f} คะแนน", delta=f"ขาดอีก {(TARGET_SCORE - avg_score):.2f}" if avg_score < TARGET_SCORE else "บรรลุเป้าหมายแล้ว ✨")
with kpi4:
    st.metric("สัดส่วนเคสที่ผ่านเกณฑ์ 90%", f"{above_target_cases} เคส", delta=f"{above_target_pct:.1f}% ของเคสทั้งหมด")

st.markdown("<br>", unsafe_allow_html=True)

# 📈 โซนกราฟแถวที่ 1: การจัดอันดับและแนวโน้ม
st.markdown("### 📈 อันดับผลงานและแนวโน้มคุณภาพ")
col1, col2 = st.columns(2)

with col1:
    df_agent = df_filtered.groupby("ชื่อ")["Table5.คะแนน"].mean().reset_index().sort_values(by="Table5.คะแนน")
    fig_bar = px.bar(df_agent, x="Table5.คะแนน", y="ชื่อ", orientation='h',
                     title=f"คะแนนเฉลี่ยรายบุคคล (เปรียบเทียบกับเป้าหมาย {TARGET_PERCENTAGE}%)",
                     color="Table5.คะแนน", color_continuous_scale="RdYlGn")
    fig_bar.add_vline(x=TARGET_SCORE, line_dash="dash", line_color="blue", annotation_text=f"เป้าหมาย 90% ({TARGET_SCORE})", annotation_position="top right")
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    if "วันที่ประเมิน" in df_filtered.columns:
        df_trend = df_filtered.groupby("วันที่ประเมิน")["Table5.คะแนน"].mean().reset_index()
        fig_line = px.line(df_trend, x="วันที่ประเมิน", y="Table5.คะแนน", title="แนวโน้มคุณภาพบริการรายวัน (Timeline Trend)", markers=True)
        fig_line.add_hline(y=TARGET_SCORE, line_dash="dash", line_color="blue")
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
# 🧮 ส่วนที่ 4: ตารางสรุปข้อมูลประเมินผลไขว้รายวัน (+ คำนวณ % รายบรรทัด)
# =========================================================================
st.markdown("---")
st.markdown("### 🗂️ ตารางสรุปข้อมูลประเมินผลไขว้รายวัน")

if "วันที่ประเมิน" in df_filtered.columns and not df_filtered.empty:
    df_pivot_prep = df_filtered.copy()
    
    # นับจำนวนวันที่พนักงานแต่ละคนถูกประเมินจริง (เพื่อหาคะแนนเต็มส่วนบุคคล)
    # เช่น ทำงาน 4 วัน คะแนนเต็มควรจะเป็น 4 * 25 = 100 คะแนน
    work_days_per_agent = df_pivot_prep.groupby("ชื่อ")["วันที่ประเมิน"].nunique()
    
    # แปลงรูปแบบวันที่เพื่อใช้เป็นหัวคอลัมน์
    df_pivot_prep["วันที่ประเมิน"] = df_pivot_prep["วันที่ประเมิน"].dt.strftime('%d/%m/%Y')
    
    # สร้างตาราง Pivot
    pivot_table = df_pivot_prep.pivot_table(
        index="ชื่อ",
        columns="วันที่ประเมิน",
        values="Table5.คะแนน",
        aggfunc="sum",
        fill_value=0
    )
    
    # 1. คำนวณผลรวมคะแนนดิบที่ทำได้จริง (Grand Total)
    pivot_table["Grand Total"] = pivot_table.sum(axis=1)
    
    # 2. คำนวณประสิทธิภาพเทียบกับคะแนนเต็มส่วนบุคคลรายบรรทัด
    percentage_list = []
    for agent_name in pivot_table.index:
        actual_total = pivot_table.loc[agent_name, "Grand Total"]
        days = work_days_per_agent.get(agent_name, 1) # ดึงจำนวนวันที่ประเมินจริง
        possible_full_score = days * FULL_SCORE       # คะแนนเต็มสูงสุดที่ควรได้
        
        pct = (actual_total / possible_full_score) * 100
        percentage_list.append(f"{pct:.1f}%")
        
    pivot_table["% Achievement (เทียบเต็ม)"] = percentage_list
    
    # 3. เพิ่มบรรทัดสรุปรวมท้ายตาราง (Grand Total รวมล่าง)
    # สำหรับคอลัมน์วันที่และ Grand Total ให้ใช้ผลรวม
    total_row = pivot_table.drop(columns=["% Achievement (เทียบเต็ม)"]).sum(axis=0)
    
    # สำหรับ % รวมท้ายตาราง ให้คิดจาก (ผลรวมทั้งหมด / (จำนวนเคสทั้งหมด * 25))
    total_possible_all = len(df_filtered) * FULL_SCORE
    total_pct_all = (total_row["Grand Total"] / total_possible_all) * 100
    
    # บันทึกลงแถว Grand Total ล่างสุด
    pivot_table.loc["Grand Total"] = list(total_row) + [f"{total_pct_all:.1f}%"]
    
    # แสดงตารางผลลัพธ์
    st.dataframe(pivot_table, use_container_width=True)
else:
    st.info("💡 ไม่มีข้อมูลแสดงผลในตารางเนื่องจากตัวกรอง")
