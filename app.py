# ... existing code ...
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. ตั้งค่าหน้าแดชบอร์ด
st.set_page_config(page_title="1577 CX Performance Control", layout="wide", initial_sidebar_state="expanded")
# ... existing code ...
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
        # จัดกลุ่มข้อมูลรายวันเพื่อหาผลรวมคะแนนจริง และจำนวนเคสที่ประเมินในวันนั้นๆ
        df_trend = df_filtered.groupby("วันที่ประเมิน").agg(
            Sum_Score=("Table5.คะแนน", "sum"),
            Count_Cases=("Table5.คะแนน", "count")
        ).reset_index()
        
        # คำนวณคะแนนเต็มที่เป็นไปได้ทั้งหมดในวันนั้น (จำนวนเคส x คะแนนเต็ม 25) และหาเปอร์เซ็นต์
        df_trend["Max_Possible"] = df_trend["Count_Cases"] * FULL_SCORE
        df_trend["Pct_Score"] = (df_trend["Sum_Score"] / df_trend["Max_Possible"]) * 100
        df_trend["Pct_Text"] = df_trend["Pct_Score"].apply(lambda x: f"{round(x)}%")
        
        # แปลงรูปแบบวันที่สำหรับการแสดงผลบนแกน X ให้สวยงาม
        df_trend["วันที่_แสดงผล"] = df_trend["วันที่ประเมิน"].dt.strftime('%d/%m/%Y')
        
        # สร้าง subplot ที่มี 2 แกนวาย (Dual-Axis)
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        
        # 1. เพิ่มแผนภูมิแท่ง (Bar Chart) แสดงคะแนนรวมสะสม (Qty) ที่แกนหลักฝั่งซ้าย
        fig_trend.add_trace(
            go.Bar(
                x=df_trend["วันที่_แสดงผล"],
                y=df_trend["Sum_Score"],
                name="คะแนนดิบสะสมรวม (Qty)",
                marker=dict(color="#1a5f7a"),
                text=df_trend["Sum_Score"],
                textposition="inside",  # แสดงป้ายตัวเลขคะแนนรวมสะสมไว้ด้านในแท่ง
                insidetextanchor="bottom",  # ล็อกตำแหน่งตัวเลขให้อยู่ด้านล่างภายในแท่งเหมือนในรูป
                textfont=dict(color="white", size=14, family="sans-serif", weight="bold"),
                hovertemplate="วันที่: %{x}<br>คะแนนรวม: %{y} คะแนน<extra></extra>"
            ),
            secondary_y=False
        )
        
        # 2. เพิ่มแผนภูมิเส้น (Line Chart) แสดงเปอร์เซ็นต์ผลสัมฤทธิ์ (%) ที่แกนรองฝั่งขวา
        fig_trend.add_trace(
            go.Scatter(
                x=df_trend["วันที่_แสดงผล"],
                y=df_trend["Pct_Score"],
                name="เปอร์เซ็นต์อัตราความสำเร็จ (%)",
                mode="lines+markers+text",
                line=dict(color="#ea580c", width=4),
                marker=dict(size=12, symbol="circle", color="#ea580c"),
                text=df_trend["Pct_Text"],
                textposition="top center",  # แสดงตัวเลข % ลอยเด่นอยู่เหนือจุดบนเส้นกราฟ
                textfont=dict(color="#1e293b", size=13, family="sans-serif", weight="bold"),
                hovertemplate="วันที่: %{x}<br>เปอร์เซ็นต์: %{text}<extra></extra>"
            ),
            secondary_y=True
        )
        
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
                range=[0, 110],  # กำหนดระยะเผื่อเหนือ 100% เล็กน้อยเพื่อให้ป้ายตัวเลขไม่หลุดขอบบน
                showgrid=False,
                ticksuffix="%"
            )
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
# ... existing code ...
