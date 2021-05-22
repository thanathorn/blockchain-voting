# Threads:
# 1. Question server thread (Port 30000)
# 2. Miner Control thread (Port 30001)
# 3. Transaction receiver thread (Port 30002)
#
# Question server thread tasks:
# 1. Serving question and answer to Voter
# Miner Control thread tasks:
# 1. Send set of transactions to miner
#       - Send same transactions set every 5 minute if no miner purpose block
# 2. Stop mining when miner purpose a valid block (Verify before broadcast stop command)
# Transaction receiver thread tasks
# 1. Collect transactions from voter or registration
