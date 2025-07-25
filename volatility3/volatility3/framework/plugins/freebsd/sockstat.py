from typing import Any, Callable, Iterable, List
                        
import socket as sock

from volatility3.framework import interfaces, renderers, exceptions, symbols
from volatility3.framework.configuration import requirements
from volatility3.framework.renderers import TreeGrid
from volatility3.framework.objects import utility

from volatility3.framework.symbols import freebsd
from volatility3.plugins.freebsd import pslist, lsof, creds

AF_UNIX = 1		# standardized name for AF_LOCAL */
AF_INET = 2		# internetwork: UDP, TCP, etc. */
AF_IMPLINK = 3		# arpanet imp addresses */
AF_PUP = 4		# pup protocols: e.g. BSP */
AF_CHAOS = 5		# mit CHAOS protocols */
AF_NETBIOS = 6		# SMB protocols */
AF_ISO = 7		# ISO protocols */
AF_ECMA = 8		# European computer manufacturers */
AF_DATAKIT = 9		# datakit protocols */
AF_CCITT = 10		# CCITT protocols, X.25 etc */
AF_SNA = 11		# IBM SNA */
AF_DECnet = 12		# DECnet */
AF_DLI = 13		# DEC Direct data link interface */
AF_LAT = 14		# LAT */
AF_HYLINK = 15		# NSC Hyperchannel */
AF_APPLETALK = 16		# Apple Talk */
AF_ROUTE = 17		# Internal Routing Protocol */
AF_LINK = 18		# Link layer interface */
pseudo_AF_XTP = 19		# eXpress Transfer Protocol (no AF) */
AF_COIP = 20		# connection-oriented IP, aka ST II */
AF_CNT = 21		# Computer Network Technology */
pseudo_AF_RTIP = 22		# Help Identify RTIP packets */
AF_IPX = 23		# Novell Internet Protocol */
AF_SIP = 24		# Simple Internet Protocol */
pseudo_AF_PIP = 25		# Help Identify PIP packets */
AF_ISDN = 26		# Integrated Services Digital Network*/
AF_E164 = AF_ISDN		# CCITT E.164 recommendation */
pseudo_AF_KEY = 27		# Internal key-management function */
AF_INET6 = 28		# IPv6 */
AF_NATM = 29		# native ATM access */
AF_ATM = 30		# ATM */
pseudo_AF_HDRCMPLT = 31		# Used by BPF to not rewrite headers
AF_NETGRAPH = 32		# Netgraph sockets */
AF_SLOW = 33		# 802.3ad slow protocol */
AF_SCLUSTER = 34		# Sitara cluster protocol */
AF_ARP = 35
AF_BLUETOOTH = 36		# Bluetooth sockets */
AF_IEEE80211 = 37		# IEEE 802.11 protocol */
AF_NETLINK = 38		# Netlink protocol */
AF_INET_SDP = 40		# OFED Socket Direct Protocol ipv4 */
AF_INET6_SDP = 42		# OFED Socket Direct Protocol ipv6 */
AF_HYPERV = 43		# HyperV sockets */
AF_DIVERT = 44		# divert(4) */
AF_IPFWLOG = 46
AF_MAX = 46


class Sockstat(interfaces.plugins.PluginInterface):
    """Display open sockets (type sockstat) for FreeBSD."""

    _required_framework_version = (2, 0, 0)

    @classmethod
    def get_requirements(cls) -> List[interfaces.configuration.RequirementInterface]:
        return [
            requirements.ModuleRequirement(
                name="kernel",
                description="Kernel module for the OS",
                architectures=["Intel32", "Intel64"],
            ),
            requirements.ListRequirement(
                name="pid",
                description="Filter on specific process IDs",
                element_type=int,
                optional=True,
            ),
        ]

    def _generator(self):
        kernel = self.context.modules[self.config["kernel"]]
        tasks = pslist.PsList.list_tasks(self.context, self.config["kernel"])

        for task in tasks:
            pid = task.p_pid

            for fde_file, filepath, fd in freebsd.FreebsdUtilities.files_descriptors_for_process(self.context, kernel, task):
                if fde_file.f_type == 2:  # DTYPE_SOCKET
                    print("Found socket in task", pid, "with fd", fd)
                    
                    # Socket struct found in sys/sys/socket.h
                    socket = fde_file.f_data.dereference().cast("socket")
                    
                    # Inpbc struct found in sys/sys/in_pcb.h
                    inpcb = socket.so_pcb.dereference().cast("inpcb")

                    # Coninfo struct found in sys/sys/in_pcb.h
                    con_info = inpcb.inp_inc.cast("in_conninfo")

                    # In_endpoints union found in sys/sys/in_pcb.h
                    endpoints = con_info.inc_ie.cast("in_endpoints")


                    fam = int(socket.so_proto.pr_domain.dom_family)
                    proto = int(socket.so_proto.pr_protocol)

                    ie_fport = sock.ntohs(endpoints.ie_fport)		# foreign port
                    ie_lport = sock.ntohs(endpoints.ie_lport)		# local port

#define	ie_faddr	ie_dependfaddr.id46_addr.ia46_addr4
#define	ie_laddr	ie_dependladdr.id46_addr.ia46_addr4
                    a = int(endpoints.ie_dependfaddr.id46_addr.ia46_addr4.s_addr)
                    b = int(endpoints.ie_dependladdr.id46_addr.ia46_addr4.s_addr)
                    a = a.to_bytes(4, byteorder='little')
                    b = b.to_bytes(4, byteorder='little')

                    foreign_addr = sock.inet_ntoa(a) # Foreign address
                    local_addr = sock.inet_ntoa(b) # Local address

                    # Convert to bytes

                    print(f"Socket: PID={pid}, FD={fd}, Family={fam}, Protocol={proto}")
                    print(f"Local Port: {ie_lport}, Foreign Port: {ie_fport}")
                    print(f"Local Address: {local_addr}, Foreign Address: {foreign_addr}")

                    path = f"<SOCKET AF_{socket.so_proto.pr_domain.dom_family} IPPROTO_{socket.so_proto.pr_protocol}>"
                    print()

                    yield (0, (pid, fd, filepath))


    def run(self):
        columns = [
            ("PID", int),
            ("FD", int),
            ("FILEPATH", str),
        ]
        return TreeGrid(columns, self._generator())
