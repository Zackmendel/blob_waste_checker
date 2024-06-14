import streamlit as st
import pandas as pd
import sqlite3
import requests
from bs4 import BeautifulSoup
from eth_utils import decode_hex, function_signature_to_4byte_selector
from eth_abi import decode

# Define the pages
def introduction():
    st.title(":blue[Blob Wasted Space Checker]")
    st.subheader(":red[Welcome to the Blob Wasted Space Checker application. Use the sidebar to navigate to different sections.]")
    st.markdown("""
                
## :blue[HOW IT WORKS]
   :red[This tool simply counts the number of ZEROs present in the blob data and compares it to the total number of characters to get the percentage of the total characters that is zero, in this situation, the WASTED SPACE.]             
### :blue[Use the NAVIGATION on the sidebar to pick the option you have:]
1. :red[I have blob data.] This can be copied directly from etherscan.io under the blobs section of the transaction page
2. :red[I have blob hash.] This is probably one that you have at hand. Code uses just a sample hash and might not work with another hash
3. :red[I have Tx has.] This is having the transaction hash of that carries the blob. It uses the hash to get the blob hashes and then  your allowed to choose which blob hash to analyze.
    
## :blue[THE0RY]                
            
The term :blue["Wasted blob space tracker"] refers to a mechanism used to monitor and track how much of the allocated storage space (in this case, 128KB) within a blob is :red[unused or filled with zeros]. In the context of data storage, particularly with blob storage (binary large object storage), it is common to allocate a fixed size for storage purposes. However, not all of this space may be actively used to store meaningful data. 

Here's a breakdown of the key components:

1. :blue[**Blob**:] A binary large object, typically used to store data such as images, videos, or other multimedia objects, as well as chunks of text or binary data.

2. :blue[**128KB**:] The specific size allocated for the blob. In this context, it means each blob has a storage capacity of 128 kilobytes.

3. :blue[**Zero**:] This refers to the portions of the blob that are not being used to store meaningful data and are instead filled with zeros (or are effectively empty).

4. :blue[**Wasted Blob Space Tracker**:] This is a tool or metric that measures the amount of the 128KB storage space that is not being utilized effectively and is instead filled with zeros. It helps in identifying inefficiencies in storage utilization.

In summary, the "Wasted blob space tracker" is a tool or metric designed to determine how much of the allocated 128KB storage space in a blob is actually wasted or unused, filled with zeros instead of meaningful data. This can be useful for optimizing storage efficiency and identifying areas where storage capacity might be better utilized.
                """)

def page1():
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

def page2():
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
    
    possible_bids = ["2578", "277119", "314157", "12089", "223201"]  # Add more possible bid values as needed
    
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

def page3():
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

# Sidebar for navigation
st.sidebar.image("https://pbs.twimg.com/media/GIUYdIqaMAAY7_B.jpg")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Introduction", "I have Blob Data", "I have Blob Hash", "I have Tx Hash"])

# Show the selected page
if page == "Introduction":
    introduction()
elif page == "I have Blob Data":
    page1()
elif page == "I have Blob Hash":
    page2()
elif page == "I have Tx Hash":
    page3()
