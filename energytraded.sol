// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20 {
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
    function allowance(address owner, address spender) external view returns (uint256);
}

/**
 * @title EnergyTrade
 * @dev Smart contract for P2P energy trading using SolarCoin
 */
contract EnergyTrade {
    
    IERC20 public solarCoin;
    uint256 public tradeCounter;
    
    enum TradeStatus { Active, Completed, Cancelled }
    
    struct Trade {
        uint256 tradeId;
        address seller;
        address buyer;
        uint256 energyAmount;      // in kWh
        uint256 pricePerUnit;      // SolarCoin per kWh (in wei)
        uint256 totalPrice;        // Total cost in SolarCoin
        TradeStatus status;
        uint256 timestamp;
    }
    
    // Storage
    mapping(uint256 => Trade) public trades;
    mapping(address => uint256[]) public sellerTrades;
    mapping(address => uint256[]) public buyerTrades;
    
    // Events
    event EnergyListed(
        uint256 indexed tradeId,
        address indexed seller,
        uint256 energyAmount,
        uint256 pricePerUnit,
        uint256 totalPrice
    );
    
    event EnergyPurchased(
        uint256 indexed tradeId,
        address indexed buyer,
        address indexed seller,
        uint256 energyAmount,
        uint256 totalPrice
    );
    
    event TradeCancelled(
        uint256 indexed tradeId,
        address indexed seller
    );
    
    constructor(address _solarCoinAddress) {
        require(_solarCoinAddress != address(0), "Invalid token address");
        solarCoin = IERC20(_solarCoinAddress);
        tradeCounter = 0;
    }
    
    /**
     * @dev List energy for sale
     * @param energyAmount Amount of energy in kWh
     * @param pricePerUnit Price per kWh in SolarCoin (wei)
     */
    function listEnergy(uint256 energyAmount, uint256 pricePerUnit) 
        public 
        returns (uint256) 
    {
        require(energyAmount > 0, "Energy amount must be > 0");
        require(pricePerUnit > 0, "Price must be > 0");
        
        tradeCounter++;
        uint256 totalPrice = energyAmount * pricePerUnit;
        
        trades[tradeCounter] = Trade({
            tradeId: tradeCounter,
            seller: msg.sender,
            buyer: address(0),
            energyAmount: energyAmount,
            pricePerUnit: pricePerUnit,
            totalPrice: totalPrice,
            status: TradeStatus.Active,
            timestamp: block.timestamp
        });
        
        sellerTrades[msg.sender].push(tradeCounter);
        
        emit EnergyListed(
            tradeCounter,
            msg.sender,
            energyAmount,
            pricePerUnit,
            totalPrice
        );
        
        return tradeCounter;
    }
    
    /**
     * @dev Purchase listed energy
     * @param tradeId ID of the trade to purchase
     */
    function buyEnergy(uint256 tradeId) public {
        Trade storage trade = trades[tradeId];
        
        require(trade.seller != address(0), "Trade does not exist");
        require(trade.status == TradeStatus.Active, "Trade not active");
        require(msg.sender != trade.seller, "Cannot buy your own energy");
        
        uint256 buyerBalance = solarCoin.balanceOf(msg.sender);
        require(buyerBalance >= trade.totalPrice, "Insufficient SolarCoin balance");
        
        uint256 allowanceAmount = solarCoin.allowance(msg.sender, address(this));
        require(allowanceAmount >= trade.totalPrice, "Insufficient allowance");
        
        // Transfer tokens
        bool success = solarCoin.transferFrom(
            msg.sender,
            trade.seller,
            trade.totalPrice
        );
        require(success, "Token transfer failed");
        
        // Update trade
        trade.buyer = msg.sender;
        trade.status = TradeStatus.Completed;
        
        buyerTrades[msg.sender].push(tradeId);
        
        emit EnergyPurchased(
            tradeId,
            msg.sender,
            trade.seller,
            trade.energyAmount,
            trade.totalPrice
        );
    }
    
    /**
     * @dev Cancel a listed trade (seller only)
     * @param tradeId ID of the trade to cancel
     */
    function cancelTrade(uint256 tradeId) public {
        Trade storage trade = trades[tradeId];
        
        require(trade.seller == msg.sender, "Only seller can cancel");
        require(trade.status == TradeStatus.Active, "Trade not active");
        
        trade.status = TradeStatus.Cancelled;
        
        emit TradeCancelled(tradeId, msg.sender);
    }
    
    /**
     * @dev Get trade details
     */
    function getTrade(uint256 tradeId) 
        public 
        view 
        returns (
            address seller,
            address buyer,
            uint256 energyAmount,
            uint256 pricePerUnit,
            uint256 totalPrice,
            TradeStatus status,
            uint256 timestamp
        ) 
    {
        Trade memory trade = trades[tradeId];
        return (
            trade.seller,
            trade.buyer,
            trade.energyAmount,
            trade.pricePerUnit,
            trade.totalPrice,
            trade.status,
            trade.timestamp
        );
    }
    
    /**
     * @dev Get all active trades
     */
    function getActiveTrades() public view returns (uint256[] memory) {
        uint256 activeCount = 0;
        
        for (uint256 i = 1; i <= tradeCounter; i++) {
            if (trades[i].status == TradeStatus.Active) {
                activeCount++;
            }
        }
        
        uint256[] memory activeTrades = new uint256[](activeCount);
        uint256 index = 0;
        
        for (uint256 i = 1; i <= tradeCounter; i++) {
            if (trades[i].status == TradeStatus.Active) {
                activeTrades[index] = i;
                index++;
            }
        }
        
        return activeTrades;
    }
    
    /**
     * @dev Get trades by seller
     */
    function getTradesBySeller(address seller) 
        public 
        view 
        returns (uint256[] memory) 
    {
        return sellerTrades[seller];
    }
    
    /**
     * @dev Get trades by buyer
     */
    function getTradesByBuyer(address buyer) 
        public 
        view 
        returns (uint256[] memory) 
    {
        return buyerTrades[buyer];
    }
    
    /**
     * @dev Get total number of trades
     */
    function getTotalTrades() public view returns (uint256) {
        return tradeCounter;
    }
    
    /**
     * @dev Get SolarCoin contract address
     */
    function getSolarCoinAddress() public view returns (address) {
        return address(solarCoin);
    }
}