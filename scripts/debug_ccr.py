from diameter.message.commands import CreditControlRequest
from diameter.message import Message

ccr = CreditControlRequest()
print(f"CCR type: {type(ccr)}")
print(f"CCR dir: {dir(ccr)}")
try:
    print(f"Has add_avp: {hasattr(ccr, 'add_avp')}")
except:
    pass
