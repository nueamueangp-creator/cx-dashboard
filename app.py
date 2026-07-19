import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

# 📅 ตัวกรองช่วงวันที่ประเมิน
if "วันที่ประเมิน" in df.columns:
    min_date = df["วันที่ประเมิน"].min().date()
    max_date = df["วันที่ประเมิน"].max().date()
    
    st.sidebar.subheader("📅 เลือกช่วงวันที่ประเมิน")
    selected_date_range = st.sidebar.date_input(
        "ช่วงเวลาที่ต้องการดู:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
        start_date, end_date = selected_date_range
        df_filtered = df[(df["วันที่ประเมิน"].dt.date >= start_date) & (df["วันที่ประเมิน"].dt.date <= end_date)]
    else:
        df_filtered = df.copy()
else:
    df_filtered = df.copy()

# 👤 ตัวกรองรายชื่อพนักงาน
agent_filter_type = st.sidebar.radio("รูปแบบการเลือกพนักงาน:", ["แสดงพนักงานทุกคน (All)", "เลือกเฉพาะบางคน"])
all_agents = sorted(df_filtered["ชื่อ"].dropna().unique())

if agent_filter_type == "เลือกเฉพาะบางคน":
    selected_agents = st.sidebar.multiselect("เลือกชื่อพนักงาน:", all_agents, default=all_agents[:2] if len(all_agents) > 1 else all_agents)
    df_filtered = df_filtered[df_filtered["ชื่อ"].isin(selected_agents)]

# 🏅 ตัวกรองเกรดผลงาน
all_grades = sorted(df_filtered["Performance by personal"].dropna().unique())
selected_grade = st.sidebar.selectbox("🏅 เลือกเกรดประเมิน:", ["ทั้งหมด (All)"] + all_grades)

if selected_grade != "ทั้งหมด (All)":
    df_filtered = df_filtered[df_filtered["Performance by personal"] == selected_grade]

# 📊 ตัวกรองช่วงคะแนน
if not df_filtered.empty:
    min_score, max_score = int(df_filtered["Table5.คะแนน"].min()), int(df_filtered["Table5.คะแนน"].max())
    if min_score != max_score:
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
        # 1. จัดกลุ่มข้อมูลเพื่อดึงยอดรวมสะสมคะแนน และจำนวนเคสที่ประเมินแยกเป็นรายวัน
        df_trend = df_filtered.groupby("วันที่ประเมิน").agg(
            Sum_Score=("Table5.คะแนน", "sum"),
            Count_Cases=("Table5.คะแนน", "count")
        ).reset_index()
        
        # 2. คำนวณเปอร์เซ็นต์ผลสัมฤทธิ์สะสมของแต่ละวัน และจัดแต่งข้อความของแกนและเลเบล
        df_trend["Max_Possible"] = df_trend["Count_Cases"] * FULL_SCORE
        df_trend["Pct_Score"] = (df_trend["Sum_Score"] / df_trend["Max_Possible"]) * 100
        df_trend["Pct_Text"] = df_trend["Pct_Score"].apply(lambda x: f"{round(x)}%")
        df_trend["วันที่_แสดงผล"] = df_trend["วันที่ประเมิน"].dt.strftime('%d/%m/%Y')
        
        # 3. สร้างกราฟที่มี 2 แกน Y ร่วมกัน (Dual-Axis)
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        
        # 4. เพิ่มแผนภูมิแท่ง (Bar Chart) คะแนนสะสมจริง (Qty) ที่แกนหลักฝั่งซ้าย
        fig_trend.add_trace(
            go.Bar(
                x=df_trend["วันที่_แสดงผล"],
                y=df_trend["Sum_Score"],
                name="คะแนนดิบสะสมรวม (Qty)",
                marker=dict(color="#1a5f7a"),
                text=df_trend["Sum_Score"],
                textposition="inside",
                insidetextanchor="bottom",
                textfont=dict(color="white", size=14, family="sans-serif", weight="bold"),
                hovertemplate="วันที่: %{x}<br>คะแนนรวม: %{y} คะแนน<extra></extra>"
            ),
            secondary_y=False
        )
        
        # 5. เพิ่มแผนภูมิเส้น (Line Chart) อัตราความสำเร็จ (%) ที่แกนรองฝั่งขวา
        fig_trend.add_trace(
            go.Scatter(
                x=df_trend["วันที่_แสดงผล"],
                y=df_trend["Pct_Score"],
                name="เปอร์เซ็นต์อัตราความสำเร็จ (%)",
                mode="lines+markers+text",
                line=dict(color="#ea580c", width=4),
                marker=dict(size=12, symbol="circle", color="#ea580c"),
                text=df_trend["Pct_Text"],
                textposition="top center",
                textfont=dict(color="#1e293b", size=13, family="sans-serif", weight="bold"),
                hovertemplate="วันที่: %{x}<br>เปอร์เซ็นต์: %{text}<extra></extra>"
            ),
            secondary_y=True
        )
        
        # 6. ตั้งค่าการจัดแต่งรูปแบบกราฟให้เหมือนกับรูป Excel ที่ส่งมาเป๊ะๆ
        fig_trend.update_layout(
            title="แนวโน้มคะแนนสะสมและเปอร์เซ็นต์ผลงานทีมรายวัน (Qty & % Achievement)",
            titlefont=dict(size=16, color="#0f172a", family="sans-serif", weight="bold"),
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=40, r=40, t=50, b=40),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.08,
                xanchor="right",
                x=1
            ),
            xaxis=dict(
                showgrid=False,
                type='category',
                tickfont=dict(size=12, color="#64748b")
            ),
            yaxis=dict(
                title="คะแนนดิบสะสมรวม (Qty)",
                titlefont=dict(color="#1a5f7a", size=12),
                tickfont=dict(color="#1a5f7a"),
                showgrid=True,
                gridcolor="#f1f5f9"
            ),
            yaxis2=dict(
                title="เปอร์เซ็นต์อัตราความสำเร็จ (%)",
                titlefont=dict(color="#ea580c", size=12),
                tickfont=dict(color="#ea580c"),
                range=[0, 110],  # เผื่อพื้นที่ด้านบนเพื่อให้ตัวเลเบล 92% ไม่ตกขอบ
                showgrid=False,
                ticksuffix="%"
            )
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# 📊 โซนกราฟแถวที่ 2: กราฟความเสถียรขยายเต็มหน้าจอ
st.markdown("### 🔍 เจาะลึกความเสถียรของคุณภาพบริการ")

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
    title="วิเคราะห์ความเสถียรของคุณภาพบริการรายบุคคล (เส้นหนวดยิ่งแคบ = คุณภาพบริการยิ่งเสถียรคงเส้นคงวา)",
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
    yaxis_title="คะแนนเสถียรภาพ (Median)",
    height=450
)
st.plotly_chart(fig_custom_box, use_container_width=True)

