import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="1577 CX Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS injection for executive view and mobile optimization
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700&family=Prompt:wght@500;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'Prompt', sans-serif;
        color: #0f172a;
    }
    .metric-container {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #0d9488;
    }
    .metric-label {
        font-size: 14px;
        color: #64748b;
        font-weight: 600;
    }
</style>
""", unsafe_allowed_html=True)

# Daily Score Data (Sum of Scores and Max Potential Score calculation)
# Total employees evaluated = 26. Max potential score per employee per day = 25.
# Total Max Potential score per day = 26 * 25 = 650.
daily_data = {
    'วันที่ประเมิน': ['01/12/2024', '02/12/2024', '03/12/2024', '04/12/2024'],
    'Sum_Score': [595, 475, 305, 575],
    'Max_Possible': [650, 650, 650, 650]
}
df_daily = pd.DataFrame(daily_data)
df_daily['Pct_Score'] = (df_daily['Sum_Score'] / df_daily['Max_Possible']) * 100
df_daily['Pct_Text'] = df_daily['Pct_Score'].apply(lambda x: f"{round(x)}%")

st.title("🚀 ระบบวิเคราะห์ประสิทธิภาพบริการทีม CX")
st.subheader("รายงานสรุปผลสัมฤทธิ์รายบุคคลและทิศทางคุณภาพรายวัน (PC & Mobile Support)")

# Sidebar filters for interactivity (Executive Slicer simulator)
st.sidebar.header("🎛️ ตัวแบ่งส่วนข้อมูล (Slicers)")
selected_dates = st.sidebar.multiselect(
    "เลือกวันที่ต้องการประเมิน",
    options=df_daily['วันที่ประเมิน'].tolist(),
    default=df_daily['วันที่ประเมิน'].tolist()
)

# Filter the daily dataset based on selection
df_filtered = df_daily[df_daily['วันที่ประเมิน'].isin(selected_dates)]

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="metric-container"><div class="metric-label">คะแนนรวมสะสมจริง (Qty)</div><div class="metric-value">1,950</div></div>', unsafe_allowed_html=True)
with col2:
    st.markdown('<div class="metric-container"><div class="metric-label">คะแนนเต็มศักยภาพสูงสุด (Max)</div><div class="metric-value" style="color:#0f172a;">2,600</div></div>', unsafe_allowed_html=True)
with col3:
    st.markdown('<div class="metric-container"><div class="metric-label">อัตราผลสัมฤทธิ์ภาพรวม (% Overall)</div><div class="metric-value" style="color:#ea580c;">75.0%</div></div>', unsafe_allowed_html=True)

st.write("")

# This chart displays Bar Chart (Qty score) on Primary Axis and Line Chart (%) on Secondary Axis
st.write("### 📈 ทิศทางคะแนนสะสมและเปอร์เซ็นต์ผลงานทีมรายวัน")

# Create subplot figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# 1. Add Bar Chart (Sum of Scores - Qty)
fig.add_trace(
    go.Bar(
        x=df_filtered['วันที่ประเมิน'],
        y=df_filtered['Sum_Score'],
        name="คะแนนสะสมรวม (Qty)",
        marker=dict(color="#1a5f7a", cornerradius=5),
        text=df_filtered['Sum_Score'],
        textposition="inside", # Places score quantity inside the columns (just like image_b25881.png)
        textfont=dict(color="white", size=14, family="Sarabun"),
        hovertemplate="วันที่: %{x}<br>คะแนนรวม: %{y} คะแนน<extra></extra>"
    ),
    secondary_y=False
)

# 2. Add Line Chart (Percentage Score - %)
fig.add_trace(
    go.Scatter(
        x=df_filtered['วันที่ประเมิน'],
        y=df_filtered['Pct_Score'],
        name="เปอร์เซ็นต์ความพึงพอใจ (%)",
        mode="lines+markers+text",
        line=dict(color="#ea580c", width=4),
        marker=dict(size=12, symbol="circle", color="#ea580c"),
        text=df_filtered['Pct_Text'],
        textposition="top center", # Displays % label hovering above the line points
        textfont=dict(color="#1e293b", size=13, family="Sarabun", weight="bold"),
        hovertemplate="วันที่: %{x}<br>สัดส่วนความสำเร็จ: %{text}<extra></extra>"
    ),
    secondary_y=True
)

fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=40, r=40, t=20, b=40),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.05,
        xanchor="right",
        x=1
    ),
    xaxis=dict(
        showgrid=False,
        tickfont=dict(size=12, color="#64748b", family="Sarabun")
    ),
    yaxis=dict(
        title="คะแนนดิบสะสมรวม (Qty)",
        titlefont=dict(color="#1a5f7a", size=12, family="Sarabun"),
        tickfont=dict(color="#1a5f7a", family="Sarabun"),
        range=[0, 700], # Sets primary axis limits to give padding for visuals
        showgrid=True,
        gridcolor="#f1f5f9"
    ),
    yaxis2=dict(
        title="เปอร์เซ็นต์อัตราความสำเร็จ (%)",
        titlefont=dict(color="#ea580c", size=12, family="Sarabun"),
        tickfont=dict(color="#ea580c", family="Sarabun"),
        range=[0, 100], # Sets secondary axis range perfectly to 100%
        showgrid=False,
        ticksuffix="%"
    )
)

# Draw the chart to Streamlit with responsive column configuration enabled
st.plotly_chart(fig, use_container_width=True)

st.info("""
💡 **บทวิเคราะห์เพื่อผู้บริหาร:** แผนภูมิแสดงให้เห็นว่าในวันที่ **03/12/2024** มีสัดส่วนคะแนนตกลงต่ำสุดอย่างรุนแรงเหลือเพียง **305 คะแนน (คิดเป็น 47%)** 
ในขณะที่วันอื่นมีค่าเฉลี่ยสัดส่วนสูงกว่า 73% ขึ้นไป ชี้ให้เห็นว่า วันดังกล่าวเป็นวิกฤตความพึงพอใจในระดับเชิงโครงสร้างระบบ (Systemic Issue) 
ไม่ใช่ประสิทธิภาพการบริการส่วนพนักงานรายคน
""")
