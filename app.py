import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. ตั้งค่าหน้าแดชบอร์ด
st.set_page_config(page_title="1577 CX Quality Radar", layout="wide", initial_sidebar_state="collapsed")

# 🔗 ลิงก์ CSV ของคุณที่ซิงค์สำเร็จแล้ว
sheet_csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRSLXaX4OFmcO8xhcoKllNThw3tFBbVCRETb5X9n6Q4gTc4Rudd9d5_wS7UZXKHm8BVVtzzq1sWgxAN/pub?output=csv"

try:
    # 2. ดึงข้อมูลและจัดการวันที่
    df = pd.read_csv(sheet_csv_url)
    if "วันที่ประเมิน" in df.columns:
        df["วันที่ประเมิน"] = pd.to_datetime(df["วันที่ประเมิน"])
        df = df.sort_values(by="วันที่ประเมิน")
    
    # คำนวณค่าสถิติหลัก
    total_records = len(df)
    total_staff = df["ชื่อ"].nunique()
    avg_score = df["Table5.คะแนน"].mean()
    avg_percentage = (avg_score / 25) * 100
    
    # ตั้งเกณฑ์มาตรฐานสากล (ผ่านเกณฑ์ที่ 20 คะแนน หรือ 80%)
    TARGET_SCORE = 20
    failed_cases_df = df[df["Table5.คะแนน"] < TARGET_SCORE]
    failed_percentage = (len(failed_cases_df) / total_records) * 100
    need_improve_df = df[df["Performance by personal"] == "Need Improve"]

    # 🚨 AI ตรวจสอบหาจุดบกพร่องรายบุคคลและรายวันอัตโนมัติ
    agent_means = df.groupby("ชื่อ")["Table5.คะแนน"].mean()
    lowest_agent = agent_means.idxmin()
    lowest_score = agent_means.min()
    highest_agent = agent_means.idxmax()
    highest_score = agent_means.max()
    
    worst_date_str = "ไม่มีข้อมูล"
    worst_date_score = 0
    if "วันที่ประเมิน" in df.columns:
        date_means = df.groupby("วันที่ประเมิน")["Table5.คะแนน"].mean()
        worst_date = date_means.idxmin()
        worst_date_score = date_means.min()
        worst_date_str = worst_date.strftime('%Y-%m-%d')

except Exception as e:
    st.error("❌ ไม่สามารถดึงข้อมูลได้ กรุณาตรวจสอบว่า Google Sheets มีการเปลี่ยนแปลงโครงสร้างคอลัมน์หรือไม่")
    st.stop()

# 3. ส่วนหัวแดชบอร์ด
st.markdown(
    f"""
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@455;600;700&family=Sarabun:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    
    <div class="text-slate-800">
        <header class="bg-slate-950 text-white shadow-xl rounded-2xl p-5 mb-6 flex flex-col md:flex-row items-center justify-between gap-4">
            <div class="flex items-center space-x-3">
                <div class="bg-gradient-to-tr from-rose-600 to-amber-500 p-3 rounded-xl text-white shadow-lg">
                    <i class="fa-solid fa-triangle-exclamation text-xl"></i>
                </div>
                <div>
                    <h1 class="text-xl font-bold tracking-tight text-white">1577 CX Quality Radar & Deep Insights</h1>
                    <p class="text-xs text-slate-400 mt-0.5">ระบบตรวจจับจุดบกพร่องและวิเคราะห์ประสิทธิภาพทีม CX รายบุคคลอัตโนมัติ</p>
                </div>
            </div>
            <div class="text-xs bg-slate-950 px-4 py-2 rounded-xl border border-slate-800 flex items-center gap-2">
                <span class="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span class="text-slate-300">ฐานข้อมูลสด: ซิงค์ Real-time กับ Google Sheets สำเร็จ</span>
            </div>
        </header>
    </div>
    """,
    unsafe_allow_html=True
)

