Owens Personal Game Authenticator (PMA) Bridge (for Minecraft)
Overview

Owens Personal Game Authenticator (PMA) Bridge is a custom implementation designed to facilitate Minecraft authentication using Microsoft’s OAuth 2.0 services. This tool is tailored for personal use and is not intended for commercial distribution.

Note: This project is currently in development and intended solely for personal use.
Features

    OAuth 2.0 Authentication: Utilizes Microsoft’s OAuth 2.0 for secure authentication.
    Custom Implementation: A tailored version of the mc-authn library.
    Token Management: Automates the retrieval and management of Minecraft authentication tokens.
    Flask API Endpoint: Includes a Flask API endpoint for managing authentication requests.
    Custom Domain Integration: Supports a custom domain for OAuth callback handling via callback.py.
    Device Code Flow Bridge: Allows authentication on devices without web browsers, enhancing usability in restricted environments.

Requirements

    Python 3.7 or higher
    mc-authn library (install via pip)
    Flask
    Microsoft Azure account for OAuth setup

Installation

    Clone the Repository

    bash

git clone https://github.com/yourusername/Owens-Personal-Game-Authenticator-PMA.git
cd Owens-Personal-Game-Authenticator-PMA

Install Dependencies

Ensure you have Python 3.7 or higher installed, then install the required packages:

bash

    pip install requests flask ruamel.yaml

Setup

    Configure Azure OAuth
        Sign in to the Azure Portal.
        Navigate to Azure Active Directory > App registrations > New registration.
        Create a new application and set Redirect URI to http://localhost:18275.
        Note down the Application (client) ID, Client Secret, and Directory (Tenant) ID.

    Update Configuration

    Edit server.py to replace the placeholders with your Azure credentials:

    python

    CLIENT_ID = "YOUR_CLIENT_ID"  # Replace with your Azure Client ID
    CLIENT_SECRET = "YOUR_CLIENT_SECRET"  # Replace with your Azure Client Secret
    TENANT_ID = "YOUR_TENANT_ID"  # Replace with your Azure Tenant ID

    Custom Domain Setup

    If using a custom domain, configure callback.py to handle OAuth callback requests.

Usage

    Start Authentication

    Run the following command to start the Flask API endpoint:

    bash

    python server.py

    Follow the on-screen instructions to complete the authentication process in your web browser or via the device code flow.

    Device Code Flow

    If authentication via a web browser is not possible, the Device Code Flow will allow you to authenticate using a device code. The application will provide instructions to enter the device code on a separate device with web access.

    Obtain Tokens

    After successful authentication, tokens will be saved in ~/.config/pma-bridge/data/. These tokens can be used to access Minecraft services.

Custom Implementation Details

    Flask API Endpoint: Manages OAuth flow initiation and token management.
    Custom Domain Integration: callback.py manages OAuth callbacks through a custom domain.
    Device Code Flow Bridge: Provides an alternative authentication method for devices lacking a web browser.

Future Improvements

    Client Integration: Potential support for various client applications.
    Enhanced Security Features: Improved encryption and secure storage practices.
    Expanded Documentation and Support: Comprehensive resources for configuring and using the tool.

Contributing

This project is under active development and is intended for personal use. Contributions for enhancements or improvements are welcome. Please fork the repository and submit a pull request for any changes.
License

This project is licensed under the MIT License. See the LICENSE file for details.
Contact

For questions or issues, please contact:

    Email: owen@owendobson.com
    GitHub: otdobson
