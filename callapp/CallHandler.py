import os
import pjsua2 as pj2

# Telnyx SIP Trunk Configuration
TELNYX_SIP_SERVER = "sip.telnyx.com"
TELNYX_USERNAME = "myuser"
TELNYX_PASSWORD = "mypass"

# Numbers for calls
CALLER = "120"
RECIPIENT = "123"

# Audio file path
AUDIO_FILE = "assets/Days-of-the-week.wav"

# Check if the file exists
if not os.path.isfile(AUDIO_FILE):
    raise FileNotFoundError(
        f"El archivo de audio no se encuentra en la ruta especificada: {AUDIO_FILE}")

# SIP Call Callback

class MyCallHandler(pj2.Call):
    def __init__(self, account, call_id=-1):
        super().__init__(account, call_id)
        self.audio_player = pj2.AudioMediaPlayer()
        self.tonegen = None

    def onCallState(self, prm):
        call_info = self.getInfo()
        print(f"Call state: {call_info.stateText}, Last Code: {
              call_info.lastStatusCode}")
        if call_info.state == pj2.PJSIP_INV_STATE_CONFIRMED:
            print("Call answered")
            self.play_audio()
        elif call_info.state == pj2.PJSIP_INV_STATE_DISCONNECTED:
            print("Call disconnected")
            self.hangup(pj2.CallOpParam())

    def onDtmfDigit(self, prm):
        print(f"DTMF received: {prm.digit}")
        if prm.digit == '7':
            self.generate_tone()

    def play_audio(self):
        # Play audio file
        self.audio_player.createPlayer(AUDIO_FILE)
        call_media = self.getAudioMedia(-1)
        self.audio_player.startTransmit(call_media)

    def generate_tone(self):
        # Send a DTMF tone
        print(f"|*********** generate_tone ***********|")
        self.dialDtmf('#')


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
    transport_cfg.port = 5070
    ep.transportCreate(pj2.PJSIP_TRANSPORT_UDP, transport_cfg)

    # Start library
    ep.libStart()

    # Account configuration
    acc_cfg = pj2.AccountConfig()
    acc_cfg.idUri = f"sip:{CALLER}@{TELNYX_SIP_SERVER}"
    acc_cfg.regConfig.registrarUri = f"sip:{TELNYX_SIP_SERVER}"
    acc_cfg.regConfig.timeoutSec = 3600  # Registro cada 3600 segundos
    cred = pj2.AuthCredInfo("digest", "*", TELNYX_USERNAME, 0, TELNYX_PASSWORD)
    acc_cfg.sipConfig.authCreds.append(cred)

    # Create account
    acc = pj2.Account()
    acc.create(acc_cfg)
    print("**************************|______SIP registration successful.______|**************************")

    # Check registration status
    acc_info = acc.getInfo()
    if acc_info.regIsActive:
        print("Account is registered")
    else:
        print("Account registration failed")

    # Make a call
    call = MyCallHandler(acc)
    call_param = pj2.CallOpParam()
    call_param.opt.audioCount = 1
    call_param.opt.videoCount = 0

    # Set the From header with the CALLER number
    sip_uri = f"sip:{RECIPIENT}@{TELNYX_SIP_SERVER}"

    call.makeCall(sip_uri, call_param)
    print("**************************|______MAKE CALL______|**************************")

    input("Press Enter to quit...")
    call.hangup(pj2.CallOpParam())
except Exception as e:
    print(f"Exception: {e}")
finally:
    ep.libDestroy()
