from modules import api
import threading


def main():
    print(api.accounts.accountNumbers())
    print(api.accounts.accounts())
    #You now have access to the api 
    #The tokens are stored here:
    #universe.tokens.accessToken
    #universe.tokens.refreshToken
    #tokens will not be automatically refreshed (yet) so you have 30 minutes before you need a new access key.



if __name__ == '__main__':
    print("Welcome to the unofficial Schwab api interface!\nGithub: https://github.com/tylerebowers/Schwab-API-Python")
    api.initialize()
    main()
