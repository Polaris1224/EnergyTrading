// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title SolarCoin
 * @dev ERC-20 token for P2P energy trading
 * 1 SolarCoin = 1 kWh of energy
 */
contract SolarCoin {
    string public name = "SolarCoin";
    string public symbol = "SLC";
    uint8 public decimals = 18;
    uint256 public totalSupply;
    
    address public owner;
    
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event TokensMinted(address indexed to, uint256 amount);
    event TokensBurned(address indexed from, uint256 amount);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this");
        _;
    }
    
    constructor(uint256 initialSupply) {
        owner = msg.sender;
        totalSupply = initialSupply * 10**decimals;
        balanceOf[msg.sender] = totalSupply;
        emit Transfer(address(0), msg.sender, totalSupply);
        emit TokensMinted(msg.sender, totalSupply);
    }
    
    function transfer(address to, uint256 value) public returns (bool) {
        require(to != address(0), "Invalid address");
        require(balanceOf[msg.sender] >= value, "Insufficient balance");
        
        balanceOf[msg.sender] -= value;
        balanceOf[to] += value;
        
        emit Transfer(msg.sender, to, value);
        return true;
    }
    
    function approve(address spender, uint256 value) public returns (bool) {
        require(spender != address(0), "Invalid spender address");
        
        allowance[msg.sender][spender] = value;
        emit Approval(msg.sender, spender, value);
        return true;
    }
    
    function transferFrom(address from, address to, uint256 value) public returns (bool) {
        require(from != address(0), "Invalid from address");
        require(to != address(0), "Invalid to address");
        require(balanceOf[from] >= value, "Insufficient balance");
        require(allowance[from][msg.sender] >= value, "Insufficient allowance");
        
        balanceOf[from] -= value;
        balanceOf[to] += value;
        allowance[from][msg.sender] -= value;
        
        emit Transfer(from, to, value);
        return true;
    }
    
    function mint(address to, uint256 amount) public onlyOwner {
        require(to != address(0), "Invalid address");
        
        totalSupply += amount;
        balanceOf[to] += amount;
        
        emit Transfer(address(0), to, amount);
        emit TokensMinted(to, amount);
    }
    
    function burn(uint256 amount) public {
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");
        
        balanceOf[msg.sender] -= amount;
        totalSupply -= amount;
        
        emit Transfer(msg.sender, address(0), amount);
        emit TokensBurned(msg.sender, amount);
    }
    
    function getBalance(address account) public view returns (uint256) {
        return balanceOf[account];
    }
}