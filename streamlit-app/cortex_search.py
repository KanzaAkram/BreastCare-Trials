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
    # Add layout styles and title
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
            </h1>
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

    st.sidebar.number_input("Number of Results", value=5, key="limit", min_value=3, max_value=10, help="Select the number of search results you want to display. This will control how many results are shown from your search query. The minimum number of results is 3, and the maximum is 10. Choose any value within this range.")
    

    st.sidebar.checkbox("Summarize Results", key="summarize",help=" If you want a summary with the answer, check this and search the question.")

    # Sidebar - Frequently Asked Questions

    st.sidebar.header("Frequently Asked Questions")

# Sidebar Radio Buttons for FAQs
    faq_options = [
        "What is the purpose of breast cancer clinical trials?",
        "What are the phases of a breast cancer clinical trial?",
        "How do I determine if I am eligible for a breast cancer clinical trial?",
        "What are the risks and benefits of participating in a clinical trial?",
        "Are there clinical trials for breast cancer prevention?"
    ]

    # Sidebar FAQ selection
    selected_faq = st.sidebar.radio(
        "Click a question to search:",
        options=faq_options,
        key="selected_question"
    )

    # Initialize session state for query before using it in the text_area
    if "query" not in st.session_state:
        st.session_state.query = ""  # Default value is empty, no pre-population

    # Update session state only if the user selects a FAQ and hasn't modified the text manually
    if selected_faq and not st.session_state.query:
        st.session_state.query = selected_faq  # Set query if it's empty

    # Main Text Area for User Input
    query = st.text_area(
        "Enter your query:",
        value=st.session_state.query,  # Populate from session state
        key="query",
        height=100,
        label_visibility="collapsed",
        placeholder="What do you want to know about breast cancer clinical trials?"
    )

    # If the user has typed in the query, ensure it updates session state
    if query != st.session_state.query:
        st.session_state.query = query  # Update session state with typed query
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
    You are an intelligent and empathetic assistant specialized in breast cancer clinical trials. Your purpose is to provide accurate, comprehensive, and detailed information about clinical trials based on documents and user queries.

    Your responses should focus on:
    - **Trial Information**: Provide details like trial name, phase, purpose, and eligibility criteria.
    - **Eligibility Requirements**: Clarify inclusion and exclusion criteria in an easy-to-understand way.
    - **Locations and Contacts**: Share trial locations and contact details where applicable.
    - **Procedures and Risks**: Explain the trial procedures, risks, and potential benefits.
    - **Next Steps**: Offer advice on how users can proceed, such as contacting trial coordinators or consulting their doctor.

    Use the following structure to craft responses. Ensure headings are bold and remove unnecessary symbols like hashes or slashes:
    
    - **Trial Name and Overview**
    - **Phase and Objective**
    - **Eligibility Criteria** (with subheadings for Inclusion and Exclusion Criteria)
    - **Trial Locations and Contact Information**
    - **Suggested Next Steps**
    
    When writing a detailed response, use simple language to ensure clarity for users who may not have a medical background. Be supportive and address concerns empathetically.

    If the document contains incomplete or unclear information, advise the user to visit trusted resources such as [ClinicalTrials.gov](https://clinicaltrials.gov) or consult their healthcare provider for more details. Always prioritize user understanding and support.

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


def summarize_search_results_short(results, query,search_col):
    """
    Returns a concise answer of the search results based on the user's query of breast cancer clinical trial
    """
    search_result_str = ""
    for i, r in enumerate(results):
        search_result_str += f"Result {i+1}: {r[search_col]} \n"

    prompt = f"""
        [INST]
        You are a highly intelligent assistant specialized in breast cancer clinical trials. Based on the user’s query and the provided clinical trial document, generate a concise and accurate summary that directly answers the user’s question. Your summary should:
        Address the key aspects of the user’s query without including unnecessary details.
        Highlight only the most relevant information, such as trial purpose, phase, eligibility criteria, and location, when applicable.
        Use simple, user-friendly language that is easy to understand, avoiding technical jargon unless the user explicitly asks for it.
        Be empathetic and supportive in tone, keeping the summary clear and engaging.
        If the document lacks sufficient information, politely inform the user and suggest they consult ClinicalTrials.gov or their healthcare provider for more details.
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

    # Ensure query exists in session state to avoid unnecessary processing
    if "query" not in st.session_state:
        st.session_state.query = ""  # Initialize the query if it's not already in session state

    # Search Button Logic
    if st.button("Search Clinical Trials"):
        if not st.session_state.query.strip():  # If query is empty
            st.warning("Please enter a query or select a question from the FAQ sidebar.")
        else:
            # Perform the search
            results = query_cortex_search_service(st.session_state.query)
            search_col = get_search_column(st.session_state.cortex_search_service)

            # Display detailed results
            if results:
                with st.spinner("Fetching answer..."):
                    detailed_answer = summarize_search_results(results, st.session_state.query, search_col)
                    st.markdown(detailed_answer)

                # Display concise summary if enabled
                if st.session_state.summarize:
                    with st.spinner("Generating concise summary..."):
                        concise_summary = summarize_search_results_short(results, st.session_state.query, search_col)
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