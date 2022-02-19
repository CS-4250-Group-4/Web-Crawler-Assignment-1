import crawler


def main():
    while(True):
        url = input('Enter URL of website (or to exit to end): \n')
        if(url == 'exit'):
            break
        else:
            crawler.crawl(url)


if __name__ == '__main__':
    main()
