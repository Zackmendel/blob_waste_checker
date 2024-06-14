import streamlit as st
import pandas as pd
import sqlite3
import requests
from bs4 import BeautifulSoup
from eth_utils import decode_hex, function_signature_to_4byte_selector
from eth_abi import decode

# LINK TO THE CSS FILE
with open('style.css')as f:
 st.markdown(f"<style>{f.read()}</style>", 
             unsafe_allow_html = True)

st.title("Blob Wasted Space Checker")
st.write("There are three possible scenarios for this to happen. They are:")
st.header("1. I have my Blob data at hand")

# Create a simple SQLite database in memory
conn = sqlite3.connect(':memory:')

# Function to run the query
def run_query(blob_data):
    query = f"""
    WITH blob_data_extraction AS (
    SELECT
         '{blob_data}' AS blob_data
),
lengths_and_replacements AS (
    SELECT
        blob_data,
        LENGTH(blob_data) - 2 AS blob_length,  -- Subtracting 2 for the '0x' prefix
        LENGTH(REPLACE(blob_data, '0', '')) - 2 AS non_zero_length  -- Subtracting 2 for the '0x' prefix
    FROM
        blob_data_extraction
),
wasted_space_calculation AS (
    SELECT
        blob_data,
        blob_length / 2 AS blob_length_bytes,  -- Dividing by 2 to get the byte length
        (blob_length - non_zero_length) / 2 AS zero_bytes,  -- Dividing by 2 to get the byte count
        (non_zero_length * 1.0 / blob_length) AS used_percentage,
        ((blob_length - non_zero_length) * 1.0 / blob_length) AS wasted_percentage
    FROM
        lengths_and_replacements
)
SELECT
    blob_data,
    blob_length_bytes,
    zero_bytes,
    ROUND(used_percentage * 100, 2) AS used_percentage,
    ROUND(wasted_percentage * 100, 2) AS wasted_percentage
FROM
    wasted_space_calculation;
    """
    result = pd.read_sql_query(query, conn)
    return result

# Streamlit app
# st.subheader("Blob Data Extraction")

# Text area for user input
blob_data = st.text_area("Paste your blob data here", height=300)

if st.button("Run Query", key="run_query_blob_data"):
    if blob_data:
        result = run_query(blob_data)
        st.write("Query Result:")
        st.dataframe(result)

        # WE CREATE FOUR COLUMNS HERE TO HOLD THE METRIC
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label = "Blob Length(bytes)",
 value = (result.blob_length_bytes),
)
        col2.metric(label = "Zero Bytes",
 value = (result.zero_bytes),
)
        col3.metric(label = "Used Percentage",
 value = (result.used_percentage),
)
        col4.metric(label = "Wasted_percentage",
 value = (result.wasted_percentage),
)
    else:
        st.warning("Please paste your blob data first.")

# st.metric(label = "2015 Sales",
#  value = (result.blob_lenght_bytes),
# )

# ---------------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------------

st.header("2. I have my Blob Version Hash at hand")


# Function to fetch the blob data
def fetch_blob_data(blob_hash):
    url_template = "https://etherscan.io/blob/{blob_hash}?bid={bid}"
    
    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    for bid in possible_bids:
        url = url_template.format(blob_hash=blob_hash, bid=bid)
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Locate the textarea containing the data field
            data_field = soup.find('textarea', {'id': 'inputdata'})
            
            if data_field:
                return data_field.text.strip()
    
    return "Data field not found for any of the provided bids."

possible_bids = ["2578", "277119", "another_possible_bid", "yet_another_bid"]  # Add more possible bid values as needed

