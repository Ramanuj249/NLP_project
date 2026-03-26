import streamlit as st

def apply_sidebar_style():
    st.markdown("""
    <style>
    /* ── Sidebar background ── */
    [data-testid="stSidebar"] {
        background-color: #0f0f0f !important;
        border-right: 1px solid #1e1e1e;
    }

    /* ── Hide default streamlit nav header ── */
    [data-testid="stSidebarNav"]::before {
        content: "DOCGEN AI";
        display: block;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.18em;
        color: #e8520a;
        padding: 24px 20px 12px 20px;
        border-bottom: 1px solid #1e1e1e;
        margin-bottom: 10px;
    }

    /* ── Nav links base ── */
    [data-testid="stSidebarNav"] a {
        display: flex !important;
        align-items: center !important;
        padding: 11px 16px !important;
        margin: 2px 8px !important;
        border-radius: 8px !important;
        color: #888 !important;
        font-size: 13.5px !important;
        font-weight: 400 !important;
        text-decoration: none !important;
        transition: all 0.15s ease !important;
        border: 1px solid transparent !important;
    }

    /* ── Nav link hover ── */
    [data-testid="stSidebarNav"] a:hover {
        background-color: #1a1a1a !important;
        color: #ccc !important;
        border-color: #2a2a2a !important;
    }

    /* ── Active page ── */
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: linear-gradient(90deg, #e8520a18, #e8520a05) !important;
        border-left: 3px solid #e8520a !important;
        border-radius: 0 8px 8px 0 !important;
        color: #f0f0f0 !important;
        font-weight: 500 !important;
        margin-left: 8px !important;
        padding-left: 13px !important;
    }

    /* ── Nav link text spans ── */
    [data-testid="stSidebarNav"] a span {
        font-size: 13.5px !important;
    }

    /* ── Sidebar footer info ── */
    [data-testid="stSidebarUserContent"] {
        padding: 0 !important;
    }

    /* ── Scrollbar ── */
    [data-testid="stSidebar"]::-webkit-scrollbar {
        width: 4px;
    }
    [data-testid="stSidebar"]::-webkit-scrollbar-thumb {
        background: #2a2a2a;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar bottom info
    with st.sidebar:
        st.markdown("""
        <div style="
            position: fixed;
            bottom: 24px;
            left: 0;
            width: 240px;
            padding: 12px 20px;
            border-top: 1px solid #1e1e1e;
            background: #0f0f0f;
        ">
            <p style="font-size: 11px; color: #444; margin: 0; letter-spacing: 0.05em;">
                POWERED BY AI · v1.0
            </p>
        </div>
        """, unsafe_allow_html=True)