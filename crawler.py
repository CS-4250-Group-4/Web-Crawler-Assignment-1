import requests, time
from bs4 import BeautifulSoup

def main():
    debug = True
    depth = 0
    maxDepth = 100
    
    visited = []
    #Prompt user for seed URL (hardcoded for now)
    #Check robots.txt for any restricted pages
    #Add url to the queue
    queue = []
    #seed = input("Seed URL: ")
    seed = "https://www.cpp.edu/index.shtml"
    domain = seed.split("/")[2]
    queue.append(seed)

    
    

    while((depth < maxDepth) or queue.empty()):
        depth += 1
        if(depth%20 == 0):
            print("depth: " + str(depth))
        currentUrl = queue.pop(0)
        if(debug):
            print("requesting: " + currentUrl)
        visited.append(currentUrl)
        page = requests.get(currentUrl)
        #time.sleep(.01)
        soup = BeautifulSoup(page.text, 'html.parser')
        outlinks = soup.find_all("a", href=True)
        #call split on link for # and only check first half
        #ex https://docs.python-requests.org/en/latest/#the-contributor-guide
        #ignore #the-contributor-guide and just go to https://docs.python-requests.org/en/latest/
        for tag in outlinks:
            link = tag["href"]
            if link[0] == "#":
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
                newLink = "https://" + domain + link
                if((newLink not in visited) and (newLink not in queue)):
                    queue.append(newLink)
    if (debug):
        for link in queue:
            print(link)
        print("\n\nVISITED\n")
        for link in visited:
            print(link)
        print()
        print("Queue length: " + str(len(queue)) + "\tVisited length: " + str(len(visited)))
                    
    #Main loop
        #Get url from queue
        #Requests get url
            #handle any errors 404, etc.
        #Find <a> tags
            #check same domain, check depth limit, allowed in robots.txt
        #Add links to queue




main()