# Function to run the SQLite query on the blob data
def run_query(blob_data):
    conn = sqlite3.connect(':memory:')
    query = f"""
    WITH blob_data_extraction AS (
    SELECT
         '{blob_data}' AS blob_data
),
lengths_and_replacements AS (
    SELECT
        blob_data,
        LENGTH(blob_data) - 2 AS blob_length,  -- Subtracting 2 for the '0x' prefix
        LENGTH(REPLACE(blob_data, '0', '')) - 2 AS non_zero_length  -- Subtracting 2 for the '0x' prefix
    FROM
        blob_data_extraction
),
wasted_space_calculation AS (
    SELECT
        blob_data,
        blob_length / 2 AS blob_length_bytes,  -- Dividing by 2 to get the byte length
        (blob_length - non_zero_length) / 2 AS zero_bytes,  -- Dividing by 2 to get the byte count
        (non_zero_length * 1.0 / blob_length) AS used_percentage,
        ((blob_length - non_zero_length) * 1.0 / blob_length) AS wasted_percentage
    FROM
        lengths_and_replacements
)
SELECT
    blob_data,
    blob_length_bytes,
    zero_bytes,
    ROUND(used_percentage * 100, 2) AS used_percentage,
    ROUND(wasted_percentage * 100, 2) AS wasted_percentage
FROM
    wasted_space_calculation;
    """
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result

# Streamlit app
# st.title("Etherscan Blob Data Fetcher and Analyzer")

# Input for the blob versioned hash
blob_hash = st.text_input("Enter the blob versioned hash:", "0x01010893b86ebddb5fc64a836970c985f1c8a4e58ad74af1d5dff704af7c8d97")

if st.button("Fetch and Analyze Data", key="fetch_analyze_blob_hash"):
    with st.spinner("Fetching data..."):
        blob_data = fetch_blob_data(blob_hash)
        if "Failed" not in blob_data and "Data field not found" not in blob_data:
            with st.spinner("Running query on fetched data..."):
                result = run_query(blob_data)
                st.write("Query Result:")
                st.dataframe(result)
                # WE CREATE FOUR COLUMNS HERE TO HOLD THE METRIC
                col1, col2, col3, col4 = st.columns(4)
                col1.metric(label = "Blob Length(bytes)",
        value = (result.blob_length_bytes),
        )
                col2.metric(label = "Zero Bytes",
        value = (result.zero_bytes),
        )
                col3.metric(label = "Used Percentage",
        value = (result.used_percentage),
        )
                col4.metric(label = "Wasted_percentage",
        value = (result.wasted_percentage),
        )
        else:
            st.error(blob_data)





# ---------------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------------

st.subheader("3. I have my Transaction Hash data at hand")

# Your Etherscan API Key
ETHERSCAN_API_KEY = '8DRXP2DKT85IUQDWDFZNWD81NXZUVFQPI7'

# Function to fetch transaction details from Etherscan
def get_transaction_details(tx_hash):
    tx_url = f"https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={tx_hash}&apikey={ETHERSCAN_API_KEY}"
    tx_response = requests.get(tx_url)
    tx_json = tx_response.json()

    if 'result' not in tx_json or not tx_json["result"]:
        raise ValueError(f"Error fetching transaction details: {tx_json}")

    return tx_json["result"]

# Function to decode the transaction input data
def decode_input_data(input_data):
    if input_data == '0x':
        st.write("No input data.")
        return None

    input_data = decode_hex(input_data)
    method_id = input_data[:4]
    params = input_data[4:]

    # Print the method ID and parameters for debugging
    st.write(f"Method ID: {method_id.hex()}")
    st.write(f"Params: {params.hex()}")

    # Example method signatures for common transactions (ERC-20 Transfer, ERC-721 Transfer)
    method_abis = {
        function_signature_to_4byte_selector('transfer(address,uint256)'): ['address', 'uint256'],
        function_signature_to_4byte_selector('transferFrom(address,address,uint256)'): ['address', 'address', 'uint256'],
        function_signature_to_4byte_selector('safeTransferFrom(address,address,uint256)'): ['address', 'address', 'uint256'],
        function_signature_to_4byte_selector('safeTransferFrom(address,address,uint256,bytes)'): ['address', 'address', 'uint256', 'bytes'],
    }

    if method_id not in method_abis:
        st.write("Unknown method ID")
        return None

    abi_types = method_abis[method_id]
    decoded_params = decode(abi_types, params)

    return {
        'method_id': method_id.hex(),
        'params': decoded_params
    }

# Function to fetch the blob data
def fetch_blob_data(blob_hash):
    url_template = "https://etherscan.io/blob/{blob_hash}?bid={bid}"
    
    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    for bid in possible_bids:
        url = url_template.format(blob_hash=blob_hash, bid=bid)
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Locate the textarea containing the data field
            data_field = soup.find('textarea', {'id': 'inputdata'})
            
            if data_field:
                return data_field.text.strip()
    
    return "Data field not found for any of the provided bids."

