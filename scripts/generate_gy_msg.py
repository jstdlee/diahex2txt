from diameter.message.commands import CreditControlRequest
from diameter.message.constants import *
from diameter.message.avp import AvpGrouped, AvpInteger32, AvpUtf8String, AvpUnsigned32, AvpTime

print("Starting generation...")

def create_complex_ccr():
    # Create a Credit-Control-Request
    ccr = CreditControlRequest()
    ccr.header.hop_by_hop_identifier = 0x12345678
    ccr.header.end_to_end_identifier = 0x87654321
    
    # Add Standard AVPs
    ccr.session_id = "ipv4:10.0.0.1:1234:5678"
    ccr.origin_host = b"client.example.com"
    ccr.origin_realm = b"example.com"
    ccr.destination_realm = b"server.example.com"
    ccr.auth_application_id = 4 # Gy (Diameter Credit Control application)
    ccr.service_context_id = "32251@3gpp.org" # Packet Switched
    ccr.cc_request_type = 1 # INITIAL_REQUEST
    ccr.cc_request_number = 0
    
    # Create Nested/Grouped AVPs (Multiple-Services-Credit-Control)
    mscc = AvpGrouped(AVP_MULTIPLE_SERVICES_CREDIT_CONTROL)
    
    # Rating-Group
    rg = AvpUnsigned32(AVP_RATING_GROUP)
    rg.value = 100
    mscc.value = [rg]
    
    # Requested-Service-Unit
    rsu = AvpGrouped(AVP_REQUESTED_SERVICE_UNIT)
    cc_time = AvpUnsigned32(AVP_CC_TIME)
    cc_time.value = 3600
    
    cc_total = AvpUnsigned32(AVP_CC_TOTAL_OCTETS)
    cc_total.value = 104857600
    rsu.value = [cc_time, cc_total]
    
    mscc.value.append(rsu)
    
    # Add MSCC to message
    # MSCC is usually a list (0*n)
    ccr.multiple_services_credit_control = [mscc]
    
    # User-Equipment-Info
    uei = AvpGrouped(AVP_USER_EQUIPMENT_INFO)
    uei_type = AvpEnumerated(AVP_USER_EQUIPMENT_INFO_TYPE)
    uei_type.value = 0 # IMEISV
    
    uei_val = AvpOctetString(AVP_USER_EQUIPMENT_INFO_VALUE)
    uei_val.value = b"123456789012345"
    uei.value = [uei_type, uei_val]
    
    ccr.user_equipment_info = uei
    
    # Convert to hex
    hex_output = ccr.as_bytes().hex()
    return hex_output

if __name__ == "__main__":
    from diameter.message.avp import AvpEnumerated, AvpOctetString 
    res = create_complex_ccr()
    with open("generated_hex.txt", "w") as f:
        f.write(res)
    print("Done")
