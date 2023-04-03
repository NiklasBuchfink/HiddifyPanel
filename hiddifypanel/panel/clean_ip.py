from hiddifypanel.models import *
from flask_babelex import gettext as _
default_ips="""
mcix.ircf.space		MCI
mci.ircf.space		MCI
mtn.ircf.space		MTN
mtnx.ircf.space		MTN
rtl.ircf.space		RTL
mkh.ircf.space		MKH
hwb.ircf.space		HWB
ast.ircf.space		AST
sht.ircf.space		SHT
prs.ircf.space		PRS
mbt.ircf.space		MBT
ask.ircf.space		ASK
rsp.ircf.space		RSP
afn.ircf.space		AFN
ztl.ircf.space		ZTL
psm.ircf.space		PSM
"""
from flask import request,flash
import maxminddb
import os
import re
import random

try:
    ipasn = maxminddb.open_database('GeoLite2-ASN.mmdb') if os.path.exists('GeoLite2-ASN.mmdb') else {}
    ipcountry = maxminddb.open_database('GeoLite2-Country.mmdb') if os.path.exists('GeoLite2-Country.mmdb') else {}
except Exception as e:
    print("Error can not load maxminddb")


asn_map={
    '58224':'MKH',
    '197207':'MCI',
    '12880':'ITC',
    '44244':'MTN',
    '57218':'RTL',
    '16322':'PRS',
    '56402':'HWB',
    '41689':'AST',
    '43754':'AST',
    '31549':'SHT',
    '205647':'SHT',
    '50810':'MBT',
    '39308':'ASK',
    '205207':'RSP',
    '25184':'AFR',
    '394510':'ZTL',
    '206065':'ZTL',
    '49100':'PSM'
}

def get_asn_short_name(user_ip=None):
    user_ip=user_ip or get_real_user_ip()
    asnres = ipasn.get(user_ip) if ipasn else {'autonomous_system_number':'unknown'}
    asn = f"{asnres.get('autonomous_system_number','unknown')}" if asnres else "unknown"
    return asn_map.get(asn,"unknown") 
def get_country(user_ip=None):
    user_ip=user_ip or get_real_user_ip()
    return (ipcountry.get(user_ip) or {}).get('country',{}).get('iso_code','unknown')
def get_real_user_ip_debug(user_ip=None):
    user_ip=user_ip or get_real_user_ip()
    asnres = ipasn.get(user_ip) or {}
    asn = f"{asnres.get('autonomous_system_number','unknown')}" if asnres else "unknown"
    asn_dscr = f"{asnres.get('autonomous_system_organization','unknown')}" if asnres else "unknown"
    asn_short=get_asn_short_name(user_ip)
    country=get_country(user_ip)
    default=get_host_base_on_asn(default_ips,asn_short).replace(".ircf.space","")
    return f'{user_ip} {country} {asn} {asn_short} {"ERROR" if asn_short=="unknown" else ""} fullname={asn_dscr} default:{default}' 

def get_real_user_ip():
    for header in ['CF-Connecting-IP','ar-real-ip']:
        if header in request.headers:
            return request.headers.get(header)
        
    return request.remote_addr

def get_host_base_on_asn(ips,asn_short):
    if type(ips)==str:
        ips=re.split('[ \t\r\n;,]+',ips.strip())
    valid_hosts=[ip for ip in ips if len(ip)>5]
    
    if len(ips)%2 !=0 or len(valid_hosts)==0:
        flash(_("Error! auto cdn ip can not be find, please contact admin."))
        if len(valid_hosts)==0:return

    all_hosts=[]
    for i in range(0,len(ips),2):
        if asn_short == ips[i+1]:
            print("selected ",ips[i],ips[i+1])
            all_hosts.append(ips[i])
    if len(all_hosts):
        return random.sample(all_hosts, 1)[0]
    
    return random.sample(valid_hosts,1)[0]

def get_clean_ip(ips,resolve=False,default_asn=None):
    if not ips:
        ips=default_ips
        
    ips=re.split('[ \t\r\n;,]+',ips.strip())
    user_ip=get_real_user_ip()
    asn_short = get_asn_short_name(user_ip)
    country=get_country(user_ip)
    print("Real user ip",get_real_user_ip_debug(), user_ip,asn_short,country)
    is_morteza_format=any([format for format in asn_map.values() if format in ips])
    print("IPs",ips)
    if is_morteza_format:
        if country.lower()!=hconfig(ConfigEnum.country) and default_asn:
            asn_short=default_asn
        selected_server=get_host_base_on_asn(ips, asn_short)
    else:
        selected_server=random.sample(ips, 1)[0]
    print("selected_server",selected_server)
    if resolve:
        from hiddifypanel.panel import hiddify
        return hiddify.get_domain_ip(selected_server) or selected_server
    return selected_server
    