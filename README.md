# Schwab-API-Python 
This is an unofficial python program to access the Schwab api.    
You will need a Schwab developer account [here](https://beta-developer.schwab.com/).        
Join the [Discord group](https://discord.gg/m7SSjr9rs9)


## Quick setup
1. Create a new Schwab individual developer app with callback url "https://127.0.0.1" (case sensitive) and wait until the status is "Ready for use", note that "Approved - Pending" will not work.
2. Enable TOS (Thinkorswim) for your Schwab account, it is needed for orders and other api calls.
3. Python version 3.11 or higher is required.     
4. `pip3 install requests websockets python-dotenv tk`
5. Paste keys in the `.env` file specifically appKey and appSecret.
6. Start by running the main.py file.

## What can this program do?
 - Authenticate and access the api (`api.initialize()`)
 - Functions for all api functions (examples in `main.py`)
 - Auto "access token" updates (`api.updateTokensAutomatic()`)
 - Stream real-time data (`stream.startManual()`)
 - Automatically start/stop stream (`stream.startAutomatic()`)
 ### TBD 
 - Automatic refresh token updates. (Waiting for Schwab implementation)
 - Customizable stream response handler. (Waiting for Schwab implementation)


## Usage and Design
This python client makes working with the TD/Schwab api easier.    
The idea is to make an easy to understand, organized, and highly-automatic interface for the api.   
Below is a light documentation on how it works, python is pseudocode-esk so if you are confused just read the code and follow the functions. 

### Organization

The root of the wrapper:
 - `main.py` where the main program is run from, contains examples for you to get started with.
 - `.env` contains the app key and app secret, these need to be filled in.
 - `tokens.json` contains api tokens as well as dates for when they expire.

The modules folder contains code for main operations:     
 - `api.py` contains functions relating to api calls, requests, and automatic token checker threads.
 - `stream.py` contains functions for streaming data from websockets.
 - `terminal.py` contains a program for making additional terminal windows and printing to the terminal with color.

<!---
### Initialization
main.py initializes below main() in `if __name__ == '__main__':` each call is described below:
 1. `api.initialize()` # This calls a function that checks if the access or refresh token need to be re-authenticated. It also adds the tokens and expire times to variables in `universe.py`
 2. `main()` # This is where you put your code to be run.
-->
## License (MIT)

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
