#!/usr/bin/env python3

-- coding: utf-8 --

"""
ORP - Network Diagnostics
Authorized local network diagnostics
Compatible with Termux / Linux / Windows
"""

import os
import sys
import re
import json
import time
import socket
import ipaddress
import platform
import subprocess
import concurrent.futures
from datetime import datetime

=====================================================

AUTO INSTALL COLORAMA

=====================================================

try:
from colorama import Fore, Style, init
init(autoreset=True)

except ImportError:
try:
subprocess.run(
[sys.executable, "-m", "pip", "install", "colorama"],
check=True,
timeout=45,
stdout=subprocess.DEVNULL,
stderr=subprocess.DEVNULL
)

from colorama import Fore, Style, init  
    init(autoreset=True)  

except Exception:  
    class Fore:  
        RED = ""  
        GREEN = ""  
        YELLOW = ""  
        BLUE = ""  
        MAGENTA = ""  
        CYAN = ""  
        WHITE = ""  

    class Style:  
        RESET_ALL = ""  
        BRIGHT = ""

C = Fore
S = Style

=====================================================

CONFIGURATION

=====================================================

APP_NAME = "ORP"

COMMON_PORTS = [
21, 22, 23, 25, 53, 80, 110, 139,
143, 443, 445, 554, 1900, 3306,
3389, 5000, 5353, 5555, 5900,
7000, 8008, 8080, 8443, 62078
]

PORT_INFO = {
21: ("FTP", "تحقق من الحاجة للخدمة واستخدم نقل ملفات مشفراً."),
22: ("SSH", "استخدم مصادقة قوية ومفاتيح دخول عند الحاجة."),
23: ("Telnet", "خدمة غير مشفرة؛ عطّلها إن لم تكن تحتاجها."),
25: ("SMTP", "تحقق من وظيفة خدمة البريد ومن صلاحيات الوصول."),
53: ("DNS", "قد تكون خدمة طبيعية على الراوتر."),
80: ("HTTP", "قد تكون واجهة إدارة؛ استخدم كلمة مرور قوية."),
110: ("POP3", "تحقق من الحاجة للخدمة والتشفير."),
139: ("NetBIOS", "قيّد مشاركة الملفات للأجهزة الموثوقة."),
143: ("IMAP", "تحقق من الحاجة للخدمة والتشفير."),
443: ("HTTPS", "خدمة ويب مشفرة؛ تحقق من هوية الخدمة."),
445: ("SMB", "لا تعرض مشاركة الملفات للإنترنت."),
554: ("RTSP", "قد تكون خدمة كاميرا أو بث."),
1900: ("SSDP/UPnP", "راجع إعداد UPnP في الراوتر."),
3306: ("MySQL", "قيّد الوصول إلى قاعدة البيانات."),
3389: ("RDP", "استخدم VPN ومصادقة قوية عند الحاجة."),
5000: ("APP", "تحقق من التطبيق الذي يستخدم المنفذ."),
5353: ("mDNS", "قد يكون طبيعياً لاكتشاف الأجهزة المحلية."),
5555: ("ADB", "أوقف تصحيح Android اللاسلكي عند عدم الحاجة."),
5900: ("VNC", "تحقق من المصادقة وقيود الوصول."),
7000: ("CAST", "قد تكون خدمة بث محلية."),
8008: ("CHROMECAST", "قد تكون خدمة بث محلية."),
8080: ("HTTP-ALT", "تحقق من التطبيق الذي يشغّل الخدمة."),
8443: ("HTTPS-ALT", "قد تكون واجهة إدارة بديلة."),
62078: ("APPLE-SYNC", "قد تكون خدمة مزامنة محلية.")
}

=====================================================

UI

=====================================================

def clear():
os.system("cls" if os.name == "nt" else "clear")

def banner():
print(C.CYAN + r"""


---

/ __ / __ / __ \
/ // / // / /_/ /
/ , / , / , /
// |// |// |/

""" + S.RESET_ALL)

