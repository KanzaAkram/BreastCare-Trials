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
            background: #fff4f2; /* Light background color */
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
            background-color: #000000; 
            color: #ffffff; 
        }
        .stTextInput input {
            background-color: #fff4f2; 
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
        }
        .stButton button {
        background: linear-gradient(90deg, #d5006d, #9c27b0); /* Pink to purple gradient background */
        color: white;
        font-size: 16px;
        border-radius: 8px;
        padding: 12px;
        border: none; /* Remove border */
        transition: background-color 0.3s, color 0.3s; 
        cursor: pointer;
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
            <h1 style="color: #d5006d; text-align: center; font-family: 'Arial', sans-serif;">
                Breast Cancer Clinical Trials
            </h2>
            <p style="text-align: center; color: purple; font-size: 14px; font-weight: bold; margin-bottom:50px; font-family: 'Arial', sans-serif;">
                Discover and explore breast cancer clinical trials easily and quickly.
            </p>
        """, unsafe_allow_html=True)


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

    # Sidebar options for other configurations
    st.sidebar.selectbox(
    "Cortex Search Service",
    get_available_search_services(),
    key="cortex_search_service",
    help="Select the search service you want to use. Each service provides different capabilities for clinical trials."
)

    st.sidebar.selectbox(
    "Select Summarization Model",
    MODELS,
    key="model",
    help="Choose a summarization model. Each model has different capabilities for generating summaries."
)

    st.sidebar.number_input("Number of Results", value=5, key="limit", min_value=3, max_value=10, help="Select the number of search results you want to display. This will control how many results are shown from your search query.The minimum number of results is 3, and the maximum is 10. Choose any value within this range.")
    

    st.sidebar.checkbox("Summarize Results", key="summarize",help=" If you want a summary with the answer, check this and search the question.")

    # Sidebar - Frequently Asked Questions
    st.sidebar.header("Frequently Asked Questions")
    question = st.sidebar.radio(
        "Click a question to search:",
        options=[
            "What is the purpose of breast cancer clinical trials?",
            "What are the phases of a breast cancer clinical trial?",
            "How do I determine if I am eligible for a breast cancer clinical trial?",
            "What are the risks and benefits of participating in a clinical trial?",
            "Are there clinical trials for breast cancer prevention?"
        ],
        key="selected_question",
        index=0  # Default selection
    )

    # Set the text area value dynamically based on sidebar question selection
    if question:
        st.session_state.query = question

    # Main Text Area
    st.text_area(
        "Enter your query:",
        value=st.session_state.query if "query" in st.session_state else "",
        key="query",
        height=100,
        label_visibility="collapsed",
        placeholder="What do you want to know about breast cancer clinical trials?"
    )


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

def summarize_search_results(results, query,search_col):
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
        # {search_result_str}
        </search_results>
        [/INST]
    """
    
    resp = complete(st.session_state.model, prompt)
    return resp


def summarize_search_results_short(results, query,search_col):
    """
    Returns a concise answer of the search results based on the user's query of breast cancer clinical trial
    """
    search_result_str = ""
    for i, r in enumerate(results):
        search_result_str += f"Result {i+1}: {r[search_col]} \n"

    prompt = f"""
        [INST]
        You are a helpful AI Assistant embedded in a search application. You will be provided a user's search query and a set of search result documents.
        Your task is to provide a very concise answer with all relevant details about clinical trial to the user's query with the help of the provided the search results nd if user query is irrelevant return sorry no results.
        <user_query>
        {query}
        </user_query>
        <search_results>
        # {search_result_str}
        </search_results>
        [/INST]
    """
    
    resp = complete(st.session_state.model, prompt)
    return resp



def display_summary(summary):
    """
    Display a very concise AI summary in the UI
    """
    # st.subheader("AI Summary")
    st.markdown(f"<div class='main'>{summary}</div>", unsafe_allow_html=True)


def apply_sidebar_styles():
    sidebar_styles = """
    <style>
    [data-testid="stSidebar"] {
        background: linear-gradient(90deg, #f8bbd0, #e1bee7); /* Light pink to light purple gradient */
        padding: 20px;
        color: #333333; /* Text color */
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #4a148c; /* Dark purple for headings */
    }
    </style>
    """
    st.markdown(sidebar_styles, unsafe_allow_html=True)


def main():
    apply_sidebar_styles()  # Apply sidebar styling
    init_layout()
    init_config_options()

    # Ensure `query` exists in session state to avoid unnecessary processing
    if "query" not in st.session_state or not st.session_state.query:
        st.warning("Please enter or select a query to start the search.")
        return

    # Trigger search on pressing the Search button
    if st.button("Search Clinical Trials"):
            results = query_cortex_search_service(st.session_state.query)
            search_col = get_search_column(st.session_state.cortex_search_service)

            # Display detailed results
            if results:
                # Fetch and display detailed answer
                with st.spinner("Fetching answer..."):
                    detailed_answer = summarize_search_results(results, st.session_state.query,search_col)
                    st.markdown(detailed_answer)

                # Display concise summary if summarization is enabled
                if st.session_state.summarize:
                    with st.spinner("Generating concise summary..."):
                        concise_summary = summarize_search_results_short(results, st.session_state.query,search_col)
                        st.subheader("Summary:")
                        display_summary(concise_summary)
            else:
                st.error("No results found. Please refine your query or try another.")

if __name__ == "__main__":
    # Set up the session and database connection (if required)
    session = make_session()
    root = Root(session)
    db, schema = session.get_current_database(), session.get_current_schema()
    
    # Call the main function
    main()
