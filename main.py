from big_brother import BigBrother
import time
from communication import *

def main():
    # Create BigBrother object (starts node structure)
    big_brother = BigBrother()

    # Execute transactions
    transactions = import_transactions("transactions.txt")
    print("Executing transactions...")
    big_brother.run(transactions)

    # Stop node structure
    print("Stopping Big Brother...")
    big_brother.stop()
    

if __name__ == "__main__":
    main()