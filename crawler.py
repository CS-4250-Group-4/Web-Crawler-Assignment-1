import requests, time
from bs4 import BeautifulSoup

def main():
    debug = True
    depth = 0
    maxDepth = 500
    
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
                    if((link not in visited) and (link not in queue) and (link not in skipPages)):
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
                if((newLink not in visited) and (newLink not in queue) and (newLink not in skipPages)):
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