print(C.MAGENTA + "       ORP NETWORK DIAGNOSTICS")  
print(C.WHITE + "       Interactive Console")  
print(C.CYAN + "=" * 55)

def line():
print(C.CYAN + "-" * 55 + S.RESET_ALL)

def info(msg):
print(C.CYAN + "[*] " + str(msg))

def success(msg):
print(C.GREEN + "[+] " + str(msg))

def warning(msg):
print(C.YELLOW + "[!] " + str(msg))

def error(msg):
print(C.RED + "[-] " + str(msg))

def pause():
input(C.YELLOW + "\nاضغط Enter للمتابعة...")

=====================================================

COMMAND EXECUTION

=====================================================

def run_cmd(args, timeout=5):

try:  
    result = subprocess.run(  
        args,  
        capture_output=True,  
        text=True,  
        timeout=timeout  
    )  

    return result.stdout.strip()  

except Exception:  
    return ""

=====================================================

NETWORK INFORMATION

=====================================================

def get_local_ip():

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  

try:  
    s.connect(("192.0.2.1", 80))  
    return s.getsockname()[0]  

except Exception:  
    return ""  

finally:  
    s.close()

def get_gateway():

if os.path.exists("/proc/net/route"):  

    try:  
        with open("/proc/net/route") as f:  

            next(f, None)  

            for row in f:  

                parts = row.split()  

                if len(parts) > 3 and parts[1] == "00000000":  

                    raw = bytes.fromhex(parts[2])  

                    return socket.inet_ntoa(raw[::-1])  

    except Exception:  
        pass  

output = run_cmd(["ip", "route"])  

match = re.search(r"default via ([0-9.]+)", output)  

if match:  
    return match.group(1)  

output = run_cmd(["ipconfig"])  

match = re.search(  
    r"Default Gateway[ .:]*([0-9.]+)",  
    output,  
    re.I  
)  

return match.group(1) if match else ""

def get_network():

local = get_local_ip()  

if not local:  
    return None  

output = run_cmd(["ip", "-4", "route"])  

for row in output.splitlines():  

    match = re.match(  
        r"([0-9.]+/\d+)\s+dev\s+\S+",  
        row  
    )  

    if match:  

        try:  

            network = ipaddress.ip_network(  
                match.group(1),  
                strict=False  
            )  

            if ipaddress.ip_address(local) in network:  
                return network  

        except ValueError:  
            pass  

warning("تعذر تحديد قناع الشبكة بدقة؛ استخدام /24 كتقدير.")  

return ipaddress.ip_network(local + "/24", strict=False)

def get_arp_table():

devices = {}  

try:  

    with open("/proc/net/arp") as f:  

        next(f, None)  

        for row in f:  

            parts = row.split()  

            if len(parts) >= 4:  

                ip = parts[0]  
                mac = parts[3].lower()  

                if mac != "00:00:00:00:00:00":  
                    devices[ip] = mac  

except Exception:  
    pass  

output = run_cmd(["ip", "neigh"])  

for row in output.splitlines():  

    match = re.search(  
        r"^(\S+).*lladdr\s+([0-9a-f:]{17})",  
        row,  
        re.I  
    )  

    if match:  
        devices[match.group(1)] = match.group(2).lower()  

return devices

=====================================================

TARGET VALIDATION

=====================================================

def validate_target(value):

try:  

    if "/" in value:  
        return ipaddress.ip_network(value, strict=False)  

    return ipaddress.ip_address(value)  

except ValueError:  
    return None

def choose_target():

while True:  

    value = input(  
        C.GREEN + "\nأدخل IP أو Network: " + S.RESET_ALL  
    ).strip()  

    if validate_target(value):  
        return value  

    error("عنوان IP أو Network غير صالح.")

=====================================================

HOSTNAME

=====================================================

def get_hostname(ip):

try:  
    return socket.gethostbyaddr(ip)[0]  

except Exception:  
    return "-"

=====================================================

CONNECTIVITY

=====================================================

def ping_host(ip):

if platform.system().lower() == "windows":  

    command = [  
        "ping", "-n", "1", "-w", "2000", ip  
    ]  