# =========================================================================
# 🧮 ส่วนที่ 4: ตารางสรุปข้อมูลประเมินผลไขว้รายวัน (ปรับปรุงตำแหน่งคอลัมน์)
# =========================================================================
st.markdown("---")
st.markdown("### 🗂️ ตารางสรุปข้อมูลประเมินผลไขว้รายวัน")

if "วันที่ประเมิน" in df_filtered.columns and not df_filtered.empty:
    df_pivot_prep = df_filtered.copy()
    work_days_per_agent = df_pivot_prep.groupby("ชื่อ")["วันที่ประเมิน"].nunique()
    
    agent_grade_map = df_pivot_prep.groupby("ชื่อ")["Performance by personal"].last().to_dict()
    df_pivot_prep["วันที่ประเมิน"] = df_pivot_prep["วันที่ประเมิน"].dt.strftime('%d/%m/%Y')
    
    # สร้าง Pivot Table (เริ่มต้นจะมีเฉพาะ คอลัมน์วันที่รายวัน)
    pivot_table = df_pivot_prep.pivot_table(
        index="ชื่อ", columns="วันที่ประเมิน", values="Table5.คะแนน", aggfunc="sum", fill_value=0
    )
    
    # 1. คำนวณผลรวมคะแนนดิบรายคน (Grand Total) ต่อท้ายกลุ่มคอลัมน์วันที่
    date_columns = list(pivot_table.columns)
    pivot_table["Grand Total"] = pivot_table[date_columns].sum(axis=1)
    
    # 2. คำนวณ % Achievement รายบุคคล
    percentage_list = []
    for agent_name in pivot_table.index:
        actual_total = pivot_table.loc[agent_name, "Grand Total"]
        days = work_days_per_agent.get(agent_name, 1)
        possible_full_score = days * FULL_SCORE
        pct = (actual_total / possible_full_score) * 100
        percentage_list.append(f"{pct:.1f}%")
        
    pivot_table["% Achievement (เทียบเต็ม)"] = percentage_list
    
    # 💥 [ปรับปรุงใหม่] 3. ใส่กลุ่มผลงานปัจจุบันต่อท้ายสุด อยู่ข้างๆ % ตามที่ต้องการ
    grade_list = [agent_grade_map.get(agent_name, "-") for agent_name in pivot_table.index]
    pivot_table["กลุ่มผลงานปัจจุบัน"] = grade_list
    
    # 4. แสดงผลรวมสะสมภาพรวมทั้งหมดบนหัวตาราง
    total_score_sum = pivot_table["Grand Total"].sum()
    total_possible_all = len(df_filtered) * FULL_SCORE
    total_pct_all = (total_score_sum / total_possible_all) * 100
    
    st.success(f"📊 **ภาพรวมของพนักงานทั้งหมดที่ถูกเลือก:** คะแนนสะสมรวมกันทำได้จริง **{int(total_score_sum):,} / {int(total_possible_all):,} คะแนน** (คิดเป็นเฉลี่ยรวม **{total_pct_all:.1f}%** จากคะแนนเต็มทั้งหมด)")
    
    # 5. แสดงผลตารางคลีนๆ ไม่มีแถวรวมให้รกสายตา
    st.dataframe(pivot_table, use_container_width=True)
else:
    st.info("💡 ไม่มีข้อมูลแสดงผลในตารางเนื่องจากตัวกรอง")
