import streamlit as st
from snowflake.core import Root
import snowflake.connector

MODELS = [
    "mistral-large",
    "snowflake-arctic",
    "llama3-70b",
    "llama3-8b",
]

@st.cache_resource
def make_session():
    """
    Initialize the connection to snowflake using the `conn` connection stored in `.streamlit/secrets.toml`
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
    st.title("Breast Cancer Trial Chatbot")
    st.markdown("""
        <style>
    .main {
        background: #f4f8fa; /* Light background color */
        border-radius: 15px;
        padding: 20px;
    }
    h1 {
        font-family: "Arial", sans-serif;
        color: #d5006d; /* Pink color for the heading */
    }
    .sidebar .sidebar-content {
        background-color: #000000; /* Black background for sidebar */
        color: #ffffff; /* White text in the sidebar */
    }
    .stTextInput input {
        background-color: #ffffff; /* White background for input fields */
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
    st.sidebar.markdown(f"Current database and schema: `{db}.{schema}`".replace('"', ''))

def init_config_options():
    """
    Initialize sidebar configuration options
    """
    st.text_area("Enter your query:", value="", key="query", height=100, label_visibility="collapsed")
    st.sidebar.selectbox("Cortex Search Service", get_available_search_services(), key="cortex_search_service")
    st.sidebar.number_input("Number of Results", value=5, key="limit", min_value=3, max_value=10)
    st.sidebar.selectbox("Select Summarization Model", MODELS, key="model")
    st.sidebar.checkbox("Summarize Results", key="summarize")

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
    Returns an AI summary of the search results based on the user's query
    """
    search_result_str = ""
    for i, r in enumerate(results):
        search_result_str += f"Result {i+1}: {r[search_col]} \n"

    prompt = f"""
        [INST]
        You are a helpful AI Assistant embedded in a search application. You will be provided a user's search query and a set of search result documents.
        Your task is to provide a detailed answer with all relevant details about clinical trial to the user's query with the help of the provided the search results.
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
    Display the AI summary in the UI
    """
    st.subheader("AI Summary")
    st.markdown(f"<div class='main'>{summary}</div>", unsafe_allow_html=True)

def display_search_results(results, search_col):
    """
    Display the search results in the UI
    """
    st.subheader("Search Results")
    for i, result in enumerate(results):
        container = st.expander(f"Result {i+1}", expanded=True)
        container.markdown(result[search_col])

def main():
    init_layout()
    init_config_options()

    if not st.session_state.query:
        return
    results = query_cortex_search_service(st.session_state.query)
    search_col = get_search_column(st.session_state.cortex_search_service)
    if st.session_state.summarize:
        with st.spinner("Summarizing results..."):
            summary = summarize_search_results(results, st.session_state.query, search_col)
            display_summary(summary)
    display_search_results(results, search_col)


if __name__ == "__main__":
    st.set_page_config(page_title="Breast Cancer Trial Chatbot", layout="wide")
    
    session = make_session()
    root = Root(session)
    db, schema = session.get_current_database(), session.get_current_schema()
    
    main()
