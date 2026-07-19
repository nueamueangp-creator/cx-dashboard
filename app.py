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
    sum_actual_score = df_filtered["Table5.คะแนน"].sum()
    sum_possible_score = total_records * FULL_SCORE
    
    avg_score = df_filtered["Table5.คะแนน"].mean()
    avg_percentage = (sum_actual_score / sum_possible_score) * 100
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

# 📋 แสดงเกณฑ์การแบ่งเกรดผลงาน (Grading Rule Criteria)
with st.expander("📋 คลิกเพื่อดูเกณฑ์การประเมินและแบ่งเกรดพนักงาน (Grading Criteria)", expanded=True):
    gc1, gc2, gc3, gc4 = st.columns(4)
    gc1.markdown("🟢 **Excellent (ดีเยี่ยม)**<br>คะแนนเฉลี่ย: **มากกว่า 22.5 คะแนน**<br>*(บรรลุเป้าหมายที่ตั้งไว้ 90% ขึ้นไป)*", unsafe_allow_html=True)
    gc2.markdown("🔵 **Good (ดีตามมาตรฐาน)**<br>คะแนนเฉลี่ย: **20.0 - 22.5 คะแนน**<br>*(อยู่ในเกณฑ์มาตรฐานการบริการที่ดี)*", unsafe_allow_html=True)
    gc3.markdown("🟡 **Fair (พอใช้)**<br>คะแนนเฉลี่ย: **15.0 - 19.9 คะแนน**<br>*(ต่ำกว่าเป้าหมายเล็กน้อย ต้องปรับปรุง)*", unsafe_allow_html=True)
    gc4.markdown("🔴 **Need Improve (ต้องปรับปรุงด่วน)**<br>คะแนนเฉลี่ย: **ต่ำกว่า 15.0 คะแนน**<br>*(ผลงานหลุดเกณฑ์วิกฤต ต้องได้รับการโค้ช)*", unsafe_allow_html=True)

st.markdown("---")

# 📊 สรุปตัวเลขสำคัญเปรียบเทียบกับเป้าหมาย 90% (KPI Cards)
st.markdown("### 📌 ตัวชี้วัดประสิทธิภาพเทียบกับเป้าหมาย 90%")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("คะแนนเต็มต่อเคส", f"{FULL_SCORE} คะแนน")
with kpi2:
    st.metric("คะแนนสะสมที่ทำได้จริงทั้งหมด", f"{int(sum_actual_score):,} / {int(sum_possible_score):,}", delta=f"คิดเป็น {avg_percentage:.1f}% ของคะแนนเต็ม")
with kpi3:
    st.metric(f"คะแนนเป้าหมายเฉลี่ย ({TARGET_PERCENTAGE}%)", f"{TARGET_SCORE:.2f} คะแนน", delta=f"ค่าเฉลี่ยขาดอีก {(TARGET_SCORE - avg_score):.2f}" if avg_score < TARGET_SCORE else "ค่าเฉลี่ยบรรลุเป้าหมายแล้ว ✨")
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

# 📊 โซนกราฟแถวที่ 2: แสดงกราฟความเสถียรคู่กับพื้นที่ว่างเพื่อความโปร่งสบายตา
st.markdown("### 🔍 เจาะลึกความเสถียรของคุณภาพบริการ")
col3, col4 = st.columns(2)

with col3:
    st.info("💡 เคล็ดลับการดูฝั่งขวา: ความกว้างของเส้นหนวดดำ ยิ่งยาวยิ่งแปลว่าพนักงานคนนั้นอารมณ์หรือคุณภาพงานแกว่งสูงในแต่ละเคส ซึ่งส่งผลต่อคะแนนความคงเส้นคงวาในการบริการลูกค้า")

