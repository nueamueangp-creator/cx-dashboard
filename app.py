import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =========================================================================
# 1. ตั้งค่าหน้าแดชบอร์ดและโหลดข้อมูล
# =========================================================================
st.set_page_config(page_title="1577 CX Performance Control", layout="wide", initial_sidebar_state="expanded")

# 🔗 ลิงก์ CSV ของคุณ
sheet_csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRSLXaX4OFmcO8xhcoKllNThw3tFBbVCRETb5X9n6Q4gTc4Rudd9d5_wS7UZXKHm8BVVtzzq1sWgxAN/pub?output=csv"

try:
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

# 🛠️ ฟังก์ชันกำหนดสีตามเกณฑ์จริง 
def get_color_by_score(score):
    if score > 22.5:
        return "#10b981"  # 🟢 Excellent (เขียว)
    elif 20.0 <= score <= 22.5:
        return "#3b82f6"  # 🔵 Good (น้ำเงิน/ฟ้า)
    elif 15.0 <= score < 20.0:
        return "#f59e0b"  # 🟡 Fair (ส้ม/เหลือง)
    else:
        return "#ef4444"  # 🔴 Need Improve (แดง)

# =========================================================================
# 2. ระบบตัวกรองข้อมูลแถบข้าง (SIDEBAR FILTERS)
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
# 3. ส่วนหัวของหน้าและข้อมูลส่วนบน (UI HEADER & KPI CARDS)
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

# 📋 แสดงเกณฑ์การแบ่งเกรดผลงาน
with st.expander("📋 คลิกเพื่อดูเกณฑ์การประเมินและแบ่งเกรดพนักงาน (Grading Criteria)", expanded=True):
    gc1, gc2, gc3, gc4 = st.columns(4)
    gc1.markdown("🟢 **Excellent (ดีเยี่ยม)**<br>คะแนนเฉลี่ย: **มากกว่า 22.5 คะแนน**<br>*(บรรลุเป้าหมายที่ตั้งไว้ 90% ขึ้นไป)*", unsafe_allow_html=True)
    gc2.markdown("🔵 **Good (ดีตามมาตรฐาน)**<br>คะแนนเฉลี่ย: **20.0 - 22.5 คะแนน**<br>*(อยู่ในเกณฑ์มาตรฐานการบริการที่ดี)*", unsafe_allow_html=True)
    gc3.markdown("🟡 **Fair (พอใช้)**<br>คะแนนเฉลี่ย: **15.0 - 19.9 คะแนน**<br>*(ต่ำกว่าเป้าหมายเล็กน้อย ต้องปรับปรุง)*", unsafe_allow_html=True)
    gc4.markdown("🔴 **Need Improve (ต้องปรับปรุงด่วน)**<br>คะแนนเฉลี่ย: **ต่ำกว่า 15.0 คะแนน**<br>*(ผลงานหลุดเกณฑ์วิกฤต ต้องได้รับการโค้ช)*", unsafe_allow_html=True)

st.markdown("---")

# 📊 สรุปตัวเลขสำคัญเปรียบเทียบกับเป้าหมาย (KPI Cards)
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

# =========================================================================
# 4. โซนกราฟหลักส่วนบน: แบ่ง 2 คอลัมน์ (ซ้าย-ขวา เท่ากัน)
# =========================================================================
st.markdown("### 📈 อันดับผลงานและแนวโน้มคุณภาพ")
col1, col2 = st.columns(2)

