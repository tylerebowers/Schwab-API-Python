"""
This file contains a class to manage tokens
Coded by Tyler Bowers
Github: https://github.com/tylerebowers/Schwab-API-Python
"""
import os
import ssl
import json
import time
import base64
import logging
import requests
import datetime
import threading
import webbrowser
import http.server


class Tokens:
    def __init__(self, client, app_key, app_secret, callback_url, tokens_file="tokens.json", update_tokens_auto=True):
        """
        Initialize a tokens manager
        :param client: client object
        :type client: Client
        :param app_key: app key credentials
        :type app_key: str
        :param app_secret: app secret credentials
        :type app_secret: str
        :param callback_url: url for callback
        :type callback_url: str
        :param tokens_file: path to tokens file
        :type tokens_file: str
        :param update_tokens_auto: update tokens automatically
        :type update_tokens_auto: bool
        """
        if app_key is None:
            raise Exception("[Schwabdev] app_key cannot be None.")
        if app_secret is None:
            raise Exception("[Schwabdev] app_secret cannot be None.")
        if callback_url is None:
            raise Exception("[Schwabdev] callback_url cannot be None.")
        if tokens_file is None:
            raise Exception("[Schwabdev] tokens_file cannot be None.")
        if len(app_key) != 32 or len(app_secret) != 16:
            raise Exception("[Schwabdev] App key or app secret invalid length.")
        if callback_url[0:5] != "https":
            raise Exception("[Schwabdev] callback_url must be https.")
        if callback_url[-1] == "/":
            raise Exception("[Schwabdev] callback_url cannot be path (ends with \"/\").")
        if tokens_file[-1] == '/':
            raise Exception("[Schwabdev] Tokens file cannot be path.")

        self._client = client                               # client object
        self._app_key = app_key                             # app key credential
        self._app_secret = app_secret                       # app secret credential
        self._callback_url = callback_url                   # callback url to use

        self.access_token = None                            # access token from auth
        self.refresh_token = None                           # refresh token from auth
        self.id_token = None                                # id token from auth
        self._access_token_issued = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)  # datetime of access token issue
        self._refresh_token_issued = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc) # datetime of refresh token issue
        self._access_token_timeout = 1800                   # in seconds (from schwab)
        self._refresh_token_timeout = 7 * 24 * 60 * 60      # in seconds (from schwab)
        self._tokens_file = tokens_file                     # path to tokens file

        self._logger = logging.getLogger("Schwabdev.Tokens")           # logger for this class

        # Try to load tokens from the tokens file
        if None not in self._read_tokens():
            if update_tokens_auto:
                self.update_tokens()  # check if tokens need to be updated and update if needed
            at_delta = self._access_token_timeout - (datetime.datetime.now(datetime.timezone.utc) - self._access_token_issued).total_seconds()
            self._logger.info(f"Access token expires in {'-' if at_delta < 0 else ''}{int(abs(at_delta) / 3600):02}H:{int((abs(at_delta) % 3600) / 60):02}M:{int((abs(at_delta) % 60)):02}S")
            rt_delta = self._refresh_token_timeout - (datetime.datetime.now(datetime.timezone.utc) - self._refresh_token_issued).total_seconds()
            self._logger.info(f"Refresh token expires in {'-' if rt_delta < 0 else ''}{int(abs(rt_delta) / 3600):02}H:{int((abs(rt_delta) % 3600) / 60):02}M:{int((abs(rt_delta) % 60)):02}S")
        else:
            # The tokens file doesn't exist, so create it.
            self._logger.warning(f"Token file does not exist or invalid formatting, creating \"{str(tokens_file)}\"")
            # Tokens must be updated.
            if update_tokens_auto:
                self.update_refresh_token()

        # Spawns a thread to check the access token and update if necessary
        if update_tokens_auto:
            def checker():
                while True:
                    self.update_tokens()
                    time.sleep(30)

            threading.Thread(target=checker, daemon=True).start()
        else:
            self._logger.warning("Warning: Tokens will not be updated automatically.")

    def _post_oauth_token(self, grant_type: str, code: str):
        """
        Makes API calls for auth code and refresh tokens
        :param grant_type: 'authorization_code' or 'refresh_token'
        :type grant_type: str
        :param code: authorization code
        :type code: str
        :return: response
        :rtype: requests.Response
        """
        headers = {'Authorization': f'Basic {base64.b64encode(bytes(f"{self._app_key}:{self._app_secret}", "utf-8")).decode("utf-8")}',
                   'Content-Type': 'application/x-www-form-urlencoded'}
        if grant_type == 'authorization_code':  # gets access and refresh tokens using authorization code
            data = {'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': self._callback_url}
        elif grant_type == 'refresh_token':  # refreshes the access token
            data = {'grant_type': 'refresh_token',
                    'refresh_token': code}
        else:
            raise Exception("Invalid grant type; options are 'authorization_code' or 'refresh_token'")
        return requests.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data)

    def _write_tokens(self, at_issued: datetime, rt_issued: datetime, token_dictionary: dict):
        """
        Writes token file and sets variables
        :param at_issued: access token issued
        :type at_issued: datetime.pyi
        :param rt_issued: refresh token issued
        :type rt_issued: datetime.pyi
        :param token_dictionary: token dictionary
        :type token_dictionary: dict
        """
        self.access_token = token_dictionary.get("access_token")
        self.refresh_token = token_dictionary.get("refresh_token")
        self.id_token = token_dictionary.get("id_token")
        self._access_token_issued = at_issued
        self._refresh_token_issued = rt_issued
        try:
            with open(self._tokens_file, 'w') as f:
                to_write = {"access_token_issued": at_issued.isoformat(),
                            "refresh_token_issued": rt_issued.isoformat(),
                            "token_dictionary": token_dictionary}
                json.dump(to_write, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self._logger.error(e)
            self._logger.error("Could not write tokens file")


    def _read_tokens(self):
        """
        Reads token file and sets variables
        :return: access token issued, refresh token issued, token dictionary
        :rtype: datetime.pyi, datetime.pyi, dict
        """
        try:
            with open(self._tokens_file, 'r') as f:
                d = json.load(f)
                token_dictionary = d.get("token_dictionary")
                self.access_token = token_dictionary.get("access_token")
                self.refresh_token = token_dictionary.get("refresh_token")
                self.id_token = token_dictionary.get("id_token")
                self._access_token_issued = datetime.datetime.fromisoformat(d.get("access_token_issued"))
                self._refresh_token_issued = datetime.datetime.fromisoformat(d.get("refresh_token_issued"))
                return self._access_token_issued, self._refresh_token_issued, token_dictionary
        except Exception as e:
            self._logger.error(e)
            return None, None, None

    def update_tokens(self, force=False):
        """
        Checks if tokens need to be updated and updates if needed (only access token is automatically updated)
        :param force: force update of refresh token (also updates access token)
        :type force: bool
        """
        # refresh token notification
        rt_delta = self._refresh_token_timeout - (datetime.datetime.now(datetime.timezone.utc) - self._refresh_token_issued).total_seconds()
        if rt_delta < 43200:  # Start to warn the user that the refresh token will expire in less than 43200 = 12 hours
            self._logger.info(f"The refresh token will expire soon! ({'-' if rt_delta < 0 else ''}{int(abs(rt_delta) / 3600):02}H:{int((abs(rt_delta) % 3600) / 60):02}M:{int((abs(rt_delta) % 60)):02}S remaining)")

        # check if we need to update refresh (and access) token
        if (rt_delta < 3600) or force:
            self._logger.warning("The refresh token has expired!")
            self.update_refresh_token()
        # check if we need to update access token
        elif (self._access_token_timeout - (datetime.datetime.now(datetime.timezone.utc) - self._access_token_issued).total_seconds()) < 61:
            self._logger.info("The access token has expired, updating automatically.")
            self.update_access_token()

    """
        Access Token functions below
    """

    def update_access_token(self):
        """
        "refresh" the access token using the refresh token
        """
        response = self._post_oauth_token('refresh_token', self.refresh_token)
        if response.ok:
            # get and update to the new access token
            at_issued = datetime.datetime.now(datetime.timezone.utc)
            self._write_tokens(at_issued, self._refresh_token_issued, response.json())
            # show user that we have updated the access token
            self._logger.info(f"Access token updated: {self._access_token_issued}")
        else:
            self._logger.error(response.text)
            self._logger.error(f"Could not get new access token; refresh_token likely invalid.")

    """
        Refresh Token functions below
    """

    def _generate_certificate(self, common_name="common_name", key_filepath="localhost.key", cert_filepath="localhost.crt"):
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa

        # make folders for cert files
        os.makedirs(os.path.dirname(key_filepath), exist_ok=True)
        os.makedirs(os.path.dirname(cert_filepath), exist_ok=True)

        # create a key pair
        key = rsa.generate_private_key(public_exponent=65537,key_size=2048)

        # create a self-signed cert
        builder = x509.CertificateBuilder()
        builder = builder.subject_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Schwabdev"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Authentication"),
        ]))
        builder = builder.issuer_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ]))
        builder = builder.not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        builder = builder.not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3650))
        builder = builder.serial_number(x509.random_serial_number())
        builder = builder.public_key(key.public_key())
        builder = builder.add_extension(
            x509.SubjectAlternativeName([x509.DNSName(common_name)]),
            critical=False,
        )
        builder = builder.sign(key, hashes.SHA256())
        with open(key_filepath, "wb") as f:
            f.write(key.private_bytes(encoding=serialization.Encoding.PEM,
                                      format=serialization.PrivateFormat.TraditionalOpenSSL,
                                      encryption_algorithm=serialization.NoEncryption()))
        with open(cert_filepath, "wb") as f:
            f.write(builder.public_bytes(serialization.Encoding.PEM))
        self._logger.info(f"Certificate generated and saved to {key_filepath} and {cert_filepath}")



    def _update_refresh_token_from_code(self, url_or_code):
        """
        Get new access and refresh tokens using callback url or authorization code.
        :param url_or_code: callback url (full url) or authorization code (the code=... in url)
        :type url_or_code: str
        """
        if url_or_code.startswith("https://"):
            code = f"{url_or_code[url_or_code.index('code=') + 5:url_or_code.index('%40')]}@"
            # session = responseURL[responseURL.index("session=")+8:]
        else:
            code = url_or_code
        # get new access and refresh tokens
        now = datetime.datetime.now(datetime.timezone.utc)
        response = self._post_oauth_token('authorization_code', code)
        if response.ok:
            # update token file and variables
            self._write_tokens(now, now, response.json())
            self._logger.info("Refresh and Access tokens updated")
        else:
            self._logger.error(response.text)
            self._logger.error("Could not get new refresh and access tokens, check these:\n"
                               "1. App status is \"Ready For Use\".\n"
                               "2. App key and app secret are valid.\n"
                               "3. You pasted the whole url within 30 seconds. (it has a quick expiration)")

    def update_refresh_token(self):
        """
        Get new access and refresh tokens using authorization code.
        """

        # get and open the link that the user will authorize with.
        auth_url = f'https://api.schwabapi.com/v1/oauth/authorize?client_id={self._app_key}&redirect_uri={self._callback_url}'
        print(f"[Schwabdev] Open to authenticate: {auth_url}")
        try:
            webbrowser.open(auth_url)
        except Exception as e:
            self._logger.error(e)
            self._logger.warning("Could not open browser for authorization")

        #parse the callback url
        url_split = self._callback_url.split("://")[-1].split(":")
        url_parsed = url_split[0]
        port_parsed = url_split[-1] # this may or may not have the port

        if port_parsed.isdigit(): # if there is a port then capture the callback url

            # class used to share code outside the http server
            class SharedCode:
                def __init__(self):
                    self.code = ""

            # custom HTTP handler to silence logger and get code
            class HTTPHandler(http.server.BaseHTTPRequestHandler):
                shared = None

                def log_message(self, format, *args):
                    pass  # silence logger

                def do_GET(self):
                    if self.path.find("code=") != -1:
                        self.shared.code = f"{self.path[self.path.index('code=') + 5:self.path.index('%40')]}@"
                    self.send_response(200, "OK")
                    self.end_headers()
                    self.wfile.write(b"You may now close this page.")

            shared = SharedCode()

            HTTPHandler.shared = shared
            httpd = http.server.HTTPServer((url_parsed, int(port_parsed)), HTTPHandler)

            cert_filepath = os.path.expanduser("~/.schwabdev/localhost.crt")
            key_filepath = os.path.expanduser("~/.schwabdev/localhost.key")
            if not (os.path.isfile(cert_filepath) and os.path.isfile(key_filepath)): #this does not check if the cert and key are valid
                self._generate_certificate(common_name=url_parsed, cert_filepath=cert_filepath, key_filepath=key_filepath)

            ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ctx.load_cert_chain(certfile=cert_filepath, keyfile=key_filepath)
            #ctx.load_default_certs()

            httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
            while len(shared.code) < 1: # wait for code
                httpd.handle_request()

            httpd.server_close()
            code = shared.code
        else: # if there is no port then the user must copy/paste the url
            response_url = input("[Schwabdev] After authorizing, paste the address bar url here: ")
            code = f"{response_url[response_url.index('code=') + 5:response_url.index('%40')]}@"

        if code is not None:
            self._update_refresh_token_from_code(code)
        else:
            self._logger.error("Could not get new refresh token without code.")