with col4:
    df_box_stat = df_filtered.groupby("ชื่อ")["Table5.คะแนน"].agg(
        Max="max",
        Median="median",
        Min="min"
    ).reset_index()
    
    df_box_stat["error_plus"] = df_box_stat["Max"] - df_box_stat["Median"]
    df_box_stat["error_minus"] = df_box_stat["Median"] - df_box_stat["Min"]

    fig_custom_box = px.bar(
        df_box_stat, x="ชื่อ", y="Median",
        error_y="error_plus", error_y_minus="error_minus",
        title="วิเคราะห์ความเสถียรของคุณภาพบริการ (ความยาวเส้นหนวด = คะแนนแกว่ง)",
        color="ชื่อ"
    )

    fig_custom_box.update_traces(
        hovertemplate="<b>%{x}</b><br>" +
                      "คะแนนสูงสุด (Max): %{customdata[0]} คะแนน<br>" +
                      "คะแนนตรงกลาง (Median): %{y} คะแนน<br>" +
                      "คะแนนต่ำสุด (Min): %{customdata[1]} คะแนน<extra></extra>",
        customdata=df_box_stat[["Max", "Min"]].values
    )
    
    fig_custom_box.update_layout(
        hovermode="closest",
        yaxis_title="คะแนนเสถียรภาพ (Median)"
    )
    st.plotly_chart(fig_custom_box, use_container_width=True)

# =========================================================================
# 🧮 ส่วนที่ 4: ตารางสรุปข้อมูลประเมินผลไขว้รายวัน (+ เพิ่มกลุ่มเกรดผลงาน)
# =========================================================================
st.markdown("---")
st.markdown("### 🗂️ ตารางสรุปข้อมูลประเมินผลไขว้รายวัน")

if "วันที่ประเมิน" in df_filtered.columns and not df_filtered.empty:
    df_pivot_prep = df_filtered.copy()
    work_days_per_agent = df_pivot_prep.groupby("ชื่อ")["วันที่ประเมิน"].nunique()
    
    # ดึงค่ากลุ่มเกรดล่าสุดของพนักงานแต่ละคนมาจับคู่
    agent_grade_map = df_pivot_prep.groupby("ชื่อ")["Performance by personal"].last().to_dict()
    
    df_pivot_prep["วันที่ประเมิน"] = df_pivot_prep["วันที่ประเมิน"].dt.strftime('%d/%m/%Y')
    
    pivot_table = df_pivot_prep.pivot_table(
        index="ชื่อ", columns="วันที่ประเมิน", values="Table5.คะแนน", aggfunc="sum", fill_value=0
    )
    
    # 1. แทรกคอลัมน์กลุ่มเกรดผลงานไว้หน้าสุด
    pivot_table.insert(0, "กลุ่มผลงานปัจจุบัน", pivot_table.index.map(agent_grade_map))
    
    # 2. คำนวณผลรวมคะแนน
    # เลือกเฉพาะคอลัมน์วันที่ (ที่เป็นตัวเลขคะแนน) มา Sum ป้องกันการดึงคอลัมน์เกรดที่เป็น Text มารวม
    date_columns = [col for col in pivot_table.columns if col != "กลุ่มผลงานปัจจุบัน"]
    pivot_table["Grand Total"] = pivot_table[date_columns].sum(axis=1)
    
    # 3. คำนวณ % Achievement รายบุคคล
    percentage_list = []
    for agent_name in pivot_table.index:
        actual_total = pivot_table.loc[agent_name, "Grand Total"]
        days = work_days_per_agent.get(agent_name, 1)
        possible_full_score = days * FULL_SCORE
        pct = (actual_total / possible_full_score) * 100
        percentage_list.append(f"{pct:.1f}%")
        
    pivot_table["% Achievement (เทียบเต็ม)"] = percentage_list
    
    # 4. สร้างแถวรวม (Grand Total ของตารางด้านล่างสุด)
    total_row_data = {"กลุ่มผลงานปัจจุบัน": "-"}
    for col in date_columns:
        total_row_data[col] = pivot_table[col].sum()
    total_row_data["Grand Total"] = pivot_table["Grand Total"].sum()
    
    total_possible_all = len(df_filtered) * FULL_SCORE
    total_pct_all = (total_row_data["Grand Total"] / total_possible_all) * 100
    total_row_data["% Achievement (เทียบเต็ม)"] = f"{total_pct_all:.1f}%"
    
    pivot_table.loc["Grand Total"] = total_row_data
    
    st.dataframe(pivot_table, use_container_width=True)
else:
    st.info("💡 ไม่มีข้อมูลแสดงผลในตารางเนื่องจากตัวกรอง")
