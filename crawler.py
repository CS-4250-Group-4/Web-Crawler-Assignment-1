from itertools import count
import requests, time, csv, os
from bs4 import BeautifulSoup
from typing import Counter
from asyncio.windows_events import NULL

#Whether or not to download each page visited
download = True
#

report_info = []
disallowed_url_arr = []
seed_count = 0
word_count = {}

#Check if the repository folder exists, if it doesnt make it
savePath = os.path.dirname(os.path.abspath(__file__)) + "\\repository\\"
if not os.path.exists(savePath):
    os.makedirs(savePath)
    
session = requests.Session()

def crawl(seed, count_seed):
    debug = False
    depth = 0
    maxDepth = 500
    visited = []
    
    #Check robots.txt for any restricted pages
    #Add url to the queue
    queue = []

    #Seeds
        #https://www.cpp.edu/index.shtml
        #https://ur.medeqipexp.com/
        #https://www.japscan.ws/ 

    domain = seed.split("/")[2]
    queue.append(seed)

    session.headers.update({'Host': domain,
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Connection': 'keep-alive',
                            'Pragma': 'no-cache',
                            'Cache-Control': 'no-cache'})

    while((depth < maxDepth) or (len(queue) == 0)):
        depth += 1
        num_outLinks = 0
        currentUrl = queue.pop(0)

        if depth == 1:
            get_html = requests.get(currentUrl).content
            soup_lang = BeautifulSoup(get_html, 'html.parser')
            print("Language is: " + soup_lang.html["lang"])


        #Every 20 pages print show the depth in the console
        if(depth%20 == 0):
            print("depth: " + str(depth) + "/" + str(maxDepth))
            #Every 100 pages show the size of the queue
            if(depth%100 == 0):
                print("Queue length: " + str(len(queue)))
        
        if(debug):
            print("requesting: " + currentUrl)
        visited.append(currentUrl)

        try:
            #get the current page's html
            page = session.get(currentUrl, timeout=5)
            if download:
                #save the current page's html to the repositroy folder
                completePath = os.path.normpath(savePath + seed.split(":")[1] + "\\" + str(depth) + ".html")
                with open(completePath, 'w', encoding="utf-8") as file:
                    file.write(page.text)
                
        except requests.exceptions.Timeout:
            num_try = 0
            while(num_try < 5):
                time.sleep(5)
                page = session.get(currentUrl, timeout=25)
                if(page is not NULL):
                    break
                num_try += 1
        except requests.exceptions.TooManyRedirects:
            print('Bad url')
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        #Count word for each url that is going to be visited
        start_wordcount(page)

        #time.sleep(.01)
        soup = BeautifulSoup(page.text, 'html.parser')
        outlinks = soup.find_all("a", href=True)

        # call split on link for # and only check first half
        # ex https://docs.python-requests.org/en/latest/#the-contributor-guide
        # ignore #the-contributor-guide and just go to https://docs.python-requests.org/en/latest/
        
        for tag in outlinks:
            link = tag["href"]
            #if the tag doesnt have an href skip it
            if not link:
                pass
            #If the tag just has a comment instead of an actual link skip it
            elif link[0] == "#":
                #print("skipping " + link["href"])
                pass
            #ex of split: link.split("/") = ['https:', '', 'www.cpp.edu', 'index.shtml']
            elif link[0:4] == "http":
                num_outLinks += 1
                if(domain == link.split("/")[2]):
                    #print("adding " + link["href"])
                    if((link not in visited) and (link not in queue)):
                        queue.append(link)
            else:
                #print("appending then adding " + link["href"])
                if(link.split(":")[0] == "mailto"):
                    #Skip any links that are just email addresses
                    continue
                #Link in this case is not a direct link, looks something like this /blog_portal/category/fashion/ranking/
                #domain would just be ameblo.jp
                #sometimes need to add the starting /
                if(link[0] != "/"):
                    link = "/" + link
                newLink = "https://" + domain + link
                num_outLinks += 1
                if((newLink not in visited) and (newLink not in queue)):
                    queue.append(newLink)
        report_info.append([currentUrl, num_outLinks])
    
    #Get top 100 words with count and write to .csv file
    counter = Counter(word_count)
    most_frequent = counter.most_common(100)    
    save_wordcount_csv(most_frequent, count_seed)
    word_count.clear()

    if (debug):
        for link in queue:
            print(link)
        print("\n\nVISITED\n")
        for link in visited:
            print(link)
        print("\nQueue length: " + str(len(queue)) +
              "\tVisited length: " + str(len(visited)))

    save_report_csv(count_seed)

