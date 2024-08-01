Owens Personal Game Authenticator (PMA) Bridge
Overview

Owens Personal Game Authenticator (PMA) Bridge is a custom implementation of the mc-authn library. This tool acts as a bridge for Minecraft authentication, leveraging Microsoft’s OAuth 2.0 services to streamline the process of obtaining and managing Minecraft authentication tokens. It is specifically tailored for personal projects and is not intended for commercial use or broad distribution.

Note: This project is currently in development and designed for personal use only.
Features

    OAuth 2.0 Authentication: Utilizes Microsoft’s OAuth 2.0 for secure authentication.
    Custom Implementation: A personalized version of the mc-authn library.
    Token Management: Automates the retrieval and management of authentication tokens for Minecraft.
    Flask API Endpoint: Includes a Flask API endpoint to initiate and manage authentication requests.
    Custom Domain Integration: Designed to work with a custom domain using callback.py to forward requests to the authentication server.

Requirements

    Python 3.7 or higher
    mc-authn library (installed via pip)
    Flask for the API
    Microsoft Azure account for OAuth setup

Installation

    Clone the Repository

    bash

git clone https://github.com/yourusername/pma-bridge.git
cd pma-bridge

Install Dependencies

Ensure you have Python 3.7 or higher installed, then install the required Python packages:

bash

    pip install requests flask ruamel.yaml

Setup

    Configure Azure OAuth
        Sign in to the Azure Portal.
        Navigate to Azure Active Directory > App registrations > New registration.
        Create a new application and set Redirect URI to http://localhost:18275.
        Note down the Application (client) ID, Client Secret, and Directory (Tenant) ID.

    Update Hard-Coded Values

    The authserver.py script contains hard-coded values for ClientID, ClientSecret, and TenantID. Replace these placeholders in the script with your actual Azure credentials:

    python

    CLIENT_ID = "YOUR_CLIENT_ID"  # Replace with your Azure Client ID
    CLIENT_SECRET = "YOUR_CLIENT_SECRET"  # Replace with your Azure Client Secret
    TENTNT_ID = "YOUR_TENANT_ID"  # Replace with your Azure Tenant ID

    Ensure you replace YOUR_CLIENT_ID, YOUR_CLIENT_SECRET, and YOUR_TENANT_ID with your actual Azure credentials.

    Custom Domain Setup

    If you wish to use a custom domain, configure the callback.py script to handle forwarding requests to the authentication server. This script helps in managing OAuth callbacks through your custom domain setup.

Usage

    Start Authentication

    Run the authentication script to initiate the login process. This script starts a Flask API endpoint to handle authentication requests:

    bash

    python authserver.py

    Follow the on-screen instructions to complete the authentication process in your web browser.

    Obtain Tokens

    After successful authentication, tokens will be saved in ~/.config/pma-bridge/data/. These tokens can be used to access Minecraft services.

Custom Implementation Details

    Flask API Endpoint: The application features a Flask API endpoint that handles the OAuth flow initiation and token management, enabling automated requests and integration with other services.
    Custom Domain Integration: The callback.py script allows integration with a custom domain, forwarding OAuth requests to the authentication server for streamlined processing.
    Hard-Coded Values: The script uses hard-coded values for configuration, including ClientID, ClientSecret, and TenantID, which can be customized for your needs.

Future Improvements

    Device Code Flow Bridge: Plans to incorporate a device code flow to facilitate authentication on devices that lack a web browser or in scenarios where interactive login is impractical. This will enhance the tool's flexibility and usability, especially in environments where traditional OAuth flows are challenging.
    Client Integration: Future updates may include support for integrating with various client applications, simplifying the use of the authenticator across different platforms and workflows. This includes creating seamless integrations with Minecraft clients and other related tools.
    Enhanced Security Features: Additional security measures will be implemented to protect tokens and credentials, such as improved encryption and secure storage practices.
    Expanded Documentation and Support: Development of more comprehensive documentation and support resources to assist users in configuring and using the tool effectively.

Contributing

This project is under active development and is intended for personal use. Contributions are welcome for enhancements or improvements. Please fork the repository and submit a pull request for any changes.
License

This project is licensed under the MIT License. See the LICENSE file for details.
Contact

For questions or issues, please contact:

    Email: owen@owendobson.com
    GitHub: otdobson