# 4. 💡 โซนบทวิเคราะห์และข้อแนะนำอัตโนมัติ (AI Automated Insights Box)
st.markdown("### 💡 บทวิเคราะห์ปัญหาและข้อแนะนำเชิงกลยุทธ์ (Automated Insights)")
st.markdown(
    f"""
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-white mb-6 shadow-md">
        <div class="flex items-center space-x-2 text-amber-400 mb-3 font-semibold text-sm">
            <i class="fa-solid fa-lightbulb"></i>
            <span>บทสรุปผู้บริหาร (Executive Summary Report)</span>
        </div>
        <ul class="space-y-3 text-xs text-slate-300 list-disc pl-4">
            <li><b>พนักงานที่ต้องได้รับการสนับสนุนด่วน:</b> คุณ <span class="text-rose-400 font-bold">{lowest_agent}</span> มีคะแนนประเมินเฉลี่ยต่ำที่สุดในแผนก อยู่ที่ <span class="text-rose-400 font-bold">{lowest_score:.2f} / 25</span> คะแนน ควรจัดกลุ่มทำ Coaching รายบุคคล</li>
            <li><b>พนักงานผลงานดีเด่น (Top Performer):</b> คุณ <span class="text-emerald-400 font-bold">{highest_agent}</span> ทำคะแนนเฉลี่ยสูงสุดในแผนก อยู่ที่ <span class="text-emerald-400 font-bold">{highest_score:.2f} / 25</span> คะแนน สามารถดึงมาเป็น Buddy ถ่ายทอดเทคนิคให้เพื่อนได้</li>
            <li><b>วันที่ประสิทธิภาพการบริการวิกฤตที่สุด:</b> วันที่ <span class="text-amber-400 font-bold">{worst_date_str}</span> ทีมมีคะแนนเฉลี่ยดิ่งลงต่ำที่สุดเหลือเพียง <span class="text-amber-400 font-bold">{worst_date_score:.2f} / 25</span> คะแนน <i>(แนะนำให้ตรวจสอบว่าวันดังกล่าวมีปัญหาระบบล่ม ปริมาณสายล้น หรือปัจจัยภายนอกหรือไม่)</i></li>
            <li><b>อัตราความเสี่ยงภาพรวม:</b> มีเคสที่ตกเกณฑ์มาตรฐาน (ต่ำกว่า {TARGET_SCORE} คะแนน) อยู่สูงถึง <span class="text-rose-400 font-bold">{failed_percentage:.1f}%</span> ของเคสทั้งหมดในระบบ</li>
        </ul>
        <div class="mt-4 pt-4 border-t border-slate-800 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div class="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
                <span class="text-emerald-400 font-bold block mb-1">🚀 ข้อเสนอแนะที่ 1: ระบบคู่หู (Buddy System)</span>
                ให้นำแนวทางการตอบลูกค้าและเทคนิคของคุณ {highest_agent} มาจัดทำเป็น Best Practice และประกบคู่ช่วยแนะแนวคุณ {lowest_agent} ในการทำงานจริง
            </div>
            <div class="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
                <span class="text-rose-400 font-bold block mb-1">🎯 ข้อเสนอแนะที่ 2: เจาะลึกเคสวิกฤต</span>
                ดึงประวัติการคุยหรือไฟล์เสียงของกลุ่มประเมิน <span class="text-rose-400">Need Improve</span> ที่แสดงผลในตารางด้านล่างจำนวน {len(need_improve_df)} เคส มาทบทวนเพื่อหาจุดผิดพลาดร่วมกัน
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 5. การ์ดสรุปตัวเลข KPIs
st.markdown("### 📊 ตัวชี้วัดหลักประสิทธิภาพทีม (Main KPIs)")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("จำนวนพนักงานประเมิน", f"{total_staff} คน")
with kpi2:
    st.metric("คะแนนเฉลี่ยรวมทั้งทีม", f"{avg_score:.2f} / 25")
with kpi3:
    st.metric("เปอร์เซ็นต์ประสิทธิภาพเฉลี่ย", f"{avg_percentage:.1f}%")
with kpi4:
    st.metric("จำนวนเคสตกเกณฑ์ (<20 คะแนน)", f"{len(failed_cases_df)} เคส", delta=f"{failed_percentage:.1f}% ของทั้งหมด", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

# 6. โซนกราฟวิเคราะห์
st.markdown("### 📈 เจาะลึกข้อมูลรายบุคคลและแนวโน้มช่วงเวลา")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    df_agent = df.groupby("ชื่อ")["Table5.คะแนน"].mean().reset_index().sort_values(by="Table5.คะแนน")
    fig_bar = px.bar(
        df_agent, x="Table5.คะแนน", y="ชื่อ", orientation='h',
        title="อันดับคะแนนเฉลี่ยสะสมรายบุคคล (เรียงจากน้อยไปมาก)",
        labels={"Table5.คะแนน": "คะแนนเฉลี่ย", "ชื่อ": "ชื่อพนักงาน"},
        color="Table5.คะแนน", color_continuous_scale="RdYlGn"
    )
    fig_bar.add_vline(x=TARGET_SCORE, line_dash="dash", line_color="red", 
                      annotation_text=f"เกณฑ์ผ่านขั้นต่ำ ({TARGET_SCORE} คะแนน)", annotation_position="top right")
    st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    if "วันที่ประเมิน" in df.columns:
        df_trend = df.groupby("วันที่ประเมิน")["Table5.คะแนน"].mean().reset_index()
        fig_line = px.line(
            df_trend, x="วันที่ประเมิน", y="Table5.คะแนน",
            title="แนวโน้มคุณภาพการบริการรายวัน (Timeline Trend)",
            labels={"Table5.คะแนน": "คะแนนเฉลี่ยทีม", "วันที่ประเมิน": "วันที่ประเมิน"},
            markers=True
        )
        fig_line.add_hline(y=TARGET_SCORE, line_dash="dash", line_color="red")
        st.plotly_chart(fig_line, use_container_width=True)

# 7. ตารางข้อมูลดิบและการค้นหา
st.markdown("---")
st.markdown("### 📋 ตารางประวัติและระบบค้นหาเคสประเมิน")
search_query = st.text_input("🔍 ค้นหาประวัติการประเมินอย่างรวดเร็ว (พิมพ์ชื่อพนักงาน):", "")

if search_query:
    filtered_df = df[df["ชื่อ"].str.contains(search_query, na=False)]
else:
    filtered_df = df

st.dataframe(filtered_df, use_container_width=True, hide_index=True)
