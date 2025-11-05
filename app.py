import streamlit as st
from web3 import Web3
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="P2P Energy Trading",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================

# Ganache connection
GANACHE_URL = "http://127.0.0.1:7545"

# Contract addresses (PASTE YOUR DEPLOYED CONTRACT ADDRESSES HERE)
SOLARCOIN_ADDRESS = "0xCAf5D180DFfEbdD539471e6F02dAf61a75f8a413"  # ← UPDATE THIS
ENERGYTRADE_ADDRESS = "0xAA20f626477B9F4ea143984f06E98A9C411e0E86"  # ← UPDATE THIS

# Account addresses (from MetaMask/Ganache)
ACCOUNTS = {
    "Owner": "0xCe7bFa42B6195eEFA23Bb9a55213A57c63C9b294",  # ← UPDATE THIS
    "Seller": "0x7f300455aEA6ca63EC271C2815d71DF9dFb50d9d",  # ← UPDATE THIS
    "Buyer": "0xc45029184909E0cf1bdE4d29403e271b388b6422"  # ← UPDATE THIS
}

# Private keys (from Ganache - for signing transactions)
PRIVATE_KEYS = {
    "Owner": "0xa6197cd505cb4e3b5a780a92597b0ab294adaf2a8a2b0dd54cdc3941c8cc600b",  # ← UPDATE THIS
    "Seller": "0xe610b1d0e842863c46ba991f7fa34622c784688ff70720fb759672dd418b0011",  # ← UPDATE THIS
    "Buyer": "0x353c1894cf5e0d96f4ebc52be6b73ccab0e79be1645991b3a18897dc1db0b129"  # ← UPDATE THIS
}

