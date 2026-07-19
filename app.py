# =========================================================================
# 5. โซนกราฟแถวล่างสุด: วิเคราะห์ความเสถียร (ล็อกสีตามกลุ่มผลงานปัจจุบันให้ตรงกับกราฟบน)
# =========================================================================
st.markdown("### 🔍 เจาะลึกความเสถียรของคุณภาพบริการ")

x_col_box = "Shift" if "Shift" in df_filtered.columns else "ชื่อ"

# คำนวณค่าทางสถิติ Max, Mean, Min ของรายบุคคล
df_box_stat = df_filtered.groupby(x_col_box)["Table5.คะแนน"].agg(
    Mean="mean",
    Max="max",
    Min="min"
).reset_index()

# คำนวณระยะกางของหนวดแกน Y (Error Bars) บนและล่าง
df_box_stat["error_plus"] = df_box_stat["Max"] - df_box_stat["Mean"]
df_box_stat["error_minus"] = df_box_stat["Mean"] - df_box_stat["Min"]

# แมปสีจากกลุ่มผลงานปัจจุบัน (Performance Grade) เพื่อให้ตรงกับกราฟบน 100%
df_box_stat["current_grade"] = df_box_stat[x_col_box].map(agent_grade_map)
df_box_stat["color_group"] = df_box_stat["current_grade"].apply(get_color_by_grade)

# จัดเรียงลำดับตามคะแนนเฉลี่ยจากน้อยไปมาก เพื่อล้อไปกับลำดับของกราฟบน
df_box_stat = df_box_stat.sort_values(by="Mean")

fig_custom_box = go.Figure()

fig_custom_box.add_trace(go.Bar(
    x=df_box_stat[x_col_box],
    y=df_box_stat["Mean"],
    error_y=dict(
        type='data', 
        symmetric=False,
        array=df_box_stat["error_plus"].tolist(),       
        arrayminus=df_box_stat["error_minus"].tolist(), 
        visible=True, 
        thickness=1.5, 
        color="#475569"
    ),
    marker_color=df_box_stat["color_group"].tolist(), # 🎨 พ่นสีตามกลุ่มผลงานปัจจุบัน
    text=df_box_stat["Mean"].round(2),                # 🎯 แสดงตัวเลขคะแนนเฉลี่ยบนแท่งกราฟ
    textposition="inside",                             # 📍 จัดให้อยู่ด้านในปลายแท่งเพื่อหลบเส้นหนวด
    textfont=dict(color="white", weight="bold"),       # 🎨 ปรับฟอนต์สีขาวตัวหนาให้อ่านง่าย
    customdata=df_box_stat[["Max", "Min", "current_grade"]].values,
    hovertemplate="<b>%{x}</b><br>" +
                  "กลุ่มผลงานปัจจุบัน: %{customdata[2]}<br>" +
                  "คะแนนสูงสุดที่เคยทำได้ (Max): %{customdata[0]:.2f} คะแนน<br>" +
                  "คะแนนเฉลี่ยสุทธิ (Mean): %{y:.2f} คะแนน<br>" +
                  "คะแนนต่ำสุดที่เคยทำได้ (Min): %{customdata[1]:.2f} คะแนน<extra></extra>"
))

fig_custom_box.update_layout(
    title="วิเคราะห์ความเสถียรของคุณภาพบริการรายบุคคล (สีแยกตามกลุ่มผลงานปัจจุบัน | เส้นหนวดยิ่งแคบ = คุณภาพบริการยิ่งคงเส้นคงวา)",
    hovermode="closest",
    xaxis_title=x_col_box,
    yaxis_title="คะแนนเฉลี่ยสะสม (Mean)",
    height=480,
    xaxis=dict(type='category')
)
st.plotly_chart(fig_custom_box, use_container_width=True)
