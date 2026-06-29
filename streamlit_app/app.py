import streamlit as st


unit_converter_page = st.Page("page1b_bidirectional_converter.py", title="Unit Converter", icon="🔢")
# bidirectional_converter_page = st.Page(
#     "page1b_bidirectional_converter.py",
#     title="Bidirectional Converter",
#     icon="↔️",
# )
linewidth_converter_page = st.Page("page2_linewidth_converter.py", title="Linewidth Converter", icon="📏")
plots_page = st.Page("page3_plots.py", title="Plots", icon="📈")
tables_page = st.Page("page4_tables.py", title="Tables", icon="📊")
parquet_loader_page = st.Page("page5_parquet_loader.py", title="Parquet Loader", icon="📋")
ring_resonator_page = st.Page("page6_ring-resonator-model.py", title="Ring Resonator Model", icon="🔄")
pid_lock_page = st.Page("page7_pid_lock.py", title="PID Locking Simulation", icon="🖥️")
page8 = st.Page("page8_searching_lock_parameters.py", title="Searching Lock Parameters", icon="🔍")
pid_simulate_page = st.Page("page9_pid_simulate.py", title="PID Temperature Sim", icon="🌡️")
about_page = st.Page("about_page.py", title="About", icon="ℹ️")

pg = st.navigation([
    unit_converter_page,
    # bidirectional_converter_page,
    linewidth_converter_page,
    plots_page,
    tables_page,
    parquet_loader_page,
    ring_resonator_page,
    pid_lock_page,
    page8,
    pid_simulate_page,
    about_page])

st.set_page_config(page_title="Photonics Calculator", page_icon="🔬")

pg.run()