def save_wordcount_csv(most_frequent, count_seed):
    fields = ['Word', 'Count']
    most_frequent.insert(0, fields)
    filename = "words" + str(count_seed) + ".csv"

    #Writing to csv file
    with open(filename, 'w', encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile, lineterminator='\n')
        csvwriter.writerows(most_frequent)
    count_seed = count_seed + 1

def start_wordcount(url):
    #Create empty list for words that need to be cleaned
    word_list = []
    page = url
    soup = BeautifulSoup(page.text, 'html.parser')
    tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']
    #Get text from the page
    for each_text in soup.findAll(tags):
        content = each_text.text
        words = content.lower().split()
        #Append it to the wordlist and then clean the words of all symbols
        for each_word in words:
            word_list.append(each_word)
    rid_symbols(word_list)

def rid_symbols(word_list):
    final_word_list = []

    #Clean the words from any symbols
    for word in word_list:
        symbols = '!@#$%^&*()_-+={[}]|\;:"<>?/., '
        for i in range (0, len(symbols)):
            word = word.replace (symbols[i], '')
        if len(word) > 0:
            final_word_list.append(word)
    
    #Create a dictionary of all the words and start counting
    create_dictionary(final_word_list)

def create_dictionary(final_word_list):
    #Check if word is already in list, if so then add to its counter, if not then add word and begin counting
    for word in final_word_list:
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1

def init_robot_info(link):
    disallowed_url_arr.clear()
    url = link + 'robots.txt'
    robot_txt = session.get(url, timeout=5).text

    robot_txt_lines = robot_txt.split('\n')
    if(len(robot_txt_lines) == 0):
        return

    for line in robot_txt_lines:
        line_arr = line.split(' ')
        if(len(line_arr) > 1):
            if((line_arr[0] == 'Disallow:') and (line_arr[1] is not NULL)):
                disallowed_url_arr.append(line_arr[1])

def isAllowed(link):
    for text in disallowed_url_arr:
        if(text in link):
            return False
    return True

def save_report_csv(count_seed):
    global seed_count
    fields = ['URL', 'Number of outlinks']
    report_info.insert(0, fields)
    filename = "report" + str(count_seed) + ".csv"

    # writing to csv file
    with open(filename, 'w', ) as csvfile:
        csvwriter = csv.writer(csvfile, lineterminator='\n')
        csvwriter.writerows(report_info)
    report_info.clear()
    
def main():
    count_seed = 0
    while(True):
        seed = input('Enter seed URL (or \'done\' to end): \n')
        if(seed == 'done'):
            break
        else:
            crawlStart = time.time()
            count_seed = count_seed + 1
            #Create a new folder to hold this crawl's pages
            if download:
                #Check if the repository folder exists, if it doesnt make it
                #savePath = os.path.dirname(os.path.abspath(__file__)) + "\\repository\\Crawl" + str(count_seed) + "_" + seed
                print("seed: " + seed)
                savePath = os.path.dirname(os.path.abspath(__file__)) + "\\repository\\" + seed.split(":")[1]
                #If the folder doesn't exist, make it
                if not os.path.exists(savePath):
                    os.makedirs(savePath)
            crawl(seed, count_seed)
            crawlStop = time.time()
            print("Crawl took " + str(round(crawlStop - crawlStart, 4)) + " seconds")

if __name__ == '__main__':
    main()
