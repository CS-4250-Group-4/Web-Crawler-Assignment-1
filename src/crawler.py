import csv
import requests
import time
from bs4 import BeautifulSoup

report_info = []


def save_report_csv():
    fields = ['URL', 'Number of outlinks']
    report_info.insert(0, fields)
    filename = "report.csv"

    # writing to csv file
    with open(filename, 'w', ) as csvfile:
        csvwriter = csv.writer(csvfile, lineterminator='\n')
        csvwriter.writerows(report_info)


def main():
    debug = True
    depth = 0
    maxDepth = 100

    visited = []
    # Prompt user for seed URL (hardcoded for now)
    # Check robots.txt for any restricted pages
    # Add url to the queue
    queue = []
    #seed = input("Seed URL: ")
    seed = "https://www.japscan.ws/"
    domain = seed.split("/")[2]
    queue.append(seed)
    report = {}

    while((depth < maxDepth) or (len(queue) == 0)):
        depth += 1
        if(depth % 20 == 0):
            print("depth: " + str(depth))
        currentUrl = queue.pop(0)
        if(debug):
            print("requesting: " + currentUrl)
        visited.append(currentUrl)
        page = requests.get(currentUrl)
        # time.sleep(.01)
        soup = BeautifulSoup(page.text, 'html.parser')
        outlinks = soup.find_all("a", href=True)
        # call split on link for # and only check first half
        # ex https://docs.python-requests.org/en/latest/#the-contributor-guide
        # ignore #the-contributor-guide and just go to https://docs.python-requests.org/en/latest/
        num_outLinks = 0
        for tag in outlinks:
            link = tag["href"]
            if link[0] == "#":
                #print("skipping " + link["href"])
                pass
            # ex of split: link.split("/") = ['https:', '', 'www.cpp.edu', 'index.shtml']
            elif link[0:4] == "http":
                if(domain == link.split("/")[2]):
                    #print("adding " + link["href"])
                    if((link not in visited) and (link not in queue)):
                        queue.append(link)
                        num_outLinks += 1
            else:
                #print("appending then adding " + link["href"])
                if(link.split(":")[0] == "mailto"):
                    # Skip any links that are just email addresses
                    continue
                # Link in this case is not a direct link, looks something like this /blog_portal/category/fashion/ranking/
                # domain would just be ameblo.jp
                newLink = "https://" + domain + link
                if((newLink not in visited) and (newLink not in queue)):
                    queue.append(newLink)
                    num_outLinks += 1
        report_info.append([currentUrl, num_outLinks])

    if (debug):
        for link in queue:
            print(link)
        print("\n\nVISITED\n")
        for link in visited:
            print(link)
        print()
        print("Queue length: " + str(len(queue)) +
              "\tVisited length: " + str(len(visited)))

    save_report_csv()
    # Main loop
    # Get url from queue
    # Requests get url
    # handle any errors 404, etc.
    #Find <a> tags
    # check same domain, check depth limit, allowed in robots.txt
    # Add links to queue


main()
