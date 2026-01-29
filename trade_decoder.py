import os
import json
from dataclasses import dataclass, asdict
from decimal import Decimal
from web3 import Web3
from dotenv import load_dotenv

# 加载环境变量（读.env文件）
load_dotenv()
RPC_URL = os.getenv("RPC_URL")
if not RPC_URL:
    raise ValueError("已自动配置RPC，无需修改.env")

# 连接Polygon网络（容错处理）
try:
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    assert w3.is_connected(), "网络连接失败"
except Exception as e:
    raise ConnectionError(f"Polygon网络连不上：{e}，RPC地址无误")

# Polymarket合约地址（固定）
EXCHANGE_ADDRESSES = {
    "CTF_Exchange": "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E",
    "NegRisk_CTFExchange": "0xC5d563A36AE78145C45a50134d48A1215220f80a"
}

# OrderFilled事件ABI+Topic（固定）
ORDER_FILLED_ABI = {
    "anonymous": False,
    "inputs": [
        {"indexed":True,"name":"orderHash","type":"bytes32"},
        {"indexed":True,"name":"maker","type":"address"},
        {"indexed":True,"name":"taker","type":"address"},
        {"indexed":False,"name":"makerAssetId","type":"uint256"},
        {"indexed":False,"name":"takerAssetId","type":"uint256"},
        {"indexed":False,"name":"makerAmountFilled","type":"uint256"},
        {"indexed":False,"name":"takerAmountFilled","type":"uint256"},
        {"indexed":False,"name":"fee","type":"uint256"}
    ],
    "name":"OrderFilled","type":"event"
}
ORDER_FILLED_TOPIC = w3.keccak(text="OrderFilled(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)").hex()

# 交易数据结构
@dataclass(frozen=True)
class Trade:
    tx_hash: str;log_index: int;exchange: str;maker: str;taker: str
    maker_asset_id: str;taker_asset_id: str;maker_amount: str;taker_amount: str
    fee: str;price: str;token_id: str;side: str

def decode_trade(tx_hash: str) -> list[dict]:
    # 获取交易回执
    try:receipt = w3.eth.get_transaction_receipt(tx_hash)
    except Exception as e:raise RuntimeError(f"拿不到交易回执：{e}，哈希是否正确")

    trades = []
    for log in receipt["logs"]:
        # 过滤非目标合约+非目标事件
        if log["address"].lower() not in [a.lower() for a in EXCHANGE_ADDRESSES.values()] or ORDER_FILLED_TOPIC not in log["topics"]:
            continue
        # 解析日志
        try:decoded = w3.eth.contract(abi=[ORDER_FILLED_ABI]).events.OrderFilled().process_log(log)
        except:continue

        # 提取核心数据（简化版，容错）
        mk,tk = decoded["args"]["maker"].lower(), decoded["args"]["taker"].lower()
        mk_asset,tk_asset = str(decoded["args"]["makerAssetId"]), str(decoded["args"]["takerAssetId"])
        mk_amt,tk_amt = str(decoded["args"]["makerAmountFilled"]), str(decoded["args"]["takerAmountFilled"])
        fee,log_idx,ex = str(decoded["args"]["fee"]), log["logIndex"], log["address"].lower()
        
        if tk == ex:continue # 过滤系统交易
        # 计算价格+买卖方向（容错除零）
        try:
            if mk_asset == "0":
                price = round(Decimal(mk_amt)/Decimal(tk_amt),6);side="BUY";token_id=tk_asset
            else:
                price = round(Decimal(tk_amt)/Decimal(mk_amt),6);side="SELL";token_id=mk_asset
        except:continue

        # 组装结果
        trades.append(asdict(Trade(
            tx_hash=tx_hash.lower(),log_index=log_idx,exchange=ex,maker=mk,taker=tk,
            maker_asset_id=mk_asset,taker_asset_id=tk_asset,maker_amount=mk_amt,taker_amount=tk_amt,
            fee=fee,price=str(price),token_id=token_id,side=side
        )))
    return trades

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Polymarket交易解析")
    parser.add_argument("--tx-hash", required=True, help="Polygon交易哈希（0x开头66位）")
    args = parser.parse_args()

    # 校验哈希格式
    if not (args.tx_hash.startswith("0x") and len(args.tx_hash)==66):
        raise ValueError("哈希格式错！必须0x开头，一共66个字符")
    
    # 执行解析+打印
    print(f"正在解析：{args.tx_hash}\n解析结果：")
    print(json.dumps(decode_trade(args.tx_hash), indent=2, ensure_ascii=False))
