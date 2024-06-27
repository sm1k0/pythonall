from web3 import Web3
from web3.middleware import geth_poa_middleware
from contract_info import abi, contract_address

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0) 

contract = w3.eth.contract(address=contract_address, abi=abi)   

print(contract.address)
print(f"Баланс смарт-контракта: {w3.eth.get_balance(contract_address)}")
print(f"Баланс аккаунат 1: {w3.eth.get_balance('0x6Cd04203d18f80a4a641a2E6B5e20220Dcd27299')}")
print(f"Баланс аккаунат 2: {w3.eth.get_balance('0x2a7191D380C7F60Ba26BFf05995A61563F1F4E43')}")
print(f"Баланс аккаунат 3: {w3.eth.get_balance('0x14227DD8ffCb26ce7A3b44C8DFAbE68e3b54047C')}")
print(f"Баланс аккаунат 4: {w3.eth.get_balance('0xC529153413Bc4f068C6F7839554dC3e9C5821145')}")
print(f"Баланс аккаунат 5: {w3.eth.get_balance('0x9b528ca6D9461b7e3feDeFbAFF39Af162b776A25')}")