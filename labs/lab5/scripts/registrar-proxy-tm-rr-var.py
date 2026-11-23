import sys
import os
import KSR as KSR
from aux_classes import RedisDB

# Mandatory function - module initiation
def mod_init():
    KSR.info("===== from Python mod init\n")
    return kamailio()

class kamailio:
#    cls_counter = 0

    # Mandatory function - Kamailio class initiation
    def __init__(self):
        KSR.info('===== kamailio.__init__\n')
        self.db = RedisDB("sipnet.redis")
        # Get the local domain value 
        self.local_domain = os.getenv("SIP_DOMAIN") or ""   
        if self.db.exists(self.local_domain+"_counter"):
            KSR.info('===== Existing ' + self.local_domain+"_counter" + '\n')
        else:
            KSR.info('===== Creating ' + self.local_domain+"_counter" + '\n')
            self.db.seti(self.local_domain+"_counter", 0)

    # Mandatory function - Kamailio subprocesses
    def child_init(self, rank):
        KSR.info('===== kamailio.child_init(%d)\n' % rank)
        KSR.pv.seti("$avp(avp_counter)", 0)
        return 0

    # Function called foWr REQUEST messages received 
    def ksr_request_route(self, msg):
        # Working as a Registrar server
        if  (msg.Method == "REGISTER"):
            KSR.info("REGISTER R-URI: " + KSR.pv.get("$ru") + "\n")      # Obtaining values via Pseudo-variables (pv)
            KSR.info("            To: " + KSR.pv.get("$tu") +
                           " Contact: " + KSR.hdr.get("Contact") +"\n")  # Obtaining values via message header fields
            KSR.registrar.save('location', 0)                            # Calling Kamailio "registrar" module
            return 1

        # Working as a Redirect server
        if (msg.Method == "INVITE"):                      
            KSR.info("INVITE R-URI: " + KSR.pv.get("$ru") + "\n")
            KSR.info("        From: " + KSR.pv.get("$fu") +
                              " To: " + KSR.pv.get("$tu") +"\n")

            #Updating the INVITE counters
#            self.cls_counter = self.cls_counter + 1
            KSR.pv.seti("$avp(avp_counter)", KSR.pv.geti("$avp(avp_counter)") +1)
            KSR.pv.seti("$shv(shv_counter)", KSR.pv.geti("$shv(shv_counter)") +1)
            self.db.seti(self.local_domain+"_counter", 
                         self.db.geti(self.local_domain+"_counter") + 1)

            KSR.info("----   AVP counter: " + str(KSR.pv.geti("$avp(avp_counter)")) + "\n")
            KSR.info("----   SHV counter: " + str(KSR.pv.geti("$shv(shv_counter)")) + "\n")
            KSR.info("----   Redis counter: " + str(self.db.geti(self.local_domain+"_counter")) + '\n')

            if (KSR.pv.get("$td") != self.local_domain): # Check if To domain is the local domain
                KSR.rr.record_route()  # Add Record-Route header
                KSR.tm.t_relay()   # Forwarding using transaction mode
                return 1

            if (KSR.pv.get("$td") == self.local_domain):  # Check if To domain is local
                if (KSR.registrar.lookup("location") == 1):   # Check if registered
                    KSR.info("  lookup changed R-URI to : " + KSR.pv.get("$ru") +"\n")
                    KSR.rr.record_route()  # Add Record-Route header
                    KSR.tm.t_relay()   # Forwarding using transaction mode
                    return 1
                else:
                    KSR.sl.send_reply(404, "Not found")
                    return 1
                
        if (msg.Method == "ACK"):
            KSR.info("ACK R-URI: " + KSR.pv.get("$ru") + "\n")
            KSR.rr.loose_route()  # In case there are Record-Route headers
            KSR.registrar.lookup("location")
            KSR.tm.t_relay()
            return 1

        if (msg.Method == "BYE"):
            KSR.info("BYE R-URI: " + KSR.pv.get("$ru") + "\n")
            KSR.rr.loose_route()    # In case there are Record-Route headers
            KSR.registrar.lookup("location")
            KSR.tm.t_relay()
            return 1

        if (msg.Method == "CANCEL"):
            KSR.info("CANCEL R-URI: " + KSR.pv.get("$ru") + "\n")
            KSR.rr.loose_route()    # In case there are Record-Route headers
            KSR.registrar.lookup("location")
            KSR.tm.t_relay()
            return 1

        # If this part is reached then Method is not allowed
        KSR.sl.send_reply(403, "Forbiden method")
        return 1

    # Function called for REPLY messages received
    def ksr_reply_route(self, msg):
        KSR.info("===== response - from kamailio python script\n")
        KSR.info("      Status is:"+ str(KSR.pv.get("$rs")) + "\n")
#        KSR.info("---- Class counter: " + str(self.cls_counter))
        KSR.info("----   AVP counter: " + str(KSR.pv.geti("$avp(avp_counter)")) + "\n")
        KSR.info("----   SHV counter: " + str(KSR.pv.geti("$shv(shv_counter)")) + "\n")
        KSR.info("----   Redis counter: " + str(self.db.geti(self.local_domain+"_counter")) + '\n')
        return 1

    # Function called for messages sent/transit
    def ksr_onsend_route(self, msg):
        KSR.info("===== onsend route - from kamailio python script\n")
        KSR.info("      %s\n" %(msg.Type))
        return 1

    # Special function for INVITE methods (on failure)
    def ksr_failure_route_INVITE(self, msg):
        KSR.info("===== INVITE failure route - from kamailio python script\n")
        return 1
