# Schwab-API-Python 
This is an unofficial python program to access the Schwab api.    
You will need a Schwab developer account [here](https://beta-developer.schwab.com/).  
Join the [Discord group](https://discord.gg/m7SSjr9rs9).  
Also found on [PyPI](https://pypi.org/project/schwabdev/), install via `pip3 install schwabdev` 


## Quick setup
1. Create a new Schwab individual developer app with callback url "https://127.0.0.1" (case sensitive) and wait until the status is "Ready for use", note that "Approved - Pending" will not work.
2. Enable TOS (Thinkorswim) for your Schwab account, it is needed for orders and other api calls.
3. Python version 3.11 or higher is required.     
4. `pip3 install schwabdev requests websockets tk` (tkinter/tk may need to be installed differently)
5. Import the package `import schwabdev`
6. Create a client `client = schwabdev.Client('Your app key', 'Your app secret')`
7. Examples on how to use the client are in `tests/api_demo.py`

## What can this program do?
 - Authenticate and access the api 
 - Functions for all api functions (examples in `tests/api_demo.py`)
 - Auto "access token" updates (`client.update_tokens_auto()`)
 - Stream real-time data with customizable response handler (examples in `tests/stream_demo.py`)
 ### TBD 
 - Automatic refresh token updates. (Waiting for Schwab implementation)

## Notes

The schwabdev folder contains code for main operations:     
 - `api.py` contains functions relating to api calls, requests, and automatic token checker threads.
 - `stream.py` contains functions for streaming data from websockets.
 - `terminal.py` contains a program for making additional terminal windows and printing to the terminal with color.

## License (MIT)

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
