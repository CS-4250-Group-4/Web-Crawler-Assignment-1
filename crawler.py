from typing import Counter
import requests, time
from bs4 import BeautifulSoup
from asyncio.windows_events import NULL
import csv


word_count = {}
def main():
    debug = True
    depth = 0
    maxDepth = 200
    visited = []
    #Prompt user for seed URL (hardcoded for now)
    #Check robots.txt for any restricted pages
    #Add url to the queue
    queue = []
    #seed = input("Seed URL: ")

    #Seeds
        #https://www.cpp.edu/index.shtml
        #https://ur.medeqipexp.com/ or https://ameblo.jp/ 
        #https://www.japscan.ws/ 
    seed = "https://www.cpp.edu/index.shtml"
    #seed = "https://ur.medeqipexp.com/"
    #seed = "https://ameblo.jp/"
    #seed = "https://www.japscan.ws/"
    domain = seed.split("/")[2]
    queue.append(seed)
    

    while((depth < maxDepth) or (len(queue) == 0)):
        depth += 1
        #Every 20 pages print show the depth in the console
        if(depth%20 == 0):
            print("depth: " + str(depth))
            #Every 100 pages show the size of the queue
            if(depth%100 == 0):
                print("Queue length: " + str(len(queue)))
        current_url = queue.pop(0)
        if(debug):
            print("requesting: " + current_url)
        visited.append(current_url)
        page = requests.get(current_url)

        #Count word for each url that is going to be visited
        start_wordcount(page)

        #time.sleep(.01)
        soup = BeautifulSoup(page.text, 'html.parser')
        outlinks = soup.find_all("a", href=True)
        #call split on link for # and only check first half
        #ex https://docs.python-requests.org/en/latest/#the-contributor-guide
        #ignore #the-contributor-guide and just go to https://docs.python-requests.org/en/latest/
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
                if((newLink not in visited) and (newLink not in queue)):
                    queue.append(newLink)
    
    #Get top 100 words with count and write to .csv file
    counter = Counter(word_count)
    most_frequent = counter.most_common(100)    
    save_wordcount_csv(most_frequent)
    word_count.clear()

    if (debug):
        for link in queue:
            print(link)
        print("\n\nVISITED\n")
        for link in visited:
            print(link)
            #Sort using Counter
        print()
        print("Queue length: " + str(len(queue)) + "\tVisited length: " + str(len(visited)))

def save_wordcount_csv(most_frequent):
    fields = ['Word', 'Count']
    most_frequent.insert(0, fields)
    filename = "wordCount.csv"

    # writing to csv file
    with open(filename, 'w', ) as csvfile:
        csvwriter = csv.writer(csvfile, lineterminator='\n')
        csvwriter.writerows(most_frequent)

def start_wordcount(url):
    #Create empty list for words that need to be cleaned
    word_list = []
    page = url
    soup = BeautifulSoup(page.text, 'html.parser')

    #Get text from the page
    for each_text in soup.findAll(text=True):
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

#Main loop
    #Get url from queue
    #Requests get url
        #handle any errors 404, etc.
    #Find <a> tags
        #check same domain, check depth limit, allowed in robots.txt
    #Add links to queue

main()