# Contract ABIs
SOLARCOIN_ABI = [
    {"inputs": [{"internalType": "address", "name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "to", "type": "address"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "name": "transfer", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "name": "approve", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [], "name": "name", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "symbol", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "totalSupply", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}
]

ENERGYTRADE_ABI = [
    {"inputs": [{"internalType": "uint256", "name": "energyAmount", "type": "uint256"}, {"internalType": "uint256", "name": "pricePerUnit", "type": "uint256"}], "name": "listEnergy", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "uint256", "name": "tradeId", "type": "uint256"}], "name": "buyEnergy", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "uint256", "name": "tradeId", "type": "uint256"}], "name": "cancelTrade", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "uint256", "name": "tradeId", "type": "uint256"}], "name": "getTrade", "outputs": [{"internalType": "address", "name": "seller", "type": "address"}, {"internalType": "address", "name": "buyer", "type": "address"}, {"internalType": "uint256", "name": "energyAmount", "type": "uint256"}, {"internalType": "uint256", "name": "pricePerUnit", "type": "uint256"}, {"internalType": "uint256", "name": "totalPrice", "type": "uint256"}, {"internalType": "enum EnergyTrade.TradeStatus", "name": "status", "type": "uint8"}, {"internalType": "uint256", "name": "timestamp", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "getActiveTrades", "outputs": [{"internalType": "uint256[]", "name": "", "type": "uint256[]"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "getTotalTrades", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}
]

# ============================================
# WEB3 CONNECTION
# ============================================

@st.cache_resource
def get_web3_connection():
    w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    if w3.is_connected():
        return w3
    else:
        st.error("❌ Cannot connect to Ganache. Make sure it's running!")
        return None

w3 = get_web3_connection()

if w3:
    solarcoin_contract = w3.eth.contract(
        address=Web3.to_checksum_address(SOLARCOIN_ADDRESS),
        abi=SOLARCOIN_ABI
    )
    energytrade_contract = w3.eth.contract(
        address=Web3.to_checksum_address(ENERGYTRADE_ADDRESS),
        abi=ENERGYTRADE_ABI
    )

# ============================================
# HELPER FUNCTIONS
# ============================================

def wei_to_slc(wei_value):
    """Convert wei to SolarCoin"""
    return w3.from_wei(wei_value, 'ether')

def slc_to_wei(slc_value):
    """Convert SolarCoin to wei"""
    return w3.to_wei(slc_value, 'ether')

def get_balance(address):
    """Get SolarCoin balance"""
    balance_wei = solarcoin_contract.functions.balanceOf(
        Web3.to_checksum_address(address)
    ).call()
    return float(wei_to_slc(balance_wei))

def get_trade_status(status_code):
    """Convert status code to readable text"""
    statuses = {0: "🟢 Active", 1: "✅ Completed", 2: "❌ Cancelled"}
    return statuses.get(status_code, "Unknown")

def send_transaction(account_name, transaction):
    """Send a transaction from specified account"""
    try:
        private_key = PRIVATE_KEYS[account_name]
        account_address = Web3.to_checksum_address(ACCOUNTS[account_name])
        
        # Build transaction
        tx = transaction.build_transaction({
            'from': account_address,
            'nonce': w3.eth.get_transaction_count(account_address),
            'gas': 3000000,
            'gasPrice': w3.eth.gas_price
        })
        
        # Sign transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return receipt
    except Exception as e:
        st.error(f"Transaction failed: {str(e)}")
        return None

# ============================================
# MAIN APP
# ============================================

st.markdown('<h1 class="main-header">⚡ P2P Energy Trading Platform</h1>', unsafe_allow_html=True)

if not w3:
    st.stop()

# Sidebar - Account Selection
st.sidebar.title("🔐 Account Selection")
selected_account = st.sidebar.selectbox(
    "Select Account",
    list(ACCOUNTS.keys())
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Current Account:** {selected_account}")
st.sidebar.markdown(f"**Address:** `{ACCOUNTS[selected_account][:10]}...`")

# Display balances
st.sidebar.markdown("---")
st.sidebar.subheader("💰 Account Balances")
for name, address in ACCOUNTS.items():
    balance = get_balance(address)
    st.sidebar.metric(f"{name}", f"{balance:.2f} SLC")

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📝 List Energy", "🛒 Marketplace", "📈 My Trades"])

# ============================================
# TAB 1: DASHBOARD
# ============================================
with tab1:
    st.header("📊 Platform Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_trades = energytrade_contract.functions.getTotalTrades().call()
        st.metric("Total Trades", total_trades)
    
    with col2:
        active_trades = energytrade_contract.functions.getActiveTrades().call()
        st.metric("Active Listings", len(active_trades))
    
    with col3:
        total_supply_wei = solarcoin_contract.functions.totalSupply().call()
        total_supply = float(wei_to_slc(total_supply_wei))
        st.metric("Total SolarCoin Supply", f"{total_supply:,.0f} SLC")
    
    st.markdown("---")
    
    # Recent trades
    st.subheader("📜 Recent Trades")
    
    if total_trades > 0:
        trades_data = []
        for i in range(max(1, total_trades - 4), total_trades + 1):
            try:
                trade = energytrade_contract.functions.getTrade(i).call()
                trades_data.append({
                    "Trade ID": i,
                    "Seller": trade[0][:10] + "...",
                    "Energy (kWh)": trade[2],
                    "Price/kWh": float(wei_to_slc(trade[3])),
                    "Total Price": float(wei_to_slc(trade[4])),
                    "Status": get_trade_status(trade[5])
                })
            except:
                pass
        
        if trades_data:
            st.table(trades_data)
        else:
            st.info("No trades yet")
    else:
        st.info("No trades yet. Be the first to list energy!")

# ============================================
# TAB 2: LIST ENERGY
# ============================================
with tab2:
    st.header("📝 List Your Energy for Sale")
    
    if selected_account == "Buyer":
        st.warning("⚠️ Switch to Seller account to list energy")
    else:
        with st.form("list_energy_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                energy_amount = st.number_input(
                    "Energy Amount (kWh)",
                    min_value=1,
                    max_value=1000,
                    value=100,
                    help="Amount of energy to sell"
                )
            
            with col2:
                price_per_unit = st.number_input(
                    "Price per kWh (SLC)",
                    min_value=0.1,
                    max_value=100.0,
                    value=10.0,
                    step=0.1,
                    help="Price in SolarCoins"
                )
            
            total_price = energy_amount * price_per_unit
            st.info(f"💰 **Total Price:** {total_price:.2f} SLC")
            
            submit_button = st.form_submit_button("📤 List Energy", use_container_width=True)
            
            if submit_button:
                with st.spinner("Listing energy..."):
                    try:
                        # Prepare transaction
                        tx = energytrade_contract.functions.listEnergy(
                            energy_amount,
                            slc_to_wei(price_per_unit)
                        )
                        
                        # Send transaction
                        receipt = send_transaction(selected_account, tx)
                        
                        if receipt and receipt['status'] == 1:
                            st.success("✅ Energy listed successfully!")
                            st.balloons()
                        else:
                            st.error("❌ Transaction failed")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# ============================================
# TAB 3: MARKETPLACE
# ============================================
with tab3:
    st.header("🛒 Energy Marketplace")
    
    active_trades = energytrade_contract.functions.getActiveTrades().call()
    
    if len(active_trades) == 0:
        st.info("No active listings. Check back later!")
    else:
        for trade_id in active_trades:
            try:
                trade = energytrade_contract.functions.getTrade(trade_id).call()
                seller, buyer, energy, price_wei, total_wei, status, timestamp = trade
                
                if status == 0:  # Active
                    with st.container():
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        
                        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                        
                        with col1:
                            st.markdown(f"**Trade #{trade_id}**")
                            st.text(f"Seller: {seller[:10]}...")
                        
                        with col2:
                            st.metric("Energy", f"{energy} kWh")
                        
                        with col3:
                            price_slc = float(wei_to_slc(price_wei))
                            total_slc = float(wei_to_slc(total_wei))
                            st.metric("Price/kWh", f"{price_slc:.2f} SLC")
                            st.text(f"Total: {total_slc:.2f} SLC")
                        
                        with col4:
                            if selected_account == "Buyer":
                                if st.button(f"💳 Buy", key=f"buy_{trade_id}"):
                                    with st.spinner("Processing purchase..."):
                                        try:
                                            # First approve
                                            approve_tx = solarcoin_contract.functions.approve(
                                                Web3.to_checksum_address(ENERGYTRADE_ADDRESS),
                                                total_wei
                                            )
                                            approve_receipt = send_transaction(selected_account, approve_tx)
                                            
                                            if approve_receipt and approve_receipt['status'] == 1:
                                                # Then buy
                                                buy_tx = energytrade_contract.functions.buyEnergy(trade_id)
                                                buy_receipt = send_transaction(selected_account, buy_tx)
                                                
                                                if buy_receipt and buy_receipt['status'] == 1:
                                                    st.success("✅ Purchase successful!")
                                                    st.balloons()
                                                    st.rerun()
                                        except Exception as e:
                                            st.error(f"Error: {str(e)}")
                            else:
                                st.info("Switch to Buyer")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown("---")
            except:
                pass

# ============================================
# TAB 4: MY TRADES
# ============================================
with tab4:
    st.header("📈 My Trade History")
    
    total_trades = energytrade_contract.functions.getTotalTrades().call()
    my_trades = []
    
    for i in range(1, total_trades + 1):
        try:
            trade = energytrade_contract.functions.getTrade(i).call()
            seller, buyer, energy, price_wei, total_wei, status, timestamp = trade
            
            current_address = Web3.to_checksum_address(ACCOUNTS[selected_account])
            
            if seller == current_address or buyer == current_address:
                role = "Seller" if seller == current_address else "Buyer"
                my_trades.append({
                    "Trade ID": i,
                    "Role": role,
                    "Energy (kWh)": energy,
                    "Price/kWh (SLC)": float(wei_to_slc(price_wei)),
                    "Total (SLC)": float(wei_to_slc(total_wei)),
                    "Status": get_trade_status(status),
                    "Date": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
                })
        except:
            pass
    
    if my_trades:
        st.dataframe(my_trades, use_container_width=True)
    else:
        st.info("No trades yet. Start by listing or buying energy!")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    ⚡ P2P Energy Trading Platform | Powered by Blockchain & Quantum ML
    </div>
    """,
    unsafe_allow_html=True
)