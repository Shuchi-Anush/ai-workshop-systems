import streamlit as st

def apply_enterprise_theme():
    """Injects custom CSS to create a modern SaaS application feel."""
    css = """
    <style>
        /* Base typography and clean UI */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Card styling */
        .candidate-card {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #eaeaea;
            margin-bottom: 20px;
            color: #333333;
        }
        
        /* Dark mode compatibility for cards */
        @media (prefers-color-scheme: dark) {
            .candidate-card {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                color: #ffffff;
            }
        }
        
        /* Skill chips */
        .skill-chip {
            display: inline-block;
            background-color: #e0f2fe;
            color: #0369a1;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 12px;
            font-weight: 500;
            margin-right: 6px;
            margin-bottom: 6px;
        }
        
        /* Match percentage badges */
        .match-badge-high {
            background-color: #dcfce7;
            color: #166534;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
        }
        .match-badge-med {
            background-color: #fef08a;
            color: #854d0e;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
        }
        .match-badge-low {
            background-color: #fee2e2;
            color: #991b1b;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #f8fafc;
            border-right: 1px solid #e2e8f0;
        }
        @media (prefers-color-scheme: dark) {
            section[data-testid="stSidebar"] {
                background-color: #0f172a;
                border-right: 1px solid #1e293b;
            }
        }
        
        /* Headers */
        h1, h2, h3 {
            font-weight: 600 !important;
            letter-spacing: -0.5px;
        }
        
        /* Buttons */
        .stButton>button {
            border-radius: 6px;
            font-weight: 500;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