possible_bids = ["2578", "277119", "another_possible_bid", "yet_another_bid"]  # Add more possible bid values as needed
    


# ---------------------------------------------------------------------------------------------------------------------------------



# Function to run the SQLite query on the blob data
def run_query(blob_data):
    conn = sqlite3.connect(':memory:')
    query = f"""
    WITH blob_data_extraction AS (
    SELECT
         '{blob_data}' AS blob_data
),
lengths_and_replacements AS (
    SELECT
        blob_data,
        LENGTH(blob_data) - 2 AS blob_length,  -- Subtracting 2 for the '0x' prefix
        LENGTH(REPLACE(blob_data, '0', '')) - 2 AS non_zero_length  -- Subtracting 2 for the '0x' prefix
    FROM
        blob_data_extraction
),
wasted_space_calculation AS (
    SELECT
        blob_data,
        blob_length / 2 AS blob_length_bytes,  -- Dividing by 2 to get the byte length
        (blob_length - non_zero_length) / 2 AS zero_bytes,  -- Dividing by 2 to get the byte count
        (non_zero_length * 1.0 / blob_length) AS used_percentage,
        ((blob_length - non_zero_length) * 1.0 / blob_length) AS wasted_percentage
    FROM
        lengths_and_replacements
)
SELECT
    blob_data,
    blob_length_bytes,
    zero_bytes,
    ROUND(used_percentage * 100, 2) AS used_percentage,
    ROUND(wasted_percentage * 100, 2) AS wasted_percentage
FROM
    wasted_space_calculation;
    """
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result

# Streamlit UI
# st.title("Ethereum Transaction Decoder and Blob Analyzer")

transaction_hash = st.text_input("Enter Transaction Hash", value='0x021f91dc6e11c936ce4c785fbcc48eda94e3135f7d31766f288cdc71db8f912a')

if st.button("Fetch Transaction Details", key="fetch_tx_details"):
    try:
        # Fetch the transaction details
        tx_details = get_transaction_details(transaction_hash)

         # Create a collapsible container for transaction details
        with st.expander("Transaction Details", expanded=False):
            # Display the transaction details inside the expander
            st.write(tx_details)

        # Decode the input data of the transaction
        decoded_input = decode_input_data(tx_details["input"])

        # Display decoded input data
        if "blobVersionedHashes" in tx_details:
            st.write(f"Blob Hashes Found")

            # Save blobVersionedHashes to session state
            st.session_state.blob_versioned_hashes = tx_details["blobVersionedHashes"]
        else:
            st.write("No blob hashes found in the transaction input data.")
        
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Check if blobVersionedHashes exist in session state
if 'blob_versioned_hashes' in st.session_state:
    blob_versioned_hashes = st.session_state.blob_versioned_hashes
    st.write(f"Blob Versioned Hashes (Count: {len(blob_versioned_hashes)}):")
    blob_hash_selected = st.selectbox("Select a Blob Versioned Hash", blob_versioned_hashes)
    st.write(f"Selected Blob Versioned Hash: {blob_hash_selected}")
    blob_hash = blob_hash_selected

    if st.button("Fetch and Analyze Data", key="fetch_analyze_tx_blob_hash"):
        with st.spinner("Fetching data..."):
            blob_data = fetch_blob_data(blob_hash)
            if "Failed" not in blob_data and "Data field not found" not in blob_data:
                with st.spinner("Running query on fetched data..."):
                    result = run_query(blob_data)
                    st.write("Query Result:")
                    st.dataframe(result)
                    col1, col2, col3, col4 = st.columns(4)
                col1.metric(label = "Blob Length(bytes)",
        value = (result.blob_length_bytes),
        )
                col2.metric(label = "Zero Bytes",
        value = (result.zero_bytes),
        )
                col3.metric(label = "Used Percentage",
        value = (result.used_percentage),
        )
                col4.metric(label = "Wasted_percentage",
        value = (result.wasted_percentage),
        )
            else:
                st.error(blob_data)
