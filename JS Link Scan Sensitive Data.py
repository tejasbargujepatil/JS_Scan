import requests
import re
import concurrent.futures
import logging

# Configure logging
logging.basicConfig(filename='sensitive_info_extraction.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_sensitive_info(js_url):
    try:
        logging.info(f"Fetching JavaScript file: {js_url}")
        response = requests.get(js_url)
        response.raise_for_status()
        js_code = response.text

        # Define patterns for sensitive information
        sensitive_patterns = {
            "api_keys": re.compile(r"['\"][A-Za-z0-9_]{30,}['\"]"),  # Example pattern for API keys
            "passwords": re.compile(r"['\"]password['\"]: ?['\"][^'\"]+['\"]"),  # Example pattern for passwords
            "google_api": r'AIza[0-9A-Za-z-_]{35}',
            "firebase": r'AAAA[A-Za-z0-9_-]{7}:[A-Za-z0-9_-]{140}',
            "google_captcha": r'6L[0-9A-Za-z-_]{38}|^6[0-9a-zA-Z_-]{39}$',
            "google_oauth": r'ya29\.[0-9A-Za-z\-_]+',
            "amazon_aws_access_key_id": r'A[SK]IA[0-9A-Z]{16}',
            "amazon_mws_auth_toke": r'amzn\\.mws\\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            "amazon_aws_url": r's3\.amazonaws.com[/]+|[a-zA-Z0-9_-]*\.s3\.amazonaws.com',
            "amazon_aws_url2": r"(" \
                    r"[a-zA-Z0-9-\.\_]+\.s3\.amazonaws\.com" \
                    r"|s3://[a-zA-Z0-9-\.\_]+" \
                    r"|s3-[a-zA-Z0-9-\.\_\/]+" \
                    r"|s3.amazonaws.com/[a-zA-Z0-9-\.\_]+" \
                    r"|s3.console.aws.amazon.com/s3/buckets/[a-zA-Z0-9-\.\_]+)",
            "facebook_access_token": r'EAACEdEose0cBA[0-9A-Za-z]+',
            "authorization_basic": r'basic [a-zA-Z0-9=:_\+\/-]{5,100}',
            "authorization_bearer": r'bearer [a-zA-Z0-9_\-\.=:_\+\/]{5,100}',
            "authorization_api": r'api[key|_key|\s+]+[a-zA-Z0-9_\-]{5,100}',
            "mailgun_api_key": r'key-[0-9a-zA-Z]{32}',
            "twilio_api_key": r'SK[0-9a-fA-F]{32}',
            "twilio_account_sid": r'AC[a-zA-Z0-9_\-]{32}',
            "twilio_app_sid": r'AP[a-zA-Z0-9_\-]{32}',
            "paypal_braintree_access_token": r'access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32}',
            "square_oauth_secret": r'sq0csp-[ 0-9A-Za-z\-_]{43}|sq0[a-z]{3}-[0-9A-Za-z\-_]{22,43}',
            "square_access_token": r'sqOatp-[0-9A-Za-z\-_]{22}|EAAA[a-zA-Z0-9]{60}',
            "stripe_standard_api": r'sk_live_[0-9a-zA-Z]{24}',
            "stripe_restricted_api": r'rk_live_[0-9a-zA-Z]{24}',
            "github_access_token": r'[a-zA-Z0-9_-]*:[a-zA-Z0-9_\-]+@github\.com*',
            "rsa_private_key": r'-----BEGIN RSA PRIVATE KEY-----',
            "ssh_dsa_private_key": r'-----BEGIN DSA PRIVATE KEY-----',
            "ssh_dc_private_key": r'-----BEGIN EC PRIVATE KEY-----',
            "pgp_private_block": r'-----BEGIN PGP PRIVATE KEY BLOCK-----',
            "json_web_token": r'ey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$',
            "slack_token": r"\"api_token\":\"(xox[a-zA-Z]-[a-zA-Z0-9-]+)\"",
            "SSH_privKey": r"([-]+BEGIN [^\s]+ PRIVATE KEY[-]+[\s]*[^-]*[-]+END [^\s]+ PRIVATE KEY[-]+)",
            "Heroku API KEY": r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}',
            "possible_Creds": r"(?i)(" \
                            r"password\s*[`=:\"]+\s*[^\s]+|" \
                            r"password is\s*[`=:\"]*\s*[^\s]+|" \
                            r"pwd\s*[`=:\"]*\s*[^\s]+|" \
                            r"passwd\s*[`=:\"]+\s*[^\s]+)"
            # Add more patterns for other sensitive information
        }

        # Search for sensitive information in the JavaScript code
        sensitive_info = {}
        for category, pattern in sensitive_patterns.items():
            matches = pattern.findall(js_code)
            if matches:
                sensitive_info[category] = matches
                logging.info(f"Found sensitive info ({category}) in {js_url}: {matches}")

        return sensitive_info
    except requests.RequestException as e:
        logging.error(f"Failed to retrieve JavaScript code from {js_url}: {e}")
        return {}

def read_js_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

if __name__ == "__main__":
    file_path = input("Enter the path to the text file containing JavaScript file URLs: ")
    logging.info(f"Reading JavaScript file URLs from {file_path}")
    js_urls = read_js_urls_from_file(file_path)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(extract_sensitive_info, js_urls)

    for js_url, sensitive_info in zip(js_urls, results):
        print(f"Sensitive information found in {js_url}:")
        if sensitive_info:
            for category, info in sensitive_info.items():
                print(f"{category.capitalize()}: {', '.join(info)}")
        else:
            print("No sensitive information found.")
