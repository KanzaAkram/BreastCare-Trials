import streamlit as st
from snowflake.core import Root
import snowflake.connector

MODELS = [
    "mistral-large2"
]

@st.cache_resource
def make_session():
    """
    Initialize the connection to snowflake using the conn connection stored in .streamlit/secrets.toml
    """
    conn = st.connection("conn", type="snowflake")
    return conn.session()

def get_available_search_services():
    """
    Returns list of cortex search services available in the current schema
    """
    search_service_results = session.sql(f"SHOW CORTEX SEARCH SERVICES IN SCHEMA {db}.{schema}").collect()
    return [svc.name for svc in search_service_results]

def get_search_column(svc):
    """
    Returns the name of the search column for the provided cortex search service
    """
    search_service_result = session.sql(f"DESC CORTEX SEARCH SERVICE {svc}").collect()[0]
    return search_service_result.search_column

def init_layout():
    # st.title("BreastCare Trial Chatbot")
    st.markdown("""
        <style>
        .main {
            background: #d5006d; /* Light background color */
            border-radius: 15px;
            padding: 20px;
        }
        h1 {
            font-family: "Arial", sans-serif;
            color: #d5006d; /* Pink color for the heading */
        }
        .ribbon {
            background: linear-gradient(45deg, #ff6ec7, #d5006d);
            color: white;
            padding: 5px 15px;
            font-size: 16px;
            font-weight: bold;
            text-transform: uppercase;
            display: inline-block;
            position: relative;
            top: -30px;
            left: -20px;
            margin-top:30px;
            margin-left:20px;
        }
        .sidebar .sidebar-content {
            background-color: #000000; /* Black background for sidebar */
            color: #ffffff; /* White text in the sidebar */
        }
        .stTextInput input {
            background-color: #d5006d; /* White background for input fields */
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
        }
        .stButton button {
            background-color: #d5006d; /* Pink button background */
            color: white;
            font-size: 16px;
            border-radius: 8px;
            padding: 12px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display: flex; margin-bottom:50px; margin-top: 10px;">
        <h1 style="margin-right: 10px;color:#d5006d; ">BreastCare Trial Chatbot</h1>
        <img src="https://static.cdnlogo.com/logos/p/45/pink-ribbon.svg" alt="Pink Ribbon Logo" style="max-height: 80px; max-width: 100%;">
    </div>
""", unsafe_allow_html=True)



    with st.sidebar:
        st.markdown("""
            <h2 style="color: #d5006d; text-align: center; font-family: 'Arial', sans-serif;">
                Clinical Trials On-the-Go
            </h2>
            <p style="text-align: center; color: #333; font-size: 14px; font-weight: bold; font-family: 'Arial', sans-serif;">
                Discover and explore breast cancer clinical trials easily and quickly.
            </p>
        """, unsafe_allow_html=True)

    
    # Adding ribbon after the main heading
    
    # st.sidebar.markdown(f"Current database and schema: {db}.{schema}".replace('"', ''))

def init_config_options():
    """
    Initialize sidebar configuration options
    """
    st.markdown("""
    <style>
        .stTextArea textarea {
            background-color: #fff4f2;
            border-radius: 5px;
            padding: 10px;
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

    st.text_area("Enter your query:", value="", key="query", height=100, label_visibility="collapsed", 
                placeholder="What do you want to know about breast cancer clinical trials?")

    st.markdown('<div class="ribbon">Search for Clinical Trials</div>', unsafe_allow_html=True)
    st.sidebar.selectbox("Cortex Search Service", get_available_search_services(), key="cortex_search_service")
    st.sidebar.number_input("Number of Results", value=5, key="limit", min_value=3, max_value=10)
    st.sidebar.selectbox("Select Summarization Model", MODELS, key="model")
    st.sidebar.checkbox("Summarize Results", key="summarize")
    st.sidebar.header("Frequently Asked Questions")

    # Adding questions as clickable links
    st.sidebar.markdown("""
    - [What is the purpose of breast cancer clinical trials?](#)
    - [What are the phases of a breast cancer clinical trial?](#)
    - [How do I determine if I am eligible for a breast cancer clinical trial?](#)
    - [What are the risks and benefits of participating in a clinical trial?](#)
    - [Are there clinical trials for breast cancer prevention?](#)
    """)


def query_cortex_search_service(query):
    """
    Queries the cortex search service in the session state and returns a list of results
    """
    cortex_search_service = (
        root
        .databases[db]
        .schemas[schema]
        .cortex_search_services[st.session_state.cortex_search_service]
    )
    context_documents = cortex_search_service.search(query, [], limit=st.session_state.limit)
    return context_documents.results

def complete(model, prompt):
    """
    Queries the cortex COMPLETE LLM function with the provided model and prompt
    """
    try:
        resp = session.sql("select snowflake.cortex.complete(?, ?)", params=(model, prompt)).collect()[0][0]
    except Exception as e:
        resp = f"COMPLETE error: {e}"
    return resp

def summarize_search_results(results, query, search_col):
    """
    Returns a detailed answer of the search results based on the user's query of breast cancer clinical trial
    """
    search_result_str = ""
    for i, r in enumerate(results):
        search_result_str += f"Result {i+1}: {r[search_col]} \n"

    prompt = f"""
        [INST]
        You are a helpful AI Assistant embedded in a search application. You will be provided a user's search query and a set of search result documents.
        Your task is to provide a detailed answer with all relevant details about clinical trial to the user's query with the help of the provided the search results nd if user query is irrelevant return sorry no results.
        <user_query>
        {query}
        </user_query>
        <search_results>
        {search_result_str}
        </search_results>
        [/INST]
    """
    
    resp = complete(st.session_state.model, prompt)
    return resp

def display_summary(summary):
    """
    Display a very concise AI summary in the UI
    """
    st.subheader("AI Summary")
    st.markdown(f"<div class='main'>{summary}</div>", unsafe_allow_html=True)

def display_search_results(results, search_col):
    """
    Display the search results in the UI with sources displayed up to 25 characters
    """
    st.subheader("Search Results")
    for i, result in enumerate(results):
        container = st.expander(f"Result {i+1}", expanded=True)
        # Assuming 'search_col' is a key in the result, adjust as necessary based on your data structure
        container.markdown(result[search_col][:100])  # Limit the output to the first 100 characters/words

def main():
    init_layout()
    init_config_options()

    if not st.session_state.query:
        return

    # Trigger search on pressing the Search button
    if st.session_state.query and st.button("Search"):
        results = query_cortex_search_service(st.session_state.query)
        search_col = get_search_column(st.session_state.cortex_search_service)

        # Option to toggle summary visibility
        if st.session_state.summarize:
            with st.spinner("Summarizing results..."):
                summary = summarize_search_results(results, st.session_state.query, search_col)
                display_summary(summary)

        display_search_results(results, search_col)
        
        # Display detailed answer first
        with st.spinner("Fetching detailed results..."):
            search_answer = summarize_search_results(results, st.session_state.query, search_col)
            st.markdown(search_answer)
        
        # Display concise summary below detailed answer without reload
        if st.session_state.summarize:
            with st.spinner("Generating concise summary..."):
                concise_summary = summarize_search_results(results, st.session_state.query, search_col)
                display_summary(concise_summary)

if __name__ == "__main__":
    # st.set_page_config(page_title="BreastCare Trial Chatbot", layout="wide")
    
    session = make_session()
    root = Root(session)
    db, schema = session.get_current_database(), session.get_current_schema()
    
    main()
