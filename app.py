import streamlit as st
import streamlit_mermaid as st_mermaid
from openai import OpenAI

# 页面配置：设置标题和手机端自适应布局
st.set_page_config(page_title="信号联锁实验室", layout="centered")

# --- 模拟数据初始化 ---
if 'log' not in st.session_state:
    st.session_state.update({
        "sw1": "定位", "sw3": "定位",
        "g1": "空闲", "g3": "空闲", "g5": "空闲",
        "sig": "关闭", "log": []
    })

# --- 模拟 AI 解释功能 (需在 Streamlit 后台配置 API Key) ---
def ask_ai_expert(reason):
    if "DEEPSEEK_API_KEY" not in st.secrets:
        return "（提示：未配置 AI 秘钥，请检查后台设置）"
    try:
        client = OpenAI(api_key=st.secrets["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": "你是铁路信号专家，请简短解释联锁失效的风险。"},
                      {"role": "user", "content": reason}]
        )
        return resp.choices[0].message.content
    except:
        return "AI 暂时掉线，请检查网络。"

# --- UI 界面 ---
st.title("🚉 铁路信号联锁教学平台")
st.info("手机端提示：点击下方开关模拟现场状态，再申请进路。")

# 1. 拓扑展示区 (置顶)
s1_color = "#00ff00" if st.session_state.sig == "开放" else "#ff0000"
sw_color = "#99ff99" if st.session_state.sw1 == "定位" else "#ff9999"
g_color = "#ffcccc" if any(st.session_state[g] == "占用" for g in ["g1","g3","g5"]) else "#e1f5fe"

mermaid_code = f"""
graph LR
    S1((S1信号)) --- G1[1G] --- SW1{{道岔}} --- G3[3G] --- G5[5G]
    style S1 fill:{s1_color}
    style SW1 fill:{sw_color}
    style G1 fill:{'#ffcccc' if st.session_state.g1=='占用' else '#e1f5fe'}
    style G3 fill:{'#ffcccc' if st.session_state.g3=='占用' else '#e1f5fe'}
    style G5 fill:{'#ffcccc' if st.session_state.g5=='占用' else '#e1f5fe'}
"""
st_mermaid.st_mermaid(mermaid_code, height=250)

# 2. 设备状态控制 (手机端使用多列)
st.subheader("🛠️ 现场模拟")
c1, c2 = st.columns(2)
with c1:
    st.session_state.sw1 = st.radio("1号道岔位置", ["定位", "反位"], horizontal=True)
with c2:
    st.write("区段状态")
    if st.checkbox("模拟 3G 占用"): st.session_state.g3 = "占用"
    else: st.session_state.g3 = "空闲"

# 3. 核心操作
st.divider()
if st.button("🚀 申请 [S1-5G] 进路", use_container_width=True, type="primary"):
    # 联锁逻辑校验
    if st.session_state.sw1 != "定位":
        err = "道岔不在定位，进路未准备好！"
        st.error(err)
        st.warning(f"🤖 AI 导师说：{ask_ai_expert(err)}")
    elif st.session_state.g3 == "占用":
        err = "前方 3G 区段被占用，开放信号会导致追尾！"
        st.error(err)
        st.warning(f"🤖 AI 导师说：{ask_ai_expert(err)}")
    else:
        st.session_state.sig = "开放"
        st.success("✅ 联锁闭合，信号已开放！")

if st.button("🔄 复位系统", use_container_width=True):
    st.session_state.sig = "关闭"
    st.rerun()