else:  

    command = [  
        "ping", "-c", "1", "-W", "2", ip  
    ]  

try:  

    result = subprocess.run(  
        command,  
        stdout=subprocess.DEVNULL,  
        stderr=subprocess.DEVNULL,  
        timeout=4  
    )  

    return result.returncode == 0  

except Exception:  
    return False

=====================================================

PORT SCANNER

=====================================================

def check_port(ip, port, timeout=0.5):

try:  

    with socket.socket(  
        socket.AF_INET,  
        socket.SOCK_STREAM  
    ) as s:  

        s.settimeout(timeout)  

        return s.connect_ex((ip, port)) == 0  

except OSError:  
    return False

def parse_ports(value):

ports = set()  

for item in value.split(","):  

    item = item.strip()  

    if not item:  
        continue  

    if "-" in item:  

        first, last = map(int, item.split("-", 1))  

        if first < 1 or last > 65535:  
            raise ValueError("نطاق منافذ غير صالح.")  

        if first > last or last - first > 2048:  
            raise ValueError("النطاق غير صالح أو كبير جداً.")  

        ports.update(range(first, last + 1))  

    else:  

        port = int(item)  

        if not 1 <= port <= 65535:  
            raise ValueError("رقم منفذ غير صالح.")  

        ports.add(port)  

if not ports:  
    raise ValueError("لم يتم تحديد أي منفذ.")  

return sorted(ports)

def remediation(port):

name, advice = PORT_INFO.get(  
    port,  
    ("Unknown", "تحقق من الخدمة قبل تغيير إعداداتها.")  
)  

line()  

print(C.MAGENTA + "PORT REMEDIATION")  
print(C.WHITE + f"Port: {port}")  
print(C.WHITE + f"Service: {name}")  

print(C.YELLOW + "\nالتوصية:")  
print(advice)  

print("""

خطوات المعالجة:

1. حدد الجهاز الذي يشغّل الخدمة.
2. افتح إعدادات الجهاز الرسمية.
3. تحقق من أن الخدمة غير مطلوبة.
4. عطّلها أو قيّد الوصول إليها من إعداداتها.
5. اختبر الخدمة مجدداً بعد التغيير.

ORP لا تغلق المنافذ تلقائياً.
إغلاق الخدمة يتم من الجهاز أو واجهة إدارته.
""")

input("اضغط Enter للرجوع...")

def scan_ports(ip, ports):

info(f"فحص {len(ports)} منفذ على {ip}")  

opened = []  

with concurrent.futures.ThreadPoolExecutor(  
    max_workers=50  
) as executor:  

    futures = {  
        executor.submit(check_port, ip, port): port  
        for port in ports  
    }  

    for future in concurrent.futures.as_completed(futures):  

        port = futures[future]  

        try:  

            if future.result():  
                opened.append(port)  

        except Exception:  
            pass  

opened.sort()  

if not opened:  

    warning("لم يتم اكتشاف منافذ مفتوحة ضمن القائمة.")  

    return  

for port in opened:  

    name, advice = PORT_INFO.get(  
        port,  
        ("Unknown", "تحقق من الخدمة يدوياً.")  
    )  

    print(C.GREEN + f"\n[OPEN] {port}/TCP - {name}")  

    print(C.WHITE + advice)  

    print("""

[1] عرض معالجة المنفذ
[Enter] المنفذ التالي
""")

choice = input("ORP PORT > ").strip()  

    if choice == "1":  
        remediation(port)

def port_menu(target):

if "/" in target:  

    warning("فحص المنافذ يحتاج عنوان IP واحداً.")  

    return  

print("""

[1] فحص المنافذ الشائعة
[2] فحص منافذ محددة
[3] فحص نطاق منافذ
[0] رجوع
""")

choice = input("ORP PORTS > ").strip()  

