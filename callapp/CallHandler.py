import os
import pjsua2 as pj2
import threading

# Configuración de la troncal SIP de Telnyx
TELNYX_SIP_SERVER = "sip.telnyx.com"
TELNYX_USERNAME = "daniel30932"
TELNYX_PASSWORD = "Od7UvuML"

# Números para las llamadas
CALLER = "12058759185"
RECIPIENT = "12319362615"

# Ruta del archivo de audio
AUDIO_FILE = "assets/Days-of-the-week.wav"

# Verificar si el archivo de audio existe
if not os.path.isfile(AUDIO_FILE):
    raise FileNotFoundError(f"El archivo de audio no se encuentra en la ruta especificada: {AUDIO_FILE}")

# SIP Call Callback
class MyCallHandler(pj2.Call):
    def __init__(self, account, call_id=-1):
        super().__init__(account, call_id)
        self.audio_player = pj2.AudioMediaPlayer()

    def onCallState(self, prm):
        call_info = self.getInfo()
        print(f"Call state: {call_info.stateText}, Last Code: {call_info.lastStatusCode}")
        if call_info.state == pj2.PJSIP_INV_STATE_CONFIRMED:
            print("Call answered")
            self.play_audio()
        elif call_info.state == pj2.PJSIP_INV_STATE_DISCONNECTED:
            print("Call disconnected")
            self.hangup(pj2.CallOpParam())

    def onDtmfDigit(self, prm):
        print(f"DTMF received: {prm.digit}")

    def play_audio(self):
        # Reproducir el archivo de audio
        self.audio_player.createPlayer(AUDIO_FILE)
        call_media = self.getAudioMedia(-1)
        self.audio_player.startTransmit(call_media)

    def generate_tone(self):
        # Enviar un tono DTMF
        dtmf_param = pj2.CallSendDtmfParam()
        dtmf_param.digits = "1"  # Enviar el dígito "1" como tono DTMF
        self.dialDtmf(dtmf_param)

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
    transport_cfg.port = 5070  # Cambia el puerto a 5070
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

    def check_key_press():
        while True:
            if input() == 's':
                call.generate_tone()

    key_thread = threading.Thread(target=check_key_press)
    key_thread.start()

    input("Press Enter to quit...")
    call.hangup(pj2.CallOpParam())
except Exception as e:
    print(f"Exception: {e}")
finally:
    ep.libDestroy()
