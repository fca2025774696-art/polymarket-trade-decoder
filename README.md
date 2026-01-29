Polymarket交易解析工具
 
一款用于解析Polygon链上Polymarket平台OrderFilled订单填充事件的Python工具，精准提取交易核心数据。
 
 
 
📌 核心功能
 
1. 监听Polymarket指定交易所合约，捕获OrderFilled核心成交事件

2. 解析Polygon链交易哈希，提取订单关键信息（成交相关核心数据）

3. 过滤无效日志（如USDC转账、授权日志），仅输出有效成交数据
 
 
 
🛠 运行环境 & 依赖
 
- 运行环境：Python 3.8+

- 核心依赖：web3，安装命令
 pip install web3
 
 
 
🚀 快速使用步骤
 
1. 本地安装Python 3.8+及对应依赖

2. 项目根目录创建 .env 文件，添加Polygon RPC节点（示例）
 RPC_URL=https://polygon-rpc.com

3. 终端执行解析命令（替换为有效Polymarket交易哈希）
 python src/trade_decoder.py --tx-hash 你的有效交易哈希

4. 终端输出解析后的订单成交数据

 
 
⚠️ 重要注意事项
 
1. 仅支持Polygon主网Polymarket真实成交交易（需触发OrderFilled事件）

2. 无效交易哈希/无对应事件的交易，会返回空数组，属正常过滤结果

3.  .env 文件含RPC配置，已加入.gitignore，禁止上传至GitHub

 
 
 
📁 项目结构
 
 polymarket-trade-decoder/
├── src/                # 核心代码目录
│   └── trade_decoder.py # 主解析脚本
├── .gitignore          # 忽略无用/隐私文件
└── README.md           # 项目说明文档（当前文件）
 
 
 
操作步骤（直接照做）
 
1. 点GitHub仓库里的添加README文件，进入编辑页面

2. 清空默认内容，全选复制上面所有内容粘贴进去

3. 滑到最下方，Commit message默认或填 docs: 完善项目README，补充使用说明 

4. 点Commit changes，README就创建好了
