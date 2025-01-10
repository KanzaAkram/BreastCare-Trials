# BreastCare Trials

## 📖 Problem Statement

Breast cancer is one of the most prevalent forms of cancer worldwide, accounting for **11.7% of all new cancer cases** (Global Cancer Observatory, 2022). Despite advances in medical science, **heterogeneity in molecular subtypes**, **varying stages of diagnosis**, and **diverse therapy responses** pose significant challenges for achieving uniform patient outcomes.

### Challenges in Breast Cancer Care:
1. **Data Overload**: Clinical trials generate vast, complex datasets that are difficult to navigate and utilize effectively.
2. **Accessibility Gap**: Clinicians, researchers, and patients often struggle to access and interpret critical clinical trial information.
3. **Time Sensitivity**: Delays in finding relevant clinical trial data can hinder timely treatment decisions.
4. **Personalization**: Clinical trial data is often generalized and not tailored to specific patient profiles.

These barriers hinder innovation and limit the impact of clinical trial data, making it difficult to maximize its potential in advancing breast cancer care.

---

## 🌟 Solution: BreastCare Trials

**BreastCare Trials** is an AI-powered **Retrieval-Augmented Generation (RAG)** application designed to bridge the gap between complex clinical trial data and its end users—clinicians, researchers, and patients. By combining cutting-edge AI technologies, we empower healthcare stakeholders with precise, actionable insights to revolutionize breast cancer care.

### Key Features:
1. **Streamlined Search**: Leverages **Snowflake Cortex Search** for precise and efficient retrieval of extensive National Cancer Institute (NCI) clinical trial data.
2. **AI-Driven Summaries**: Generates concise, human-readable insights tailored to user queries using **Mistral-large2**.
3. **Patient-Centric Insights**: Tailors clinical trial recommendations and summaries based on specific patient profiles and queries.
4. **Interactive Frontend**: A user-friendly interface built with **Streamlit**, ensuring intuitive navigation for medical professionals and patients alike.
5. **Real-Time Updates**: Provides up-to-date clinical trial information, ensuring users access the latest data.

---

## 🔨 How I Built It

### Tech Stack:
- **Snowflake Cortex Search**: Enables fast, precise retrieval of clinical trial data.
- **Mistral-large2**: Generates context-aware summaries to simplify complex information.
- **Streamlit**: Delivers an interactive and accessible frontend.
- **NCI Clinical Trial Data**: Powers the platform with clinical trial documents for breast cancer.

### Development Process:
1. **Model Integration**: Seamlessly combined Snowflake Cortex Search with Mistral-large-v2 for robust RAG capabilities.
2. **User-Centric Design**: Focused on building an intuitive interface that caters to both medical professionals and patients.

---

## 🚀 Getting Started

Follow these instructions to set up and run BreastCare Trials locally.

### Prerequisites

Ensure the following are installed on your system:
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/)
- [Git](https://git-scm.com/)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YourUsername/BreastCare-Trials.git
   cd BreastCare-Trials
   ```

2. Navigate to the Streamlit application directory:
   ```bash
   cd streamlit-app
   ```

---

## 🛠 Setting Up Conda Environment

1. **Initialize Conda**:
   ```bash
   conda init
   ```

2. **Create the Environment**:
   ```bash
   conda env create -n cortex-search -f conda_env.yml
   ```

3. **Activate the Environment**:
   ```bash
   conda activate cortex-search
   ```

4. **Verify Installation**:
   ```bash
   conda list
   ```

---

## 🔒 Setting Up Streamlit Secrets

1. Create a `.streamlit` folder:
   ```bash
   mkdir .streamlit
   ```

2. Add a `secrets.toml` file with the following format:
   ```toml
   [connections.conn]
   account = "<your_account>"
   user = "<your_username>"
   password = "<your_password>"
   warehouse = "<your_warehouse>"
   database = "<your_database>"
   schema = "<your_schema>"
   client_session_keep_alive = true
   ```

Replace the placeholders with your actual credentials. **Do not share sensitive credentials publicly.**

---

## 📋 Generating `requirements.txt`

To create a `requirements.txt` file for the Streamlit app:
```bash
pip freeze > requirements.txt
```

---

## 🤝 Contributing

Contributions are welcome! Follow these steps:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Add feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.

---

