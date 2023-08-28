import requests 
import math
import time
import re
import os
from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_account.signers.local import LocalAccount
from datetime import datetime
import concurrent.futures
import asyncio


ABI = '''[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"trader","type":"address"},{"indexed":false,"internalType":"address","name":"subject","type":"address"},{"indexed":false,"internalType":"bool","name":"isBuy","type":"bool"},{"indexed":false,"internalType":"uint256","name":"shareAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"ethAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"protocolEthAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"subjectEthAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"supply","type":"uint256"}],"name":"Trade","type":"event"},{"inputs":[{"internalType":"address","name":"sharesSubject","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"buyShares","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"sharesSubject","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"getBuyPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"sharesSubject","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"getBuyPriceAfterFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"supply","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"getPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"sharesSubject","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"getSellPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"sharesSubject","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"getSellPriceAfterFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"protocolFeeDestination","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"protocolFeePercent","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sharesSubject","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"sellShares","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"_feeDestination","type":"address"}],"name":"setFeeDestination","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_feePercent","type":"uint256"}],"name":"setProtocolFeePercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_feePercent","type":"uint256"}],"name":"setSubjectFeePercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"sharesBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"sharesSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"subjectFeePercent","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]'''

class FTSniper:
    def __init__(self):
        self.held_shares = []
        self.seen_accounts = []
        self.num_of_shares = 1
        self.min_followers = 5000  #10000 1500 - min amount of followers for us to be interested in

        self.latest_block_number = 0
        self.base_fee = 0

        self.maxFeePerGas = 10
        self.maxPriorityFeePerGas = 10

        self.cost_multi = 1

        self.w3_base = Web3(Web3.WebsocketProvider('ws://10.0.0.227:8548')) # https://mainnet.base.org
        self.ft = self.w3_base.to_checksum_address("0xcf205808ed36593aa40a44f10c7f7c2f67d4a4d4")
        self.ft_contract = self.w3_base.eth.contract(address=self.ft, abi=ABI)

        self.p_key = os.getenv("PKEY")
        if not self.p_key:
            print("PKEY not found in environment variables")
            os._exit(1)
        self.ETH_ACCOUNT: LocalAccount = Account.from_key(self.p_key)
        return

    # unauthed twitter followers
    def twitter(self, username: str):

        headers = { 
            "accept-language": "en-US,en;q=0.5",
            "connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/111.0"
        }

        def get_twitter_authorization():
            sw = requests.get("https://twitter.com/sw.js").text
            url = re.search("https://abs.twimg.com/responsive-web/client-serviceworker/serviceworker.(\d|([a-zA-Z]))+.js", sw).group()

            target = requests.get(url).text
            authorization = re.search(r'(Bearer.*?)(\)|$)', target).group().replace("Bearer \".concat(\"", "").replace("\")", "")
            return f'Bearer {authorization}'

        headers["authorization"] = get_twitter_authorization()

        def get_twitter_guest_token():
            result = requests.post("https://api.twitter.com/1.1/guest/activate.json", headers=headers)
            guest_token = result.json()['guest_token']
            return guest_token

        headers["x-guest-token"] = get_twitter_guest_token()

        try:
            r = requests.get(f"https://twitter.com/i/api/graphql/k26ASEiniqy4eXMdknTSoQ/UserByScreenName?variables=%7B%22screen_name%22%3A%22{username}%22%2C%22withSafetyModeUserFields%22%3Atrue%7D&features=%7B%22blue_business_profile_image_shape_enabled%22%3Afalse%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%7D", headers=headers)
            json = r.json()["data"]
        except:
            print("Error getting twitter data")

        if not bool(json):
            print("User not found")
            return None

        followers = json["user"]["result"]["legacy"]["followers_count"]
        return {"username": username, "followers": f'{followers:,}'}

    # get user data from kosetto api
    def get_user_data(self, address):
        try:
            base_url = "https://prod-api.kosetto.com/users/"
            # timeout set to 1s so we arent held up on some bs
            response = requests.get(base_url + address, timeout=1)
        except:
            print("Error getting user data")
            return None

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
            return None

    # get the amount of shares held for our account for a given address
    def get_shares(self, addr):
        check_addr = self.w3_base.to_checksum_address(addr)
        balance = self.ft_contract.functions.sharesBalance(check_addr, self.ETH_ACCOUNT.address).call()
        return balance

    def handle_event(self, event):
        if event.args['trader'] == event.args['subject'] and event.args['shareAmount'] > 0 and event.args['ethAmount'] == 0:
            if event.args['subject'] in self.seen_accounts:
                return
            else:
                self.seen_accounts.append(event.args['subject'])
                print("found new user account: ", event.args['subject'])
                self.check_and_buy(event.args['subject'])

    async def log_loop(self, event_filter):
        while True:
            for event in event_filter.get_new_entries():
                self.check_profit()
                self.handle_event(event)
            #await asyncio.sleep(poll_interval)

    def get_transactions(self):
        
        event_filter = self.ft_contract.events.Trade.create_filter(fromBlock='latest')
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                asyncio.gather(
                    self.log_loop(event_filter)))
        finally:
            loop.close()

    def check_and_buy(self, user_addr):
        print("checking ..")
        
        user_checkaddr = self.w3_base.to_checksum_address(user_addr)            
        user_data = self.get_user_data(user_checkaddr)
        # hitting this shit too hard, lets do a shitty loop to retry 5x sleeping 1s in between
        if not user_data:
            print(f"no user_data returned for {user_checkaddr}\n")
            print("retrying... 1s 5x\n")
            for i in range(0, 5):
                print(f"retrying... {i}s\n")
                time.sleep(1)
                user_data = self.get_user_data(user_checkaddr)
                print(f"user_data returned for {user_checkaddr}\n")
                print(user_data)
                if user_data:
                    break
            
        if user_data:
            followers = self.twitter(user_data['twitterUsername'])
            if not followers:
                print("error getting followers")
                return

            followers_int = int(followers['followers'].replace(",", ""))

            # adjust max amount + gas fees we are willing to pay 
            # fuqu 0xbb3b/ThePepeology
            # dis is shit and the values are whack because testing on main D:
            tiers = [
                {'limit': 1_000_000, 'shares': 5, 'fee': 200, 'priorityFee': 200, 'cost_multi': 1.10 },
                {'limit': 500_000, 'shares': 5, 'fee': 200, 'priorityFee': 200, 'cost_multi': 1.10 },
                {'limit': 250_000, 'shares': 5, 'fee': 110, 'priorityFee': 110, 'cost_multi': 1.10 },
                {'limit': 100_000, 'shares': 5, 'fee': 110, 'priorityFee': 110, 'cost_multi': 1.10 },
                {'limit': 20_000, 'shares': 5, 'fee': 110, 'priorityFee': 110, 'cost_multi': 1.05},
                {'limit': 10_000, 'shares': 5, 'fee': 110, 'priorityFee': 110, 'cost_multi': 1.05},
                {'limit': 5_000, 'shares': 5, 'fee': 90, 'priorityFee': 90, 'cost_multi': 1.02},
                {'limit': 2_500, 'shares': 2, 'fee': 50, 'priorityFee': 50, 'cost_multi': 1},
                {'limit': 1_500, 'shares': 2, 'fee': 50, 'priorityFee': 50, 'cost_multi': 1},
            ]

            for tier in tiers:
                if followers_int > tier['limit']:
                    self.num_of_shares = tier['shares']
                    self.maxFeePerGas = tier['fee']
                    self.maxPriorityFeePerGas = tier['priorityFee']
                    self.cost_multi = tier['cost_multi']
                    break


            print(f"twitterFollowers:\t{followers_int}\n")
            print(f"twitterUser:\t{user_data['twitterUsername']}\n")
            print(f"twitterName:\t{user_data['twitterName']}\n")
            print(f"holderCount:\t{user_data['holderCount']}\n")
            print(f"holdingCount:\t{user_data['holdingCount']}\n")
            print(f"shareSupply:\t{user_data['shareSupply']}\n")

            if followers_int >= self.min_followers:
                self.buy_shares(user_checkaddr)
            #self.buy_shares(user_checkaddr)
            return       

    def buy_shares(self, user_addr):

        block_details = self.w3_base.eth.get_block("latest", full_transactions=True) # "latest"
        base_fee = block_details['baseFeePerGas']

        #if user_addr in self.held_shares:
        if any(d['account'] == user_addr for d in self.held_shares):
            print(f"already bought shares of {user_addr}\n")
            return

        print(f"buying {self.num_of_shares} shares of {user_addr} at block: {block_details['number']}\n")
        cost_estimate = self.ft_contract.functions.getBuyPriceAfterFee(user_addr, self.num_of_shares).call()
        print(f"cost estimate: {cost_estimate} for address {user_addr}\n")

        try:
            tx = self.ft_contract.functions.buyShares(user_addr, self.num_of_shares).build_transaction({
                'from': self.ETH_ACCOUNT.address,
                'chainId': 8453,
                'nonce': self.w3_base.eth.get_transaction_count(self.ETH_ACCOUNT.address),
                'value': math.ceil(cost_estimate * self.cost_multi) # even if we dont get the second TX in the block .. 
            })
        except:
            print("failed to build transaction")
            return

        gas_estimate = self.w3_base.eth.estimate_gas(tx)

        tx = self.ft_contract.functions.buyShares(user_addr, self.num_of_shares).build_transaction({
            'chainId': 8453,
            'gas': gas_estimate,
            # if you need to be competitive for the first buy of the same subjects shares in a block adjust fees accordingly
            'maxFeePerGas': self.w3_base.to_wei(self.maxFeePerGas, 'gwei'), # 10
            'maxPriorityFeePerGas': self.w3_base.to_wei(self.maxPriorityFeePerGas, 'gwei'), # 10
            'nonce': self.w3_base.eth.get_transaction_count(self.ETH_ACCOUNT.address),
            'value': math.ceil(cost_estimate * self.cost_multi) # max value in wei for purchase of shares: 0.00225
        })

        signed_tx = self.w3_base.eth.account.sign_transaction(tx, private_key=self.p_key)

        #tx_hash = self.send_request(signed_tx.rawTransaction) # generally lands 4 blocks from sending (2s each?).. 
        tx_hash = self.w3_base.eth.send_raw_transaction(signed_tx.rawTransaction)
            
        # wait for tx to be mined and check if it was successful
        tx_receipt = self.w3_base.eth.wait_for_transaction_receipt(tx_hash)
            
        if tx_receipt['status'] == 1:
            print(f"tx landed: {tx_hash.hex()} blockNumber: {tx_receipt['blockNumber']} \n")
            total_cost = (cost_estimate * self.num_of_shares) + (gas_estimate * self.base_fee + self.w3_base.to_wei('1', 'gwei'))
            
            print(f"total cost: {total_cost}\n")
            buy_info = {'account': user_addr, 'cost': total_cost, 'time': datetime.now(), 'block': block_details['number']}
            self.held_shares.append(buy_info)
        else:
            print(f"tx failed: {tx_hash.hex()}\n")
            #os._exit(1) 
            #time.sleep(1)
        return

    def get_sale_price(self, user_addr):
        price = self.ft_contract.functions.getSellPriceAfterFee(user_addr, self.num_of_shares).call()
        return price

    def get_buy_price(self, user_addr):
        price = self.ft_contract.functions.getBuyPriceAfterFee(user_addr, self.num_of_shares).call()
        return price

    # a function that monitors the getBlock() like above but every time a sell transaction is called mark it
    def sell_shares(self, user_addr):
        print(f"selling shares of {user_addr}\n")
        # check that the user has shares to sell
        balance = self.get_shares(user_addr)
        if balance == 0:
            print(f"no shares to sell for {user_addr}\n")
            return
        
        #cost_estimate = self.ft_contract.functions.getBuyPriceAfterFee(user_addr, self.num_of_shares).call()
        #print(f"cost estimate: {cost_estimate} for address {user_addr}\n")
        try:
            tx = self.ft_contract.functions.sellShares(user_addr, self.num_of_shares).build_transaction({
                'from': self.ETH_ACCOUNT.address,
                'chainId': 8453,
                'nonce': self.w3_base.eth.get_transaction_count(self.ETH_ACCOUNT.address),
            })
        except:
            print("failed to build transaction - no shares?")
            return

        gas_estimate = self.w3_base.eth.estimate_gas(tx)
        block_details = self.w3_base.eth.get_block("latest", full_transactions=True) # "latest"
        base_fee = block_details['baseFeePerGas']
        
        tx = self.ft_contract.functions.sellShares(user_addr, self.num_of_shares).build_transaction({
            'chainId': 8453,
            'gas': gas_estimate,
            'maxFeePerGas': self.w3_base.to_wei('1', 'gwei'), # 1
            'maxPriorityFeePerGas': base_fee ,
            'nonce': self.w3_base.eth.get_transaction_count(self.ETH_ACCOUNT.address),
        })

        signed_tx = self.w3_base.eth.account.sign_transaction(tx, private_key=self.p_key)
        tx_hash = self.w3_base.eth.send_raw_transaction(signed_tx.rawTransaction)
            
        # wait for tx to be mined and check if it was successful
        tx_receipt = self.w3_base.eth.wait_for_transaction_receipt(tx_hash)
            
        if tx_receipt['status'] == 1:
            try:
                self.held_shares.remove(user_addr)
            except:
                print("failed to remove address from held_shares")
            # remove the address from the self.held_shares
        return

    # pretty lame way to do this but it works
    def check_profit(self):
        # iterate the held_shares and check the price of each compared to the purchase cost
        
        for share in self.held_shares:
            print("checking profit for: ", share['account'])
            value = self.get_sale_price(share['account'])
            cost = share['cost']
            profit = value - cost
            # check that profit is double the cost
            if math.ceil(profit) >= (math.ceil(cost * 2)):
                print(f"selling profit of {profit} found for {share['account']}\n")
                # sell the share
                self.sell_shares(share['account'])
        
        #for share in self.held_shares:
        #    # check if its been at least 25 blocks since purchase
        #    if (self.latest_block_number - share['block']) > 25:
        #        print(f"selling shares of {share['account']} after 25 blocks\n")
        #        self.sell_shares(share['account'])
                

if __name__ == '__main__':
        x = FTSniper()
        x.get_transactions()