try:  

    if choice == "1":  

        ports = COMMON_PORTS  

    elif choice == "2":  

        ports = parse_ports(  
            input("أدخل المنافذ: ")  
        )  

    elif choice == "3":  

        ports = parse_ports(  
            input("أدخل النطاق مثل 8000-8100: ")  
        )  

    else:  
        return  

    scan_ports(target, ports)  

except ValueError as exc:  

    error(exc)

=====================================================

DEVICE CLASSIFICATION

=====================================================

def classify_device(ip, mac, ports, gateway):

if gateway and ip == gateway:  
    return "Router / Gateway"  

if 5555 in ports:  
    return "Android (احتمالي)"  

if 62078 in ports:  
    return "Apple (احتمالي)"  

if any(p in ports for p in (8008, 7000, 554)):  
    return "Media / Camera (احتمالي)"  

if any(p in ports for p in (445, 139, 3389)):  
    return "Windows (احتمالي)"  

if any(p in ports for p in (22, 80, 443, 8080)):  
    return "Network Device"  

return "Unknown"

def discover_devices(network):

hosts = list(network.hosts())  

if len(hosts) > 512:  

    warning("الشبكة أكبر من الحد المسموح للاكتشاف التلقائي.")  

    return []  

found = set()  

arp = get_arp_table()  

found.update(arp.keys())  

gateway = get_gateway()  

if gateway:  
    found.add(gateway)  

info(f"اكتشاف الأجهزة ضمن {network}")  

def probe(ip):  

    ip = str(ip)  

    if ping_host(ip):  
        return ip  

    for port in (80, 443, 22, 445, 53):  

        if check_port(ip, port, 0.2):  
            return ip  

    return None  

with concurrent.futures.ThreadPoolExecutor(  
    max_workers=40  
) as executor:  

    results = executor.map(probe, hosts)  

    for result in results:  

        if result:  
            found.add(result)  

return sorted(  
    [x for x in found if ipaddress.ip_address(x) in network],  
    key=lambda x: int(ipaddress.ip_address(x))  
)

def show_devices():

network = get_network()  

if not network:  

    error("تعذر تحديد الشبكة.")  

    return  

devices = discover_devices(network)  

arp = get_arp_table()  

gateway = get_gateway()  

print("\n" + "=" * 95)  

print(  
    f"{'IP':<18}"  
    f"{'MAC':<20}"  
    f"{'HOSTNAME':<28}"  
    f"{'TYPE'}"  
)  

print("=" * 95)  

for ip in devices:  

    mac = arp.get(ip, "-")  

    hostname = get_hostname(ip)  

    ports = [  
        p for p in (  
            22, 53, 80, 443, 445,  
            554, 5555, 62078, 7000, 8008  
        )  
        if check_port(ip, p, 0.2)  
    ]  

    device_type = classify_device(  
        ip,  
        mac,  
        ports,  
        gateway  
    )  

    print(  
        f"{ip:<18}"  
        f"{mac:<20}"  
        f"{hostname[:27]:<28}"  
        f"{device_type}"  
    )  

print("=" * 95)  

warning(  
    "الاكتشاف غير مضمون لكل الأجهزة، والتصنيف احتمالي."  
)

=====================================================

ROUTER INFORMATION

=====================================================

def router_information():

local = get_local_ip()  

gateway = get_gateway()  

network = get_network()  

print("\n--- معلومات الشبكة ---")  

print(f"IP الجهاز       : {local or '-'}")  

print(f"IP الراوتر      : {gateway or '-'}")  

print(f"عنوان الشبكة    : {network or '-'}")  

print(f"النظام          : {platform.platform()}")  

print(f"Python          : {platform.python_version()}")  

if gateway:  

    print("\nفحص واجهة الراوتر:")  

    for port, name in (  
        (80, "HTTP"),  
        (443, "HTTPS")  
    ):  

        if check_port(gateway, port):  

            success(f"{name} متاح على المنفذ {port}")  

        else:  

            warning(f"{name} غير متاح على المنفذ {port}")  

    print(  
        "\nتسجيل الدخول والتعديلات تتم عبر واجهة الراوتر الرسمية."  
    )

=====================================================

REPORT

=====================================================

