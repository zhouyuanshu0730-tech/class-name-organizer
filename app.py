
import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl.styles import Font, PatternFill, Alignment

from parser import parse_text


st.set_page_config(
    page_title="班级姓名智能整理系统",
    page_icon="📋",
    layout="wide"
)

st.title("📋 智能名单整理系统")
st.caption("支持多种名单格式，自动识别字段，动态生成 Excel 列")

st.info(
    "支持班级、姓名、性别、手机号、出生日期、"
    "政治面貌、职务、年龄及其他信息识别。"
)

raw_text = st.text_area(
    "第一步：粘贴原始名单",
    height=300,
    placeholder="""例如：
马文雪 女 26会计1班
26关务一班 王春喻 女
董晗晰 女 26旅游1班 2005年5月10日
陈政霖 男 26会计2班 团支书
王小明 男 13800000000"""
)

if st.button("开始智能整理", type="primary", use_container_width=True):

    if not raw_text.strip():
        st.warning("请先粘贴名单！")
    else:
        data = parse_text(raw_text)

        if not data:
            st.warning("没有识别到有效名单，请检查输入内容。")
        else:
            df = pd.DataFrame(data).fillna("")
            st.session_state["result"] = df
            st.success(f"整理完成！共识别 {len(df)} 条名单。")


if "result" in st.session_state:

    st.subheader("第二步：检查和编辑识别结果")

    edited_df = st.data_editor(
        st.session_state["result"],
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key="dynamic_result_editor"
    )

    st.write(f"名单总数：{len(edited_df)}")
    st.write(f"自动识别字段：{len(edited_df.columns)} 列")

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        edited_df.to_excel(
            writer,
            index=False,
            sheet_name="名单"
        )

        worksheet = writer.sheets["名单"]

        for column_cells in worksheet.columns:
            column_letter = column_cells[0].column_letter
            max_length = max(
                len(str(cell.value or ""))
                for cell in column_cells
            )
            worksheet.column_dimensions[column_letter].width = min(
                max(max_length + 4, 12), 30
            )

        for cell in worksheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(
                fill_type="solid",
                fgColor="217346"
            )
            cell.alignment = Alignment(horizontal="center")

        for row in worksheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(horizontal="center")

        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions

    st.download_button(
        label="📥 下载智能整理 Excel",
        data=output.getvalue(),
        file_name="智能整理名单.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    if st.button("清空结果", use_container_width=True):
        del st.session_state["result"]
        st.rerun()
