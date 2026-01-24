from diameter.message.avp import AvpGrouped, AvpInteger32
from diameter.message.constants import *

try:
    g = AvpGrouped(AVP_MULTIPLE_SERVICES_CREDIT_CONTROL)
    print(f"Dir: {dir(g)}")
    print(f"Value type: {type(g.value)}")
except Exception as e:
    print(f"Error: {e}")