# 👈 คอลัมน์ซ้าย: กราฟแท่งจัดอันดับคะแนนเฉลี่ยรายบุคคล (ล็อกสีตามเงื่อนไขจริง)
with col1:
    df_agent = df_filtered.groupby("Shift" if "Shift" in df_filtered.columns else "ชื่อ")["Table5.คะแนน"].mean().reset_index().sort_values(by="Table5.คะแนน")
    y_col = "Shift" if "Shift" in df_agent.columns else "ชื่อ"
    
    # คำนวณสีของแท่งรายบุคคลจากคะแนนจริง
    df_agent["color_group"] = df_agent["Table5.คะแนน"].apply(get_color_by_score)
    
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=df_agent["Table5.คะแนน"],
        y=df_agent[y_col],
        orientation='h',
        marker_color=df_agent["color_group"].tolist(), 
        text=df_agent["Table5.คะแนน"].round(2),
        textposition="inside",
        textfont=dict(color="white", weight="bold")
    ))
    
    fig_bar.add_vline(x=TARGET_SCORE, line_dash="dash", line_color="blue", annotation_text=f"เป้าหมาย 90% ({TARGET_SCORE})", annotation_position="top right")
    
    fig_bar.update_layout(
        title=f"คะแนนเฉลี่ยรายบุคคล (สีตามเกณฑ์ประเมินจริง)",
        xaxis_title="Table5.คะแนน",
        yaxis_title=y_col,
        height=650,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# 👉 คอลัมน์ขวา: กราฟแสดงแนวโน้มรายวันแบบแบ่ง 2 ชั้น (บน-ล่าง)
with col2:
    if "วันที่ประเมิน" in df_filtered.columns:
        df_trend = df_filtered.groupby("วันที่ประเมิน").agg(
            sum_score=("Table5.คะแนน", "sum"),
            count_cases=("Table5.คะแนน", "count")
        ).reset_index()
        
        df_trend["pct_score"] = (df_trend["sum_score"] / (df_trend["count_cases"] * FULL_SCORE)) * 100
        df_trend["วันที่_str"] = df_trend["วันที่ประเมิน"].dt.strftime('%d/%m/%Y')

        fig_split = make_subplots(
            rows=2, cols=1, 
            shared_xaxes=False, 
            vertical_spacing=0.18, 
            subplot_titles=("📈 แนวโน้ม % ประสิทธิภาพรายวัน (% Performance)", "📊 แนวโน้มคะแนนสะสมรวมรายวัน (Sum Score)")
        )

        # ชั้นบน: กราฟเส้น % ประสิทธิภาพ
        fig_split.add_trace(
            go.Scatter(
                x=df_trend["วันที่_str"],
                y=df_trend["pct_score"],
                name="% คะแนน",
                mode="lines+markers+text",
                line=dict(color="#e66f21", width=3),  
                marker=dict(size=8, symbol="circle", line=dict(color="white", width=1.5)),  
                text=df_trend["pct_score"].round(0).astype(int).astype(str) + "%",
                textposition="top center",  
                textfont=dict(weight="bold", color="#b45309", size=11)
            ),
            row=1, col=1
        )

        # ชั้นล่าง: กราฟแท่งคะแนนดิบรวมรายวัน
        max_y_value = df_trend["sum_score"].max() if not df_trend.empty else 100
        fig_split.add_trace(
            go.Bar(
                x=df_trend["วันที่_str"],
                y=df_trend["sum_score"],
                name="คะแนนรวม (Sum)",
                marker_color="#1a6582",  
                text=df_trend["sum_score"],
                textposition="outside",  
                textfont=dict(color="#334155", weight="bold")
            ),
            row=2, col=1
        )

        fig_split.update_yaxes(title_text="% คะแนน", ticksuffix="%", range=[0, 115], row=1, col=1)
        fig_split.update_xaxes(title_text="วันที่ประเมิน", type="category", showticklabels=True, row=1, col=1)
        
        fig_split.update_yaxes(title_text="Sum of คะแนน", range=[0, max_y_value * 1.25], row=2, col=1)
        fig_split.update_xaxes(title_text="วันที่ประเมิน", type="category", showticklabels=True, row=2, col=1)

        fig_split.update_layout(
            hovermode="x unified",
            showlegend=False,
            height=650, 
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_split, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================================
# 5. โซนกราฟแถวล่างสุด: วิเคราะห์ความเสถียร (แก้ไขระบบ Error Bar และล็อกสีรายบุคคล)
# =========================================================================
st.markdown("### 🔍 เจาะลึกความเสถียรของคุณภาพบริการ")

x_col_box = "Shift" if "Shift" in df_filtered.columns else "ชื่อ"

# คำนวณค่าทางสถิติ Max, Median, Min ของรายบุคคล
df_box_stat = df_filtered.groupby(x_col_box)["Table5.คะแนน"].agg(
    Max="max",
    Median="median",
    Min="min"
).reset_index()

# คำนวณระยะกางของหนวดแกน Y (Error Bars) บนและล่าง
df_box_stat["error_plus"] = df_box_stat["Max"] - df_box_stat["Median"]
df_box_stat["error_minus"] = df_box_stat["Median"] - df_box_stat["Min"]

# กำหนดสีที่ถูกต้องตามเกณฑ์ประเมินของค่า Median จริงรายบุคคล
df_box_stat["color_group"] = df_box_stat["Median"].apply(get_color_by_score)

# สร้างกราฟความเสถียรด้วย go.Figure
fig_custom_box = go.Figure()

fig_custom_box.add_trace(go.Bar(
    x=df_box_stat[x_col_box],
    y=df_box_stat["Median"],
    error_y=dict(
        type='data', 
        symmetric=False,                                # กำหนดให้หนวดบน-ล่าง ยาวไม่เท่ากันได้
        array=df_box_stat["error_plus"].tolist(),       # ระยะหนวดด้านบน
        arrayminus=df_box_stat["error_minus"].tolist(), # ระยะหนวดด้านล่าง
        visible=True, 
        thickness=1.5, 
        color="#475569"
    ),
    marker_color=df_box_stat["color_group"].tolist(), # พ่นสีตรงตัว ไม่สับสน
    customdata=df_box_stat[["Max", "Min"]].values,
    hovertemplate="<b>%{x}</b><br>" +
                  "คะแนนสูงสุด (Max): %{customdata[0]:.2f} คะแนน<br>" +
                  "คะแนนตรงกลาง (Median): %{y:.2f} คะแนน<br>" +
                  "คะแนนต่ำสุด (Min): %{customdata[1]:.2f} คะแนน<extra></extra>"
))

fig_custom_box.update_layout(
    title="วิเคราะห์ความเสถียรของคุณภาพบริการรายบุคคล (สีตามเกณฑ์ประเมินจริง | เส้นหนวดยิ่งแคบ = คุณภาพบริการยิ่งคงเส้นคงวา)",
    hovermode="closest",
    xaxis_title=x_col_box,
    yaxis_title="คะแนนเสถียรภาพ (Median)",
    height=480,
    xaxis=dict(type='category')
)
st.plotly_chart(fig_custom_box, use_container_width=True)

# =========================================================================
# 6. ส่วนตารางสรุปข้อมูลประเมินผลไขว้รายวัน (PIVOT TABLE)
# =========================================================================
st.markdown("---")
st.markdown("### 🗂️ ตารางสรุปข้อมูลประเมินผลไขว้รายวัน")

if "วันที่ประเมิน" in df_filtered.columns and not df_filtered.empty:
    df_pivot_prep = df_filtered.copy()
    
    idx_col = "Shift" if "Shift" in df_pivot_prep.columns else "ชื่อ"
    work_days_per_agent = df_pivot_prep.groupby(idx_col)["壓ันที่ประเมิน"].nunique() if "壓ันที่ประเมิน" in df_pivot_prep.columns else df_pivot_prep.groupby(idx_col)["วันที่ประเมิน"].nunique()
    
    agent_grade_map = df_pivot_prep.groupby(idx_col)["Performance by personal"].last().to_dict()
    df_pivot_prep["วันที่_str"] = df_pivot_prep["壓ันที่ประเมิน"].dt.strftime('%d/%m/%Y') if "壓ันที่ประเมิน" in df_pivot_prep.columns else df_pivot_prep["วันที่ประเมิน"].dt.strftime('%d/%m/%Y')
    
    pivot_table = df_pivot_prep.pivot_table(
        index=idx_col, columns="วันที่_str", values="Table5.คะแนน", aggfunc="sum", fill_value=0
    )
    
    date_columns = list(pivot_table.columns)
    pivot_table["Grand Total"] = pivot_table[date_columns].sum(axis=1)
    
    percentage_list = []
    for agent_name in pivot_table.index:
        actual_total = pivot_table.loc[agent_name, "Grand Total"]
        days = work_days_per_agent.get(agent_name, 1)
        possible_full_score = days * FULL_SCORE
        pct = (actual_total / possible_full_score) * 100
        percentage_list.append(f"{pct:.1f}%")
        
    pivot_table["% Achievement (เทียบเต็ม)"] = percentage_list
    pivot_table["กลุ่มผลงานปัจจุบัน"] = [agent_grade_map.get(agent_name, "-") for agent_name in pivot_table.index]
    
    total_score_sum = pivot_table["Grand Total"].sum()
    total_possible_all = len(df_filtered) * FULL_SCORE
    total_pct_all = (total_score_sum / total_possible_all) * 100
    
    st.success(f"📊 **ภาพรวมข้อมูลที่ถูกเลือก:** คะแนนสะสมรวมกันทำได้จริง **{int(total_score_sum):,} / {int(total_possible_all):,} คะแนน** (คิดเป็นเฉลี่ยรวม **{total_pct_all:.1f}%** จากคะแนนเต็มทั้งหมด)")
    st.dataframe(pivot_table, use_container_width=True)
else:
    st.info("💡 ไม่มีข้อมูลแสดงผลในตารางเนื่องจากตัวกรอง")