def export_report(target):

report = {  

    "tool": APP_NAME,  

    "date": datetime.now().isoformat(),  

    "target": target,  

    "local_ip": get_local_ip(),  

    "gateway": get_gateway(),  

    "network": str(get_network() or ""),  

    "platform": platform.platform(),  

    "python": platform.python_version(),  

    "arp_devices": get_arp_table()  

}  

filename = (  
    "ORP_REPORT_"  
    + datetime.now().strftime("%Y%m%d_%H%M%S")  
    + ".json"  
)  

try:  

    with open(  
        filename,  
        "w",  
        encoding="utf-8"  
    ) as file:  

        json.dump(  
            report,  
            file,  
            indent=4,  
            ensure_ascii=False  
        )  

    success(f"تم حفظ التقرير: {filename}")  

except Exception as exc:  

    error(exc)

=====================================================

MAIN MENU

=====================================================

def main_menu(target):

while True:  

    clear()  

    banner()  

    print(C.GREEN + f"الهدف الحالي: {target}")  

    line()  

    print("""

[1] اختبار الاتصال
[2] البحث عن اسم الجهاز
[3] فحص المنافذ
[4] اكتشاف الأجهزة المتصلة
[5] معلومات الراوتر والشبكة
[6] إنشاء تقرير
[7] تغيير الهدف
[8] فتح واجهة إدارة الراوتر
[0] خروج
""")

choice = input(C.MAGENTA + "ORP > ").strip()  

    if choice == "1":  

        if "/" in target:  

            warning("هذا الخيار يحتاج IP واحداً.")  

        elif ping_host(target):  

            success("الجهاز استجاب.")  

        else:  

            warning("لا توجد استجابة Ping.")  

            warning("قد يكون ICMP محظوراً.")  

        pause()  

    elif choice == "2":  

        if "/" in target:  

            warning("أدخل IP واحداً.")  

        else:  

            success(  
                "Hostname: " + get_hostname(target)  
            )  

        pause()  

    elif choice == "3":  

        port_menu(target)  

        pause()  

    elif choice == "4":  

        show_devices()  

        pause()  

    elif choice == "5":  

        router_information()  

        pause()  

    elif choice == "6":  

        export_report(target)  

        pause()  

    elif choice == "7":  

        target = choose_target()  

        success("تم تغيير الهدف.")  

        time.sleep(0.5)  

    elif choice == "8":  

        gateway = get_gateway()  

        if not gateway:  

            warning("تعذر اكتشاف الراوتر.")  

        else:  

            url = (  
                "https://" + gateway  
                if check_port(gateway, 443)  
                else "http://" + gateway  
            )  

            print("واجهة الإدارة:", url)  

            try:  

                import webbrowser  

                webbrowser.open(url)  

            except Exception:  

                pass  

        pause()  

    elif choice == "0":  

        success("تم إغلاق ORP.")  

        break  

    else:  

        warning("اختيار غير صحيح.")  

        pause()

=====================================================

STARTUP

=====================================================

def main():

while True:  

    clear()  

    banner()  

    print("""

[1] إدخال IP أو شبكة
[2] اكتشاف الراوتر تلقائياً
[3] معلومات الشبكة المحلية
[0] خروج
""")

choice = input("ORP START > ").strip()  

    if choice == "1":  

        target = choose_target()  

        main_menu(target)  

    elif choice == "2":  

        gateway = get_gateway()  

        if gateway:  

            success("الراوتر: " + gateway)  

            main_menu(gateway)  

        else:  

            warning("تعذر اكتشاف الراوتر.")  

            pause()  

    elif choice == "3":  

        router_information()  

        pause()  

    elif choice == "0":  

        break  

    else:  

        warning("اختيار غير صحيح.")  

        pause()

if name == "main":

try:  

    main()  

except KeyboardInterrupt:  

    print(C.YELLOW + "\nتم إيقاف ORP.")  

except Exception as exc:  

    error(f"خطأ غير متوقع: {exc}")  

    input("اضغط Enter للخروج...")
