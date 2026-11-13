
import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl.styles import Font, PatternFill, Alignment

from parser import parse_text
from class_config import EXCEL_COLUMNS


# 网页设置
st.set_page_config(
    page_title="班级姓名智能整理系统",
    page_icon="📋",
    layout="centered"
)

st.title("📋 班级姓名智能整理系统")
st.caption("粘贴原始名单，自动识别班级和姓名，一键生成 Excel")

st.info(
    "整理规则：支持所有年级；没有填写班级编号时默认1班；"
    "没有识别到班级时，班级列留空。"
)

# 输入名单
raw_text = st.text_area(
    "第一步：请粘贴原始名单",
    height=280,
    placeholder="""例如：
1. 26高铁2班李俊楦
2. 26关务何梓萌
3. 26会计2班陈政霖
4. 王小明"""
)

# 自动整理
if st.button("开始自动整理", type="primary", use_container_width=True):

    if not raw_text.strip():
        st.warning("请先粘贴名单内容！")
    else:
        data = parse_text(raw_text)

        df = pd.DataFrame(data, columns=EXCEL_COLUMNS)

        st.session_state["result"] = df

        st.success(f"整理完成！共整理 {len(df)} 条名单。")


# 显示和编辑结果
if "result" in st.session_state:

    st.subheader("第二步：检查并修改整理结果")

    edited_df = st.data_editor(
        st.session_state["result"],
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key="result_editor"
    )

    st.write(f"名单总数：{len(edited_df)}")

    # 生成Excel
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        edited_df.to_excel(
            writer,
            index=False,
            sheet_name="名单"
        )

        worksheet = writer.sheets["名单"]

        # 设置列宽
        worksheet.column_dimensions["A"].width = 22
        worksheet.column_dimensions["B"].width = 18

        # 设置表头样式
        for cell in worksheet[1]:
            cell.font = Font(
                bold=True,
                color="FFFFFF"
            )

            cell.fill = PatternFill(
                fill_type="solid",
                fgColor="217346"
            )

            cell.alignment = Alignment(
                horizontal="center"
            )

        # 内容居中
        for row in worksheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(
                    horizontal="center"
                )

        # 冻结表头和开启筛选
        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions

    # 下载按钮
    st.download_button(
        label="📥 下载 Excel 文件",
        data=output.getvalue(),
        file_name="班级姓名名单.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    # 清空按钮
    if st.button("清空结果", use_container_width=True):
        del st.session_state["result"]
        st.rerun()
