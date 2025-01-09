import pjsua2 as pj2

# Configuración de la troncal SIP de Telnyx
TELNYX_SIP_SERVER = "sip.telnyx.com"
TELNYX_USERNAME = "myusername"
TELNYX_PASSWORD = "mypassword"

# Números para las llamadas
CALLER = "+120"
RECIPIENT = "+123"

# SIP Call Callback
class MyCallHandler(pj2.Call):
    def __init__(self, account, call_id=-1):
        super().__init__(account, call_id)

    def onCallState(self, prm):
        call_info = self.getInfo()
        print(f"Call state: {call_info.stateText}, Last Code: {call_info.lastStatusCode}")

    def onDtmfDigit(self, prm):
        print(f"DTMF received: {prm.digit}")

# Main Endpoint Setup
ep = pj2.Endpoint()
ep.libCreate()

try:
    # Initialize endpoint
    ep_cfg = pj2.EpConfig()
    ep_cfg.logConfig.level = 5
    ep_cfg.logConfig.consoleLevel = 5

    ep.libInit(ep_cfg)

    # Configure no audio device
    ep.audDevManager().setNullDev()

    # Create transport
    transport_cfg = pj2.TransportConfig()
    transport_cfg.port = 5060
    ep.transportCreate(pj2.PJSIP_TRANSPORT_UDP, transport_cfg)

    # Start library
    ep.libStart()

    # Account configuration
    acc_cfg = pj2.AccountConfig()
    acc_cfg.idUri = f"sip:{TELNYX_USERNAME}@{TELNYX_SIP_SERVER}"
    acc_cfg.regConfig.registrarUri = f"sip:{TELNYX_SIP_SERVER}"
    acc_cfg.regConfig.timeoutSec = 3600  # Registro cada 3600 segundos
    cred = pj2.AuthCredInfo("digest", "*", TELNYX_USERNAME, 0, TELNYX_PASSWORD)
    acc_cfg.sipConfig.authCreds.append(cred)

    # Create account
    acc = pj2.Account()
    acc.create(acc_cfg)
    print("**************************|______SIP registration successful.______|**************************")

    # Make a call
    call = MyCallHandler(acc)
    call.makeCall(f"sip:{RECIPIENT}@{TELNYX_SIP_SERVER}", pj2.CallOpParam())
    print("**************************|______MAKE CALL______|**************************")

    input("Press Enter to quit...")
    call.hangup(pj2.CallOpParam())
except Exception as e:
    print(f"Exception: {e}")
finally:
    ep.libDestroy()
