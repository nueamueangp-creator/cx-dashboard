import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าแดชบอร์ด
st.set_page_config(page_title="1577 CX Department Dashboard", layout="wide", initial_sidebar_state="collapsed")

# 🔗 ⚠️ สำคัญมาก: ก๊อปปี้ลิงก์ .csv ที่ได้จากข้อ 3 ในส่วนแรกมาวางแทนที่เครื่องหมายคำพูดด้านล่างนี้เลยครับ
sheet_csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRSLXaX4OFmcO8xhcoKllNThw3tFBbVCRETb5X9n6Q4gTc4Rudd9d5_wS7UZXKHm8BVVtzzq1sWgxAN/pub?output=csv"

try:
    # 2. ดึงข้อมูลสดจาก Google Sheets
    df = pd.read_csv(sheet_csv_url)
    
    # คำนวณค่าสถิติจริง
    total_records = len(df)
    total_staff = df["ชื่อ"].nunique()
    avg_score = df["Table5.คะแนน"].mean()
    avg_percentage = (avg_score / 25) * 100
    need_improve_count = len(df[df["Performance by personal"] == "Need Improve"])

except Exception as e:
    st.error("❌ ไม่สามารถดึงข้อมูลจาก Google Sheets ได้ กรุณาตรวจสอบลิงก์ CSV หรืออินเทอร์เน็ต")
    st.stop()

# 3. ตกแต่งหน้าตาเว็บด้วย HTML + Tailwind CSS สไตล์ที่คุณชอบ
st.markdown(
    f"""
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@450;600;700&family=Sarabun:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    
    <style>
        * {{ font-family: 'Sarabun', sans-serif; }}
        h1, h2, h3, h4, .font-prompt {{ font-family: 'Prompt', sans-serif; }}
    </style>

    <div class="text-slate-800">
        <header class="bg-slate-900 text-white shadow-md rounded-2xl p-5 mb-6 flex flex-col md:flex-row items-center justify-between gap-4">
            <div class="flex items-center space-x-3">
                <div class="bg-indigo-600 p-3 rounded-xl text-white shadow-lg">
                    <i class="fa-solid fa-users-gear text-xl"></i>
                </div>
                <div>
                    <h1 class="text-xl font-bold tracking-tight text-white">1577 CX Department Dashboard</h1>
                    <p class="text-xs text-slate-400 mt-0.5">ระบบสรุปผลการประเมินพนักงาน (Real-time Google Sheets Sync)</p>
                </div>
            </div>
            <div class="text-xs bg-slate-800 px-4 py-2 rounded-xl border border-slate-700 flex items-center gap-2">
                <span class="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span class="text-slate-300">ซิงค์กับ Google Sheets สำเร็จ</span>
            </div>
        </header>

        <!-- KPI Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 flex items-center space-x-4">
                <div class="p-3 rounded-xl bg-indigo-50 text-indigo-600"><i class="fa-solid fa-user-tie text-lg"></i></div>
                <div>
                    <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">พนักงานในระบบ</p>
                    <p class="text-lg font-bold text-slate-800">{total_staff} คน</p>
                </div>
            </div>
            <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 flex items-center space-x-4">
                <div class="p-3 rounded-xl bg-emerald-50 text-emerald-600"><i class="fa-solid fa-star text-lg"></i></div>
                <div>
                    <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">คะแนนเฉลี่ย</p>
                    <p class="text-lg font-bold text-slate-800">{avg_score:.2f} / 25</p>
                </div>
            </div>
            <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 flex items-center space-x-4">
                <div class="p-3 rounded-xl bg-sky-50 text-sky-600"><i class="fa-solid fa-chart-simple text-lg"></i></div>
                <div>
                    <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">ประสิทธิภาพรวม</p>
                    <p class="text-lg font-bold text-slate-800">{avg_percentage:.1f}%</p>
                </div>
            </div>
            <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 flex items-center space-x-4">
                <div class="p-3 rounded-xl bg-rose-50 text-rose-600"><i class="fa-solid fa-triangle-exclamation text-lg"></i></div>
                <div>
                    <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">ต้องปรับปรุงด่วน</p>
                    <p class="text-lg font-bold text-rose-600">{need_improve_count} รายการ</p>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 4. แสดงผลกราฟ
st.markdown("### 📈 บทวิเคราะห์ข้อมูลพนักงาน")
col1, col2 = st.columns(2)

with col1:
    df_grouped = df.groupby("ชื่อ")["Table5.คะแนน"].mean().reset_index().sort_values(by="Table5.คะแนน", ascending=False)
    fig_bar = px.bar(df_grouped, x="ชื่อ", y="Table5.คะแนน", title="อันดับคะแนนเฉลี่ยรายบุคคล",
                     labels={"Table5.คะแนน": "คะแนนเฉลี่ย", "ชื่อ": "พนักงาน"}, color="Table5.คะแนน")
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    fig_pie = px.pie(df, names="Performance by personal", title="สัดส่วนเกรดประเมินผลพนักงาน")
    st.plotly_chart(fig_pie, use_container_width=True)

# 5. แสดงผลตารางด้านล่าง
st.markdown("---")
st.markdown("### 📊 ข้อมูลตารางการประเมินจริง")
search_query = st.text_input("🔍 ค้นหาชื่อพนักงาน:", "")
if search_query:
    filtered_df = df[df["ชื่อ"].str.contains(search_query, na=False)]
else:
    filtered_df = df
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
