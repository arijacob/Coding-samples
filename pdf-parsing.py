from pypdf import PdfReader
from difflib import SequenceMatcher

import csv

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Main function to parse pdf and create dataset
def main():
    csvfile = open('csv_file', 'w')  # Open new csv file
    headers = ['date', 'bill', 'name', 'party', 'county', 'vote', 'page']  # Create columns headers of dataset

    # Write the columns as headers
    c = csv.DictWriter(csvfile, fieldnames=headers)
    c.writeheader()

    # Use program to parse the pdf
    reader = PdfReader("pdf")
    page_number = 1  # page number you want to start on
    date = "No date found yet"  # initialize date

    # Parse document by page, splitting up each line.
    while page_number != 1616:
        page = reader.pages[page_number]  # Assign page number to variable
        text = page.extract_text().splitlines()  # Assign text to variable
        date = findDate(text, date)  # Assign date to variable
        page_number += 1  # Increment to next page

        # Begin search of line be line to get date, bill, and votes
        for i in range(len(text)):
            string = (text[i])[0:10]
            dstring = (text[i])[0:11]

            # When the line is the date of vote, assign correct date
            if dstring.lower() == "carson city" and i == 2:
                date = (text[i])[11:]
                date = date.strip()
            # Logic when the line is the start of a vote
            if similar(string.lower(), "roll call ") > .75 and (text[i])[0:11].lower() != "roll called" and (text[i])[0:
            12].lower() != "roll  called":

                # Error check to confirm this is actually start of vote
                if similar(string.lower(), "roll call ") != 1:
                    print("Page:", page_number, string.lower(), "= Roll call")

                # Get bill number/name
                bill = (text[i])[13:]
                # bill = bill[:len(bill) - 2]

                currentValues = makeDict(date, page_number, bill)  # Create variable for values we currently have (
                # Date of vote, page is occurs on, and the bill name/number)
                currentValues["lastLine"] = i + 1  # Part of error check for when vote goes over a page

                # Logic to find the number of votes and members who votes in each possible way
                if similar((text[i + 2])[0:4].lower(), "nays") > .6 or similar((text[i + 2])[0:5].lower(),
                                                                               "nays ") > .6:  # For Nay votes
                    nayline = i + 2
                    currentValues = handleName(text, currentValues, "Nays", nayline, page_number, bill)  # Call
                    # handleName function to get the members who voted Nay

                    # Error check that this is actually a Nay vote
                    if similar((text[i + 2])[0:4].lower(), "nays") != 1:
                        print("Page:", page_number, (text[i + 2])[0:4], "= Nays")
                # Part of error check to ensure this wasn't actually a line with the Nay votes
                else:
                    print((text[i + 2])[0:4].lower(), " Full Line: ", (text[i + 2]))
                    if (text[i + 2])[0:4].lower() == "majo":
                        print(text, page_number)
                # Search through lines after we know there was a vote to get other types of voting, besides Nays
                # Logic for Absent voting
                for j in range(3, 7):
                    if i + j < len(text) and (
                            similar(text[i + j][0:6].lower(), "absent") > .5 or similar(text[i + j][0:7].lower(),
                                                                                        "absent") > .5) and (
                            text[i + j][0:6].lower() != "senate") and (text[i + j][0:6].lower() != "sena t") and (
                            text[i + j][0:5].lower() != "senat") and (text[i + j][0:6].lower() != "jacobs") and (
                            text[i + j][0:6].lower() != "assemb"):
                        # Error check to make sure this is line with absent votes
                        if similar(text[i + j][0:6].lower(), "absent") != 1:
                            print("Page:", page_number, text[i + j][0:6].lower(), "= absent")

                        absentLine = i + j  # Index line with absent votes
                        currentValues = handleName(text, currentValues, "Absent", absentLine, page_number,
                                                   bill)  # Call
                        # handleName function to get the members who voted Absent
                # Logic for Not Voting
                for j in range(3, 7):
                    if i + j < len(text) and (
                            similar(text[i + j][0:10].lower(), "not voting") > .6 or similar(text[i + j][0:12].lower(),
                                                                                             "not voting  ") > .6):
                        #  Error check to make sure this is line with absent votes
                        if similar(text[i + j][0:10].lower(), "not voting") != 1:
                            print("Page:", page_number, text[i + j][0:10].lower(), "= not voting")

                        notvotingLine = i + j  # Index line with Not Voting votes
                        currentValues = handleName(text, currentValues, "Not Voting", notvotingLine, page_number,
                                            bill)  # Call handleName function to get the members who voted Not Voting

                # Logic for excused voting
                for j in range(3, 7):
                    if i + j < len(text) and similar(text[i + j][0:7].lower(), "excused") > .6:  # Find excused votes
                        excusedLine = i + j  # Index line with excused votes
                        currentValues = handleName(text, currentValues, "Excused", excusedLine, page_number, bill)  #
                        # Call handleName function to get the members who voted Excused
                # Call function to add rows to csv, for this vote
                createCSV(currentValues, c)

                # Error check to make sure line after all the votes is what it should be
                if len(text) != currentValues["lastLine"] + 1:
                    print(text[currentValues["lastLine"] + 1], " Page number: ", page_number, "Bill:", bill)

                # Error check to make sure line it thinks is a vote is actually a vote
                if similar((text[i - 2])[0:10], "Roll call ") < .75 and (text[i])[0:11].lower() != "roll called" and (
                        similar((text[i])[0:4].lower(), "nays") > .6 or similar((text[i])[0:5].lower(), "nays ") > .6):
                    print("page:", page_number, text[i - 2])

                # Error check to make sure line it thinks is a vote is actually a vote
                if ((text[i])[0:4]).lower() == "yeas" and similar(((text[i - 1])[0:10]).lower(), "roll call ") < .7:
                    print("Incorrectly parsed Roll call. Page:", page_number, "  Bill:", (text[i - 1])[13:])
                if (text[i - 2])[0:10] != "roll call " and similar((text[i])[0:4].lower(), "nays") > .6 or similar(
                        (text[i])[0:5].lower(), "nays ") > .6:
                    print("Missed a Roll call:", page_number, text[i - 2])

    csvfile.close()  # Close CSV file when dataset is finished generating


# Function to create and fill CSV
def createCSV(lastname, c):
    namesList = []
    for name, value in lastname.items():
        namesList.append(value)
    c.writerows(namesList)

# Function to mark how members voted on a specific bill
def handleName(text, lastname, voteType, voteLine, page_number, bill):
    # Declare variables
    actualVote = ""
    substring = ""
    whileLoopNum = ""
    idx = ""

    # Logic to determine what vote we are marking members for.
    if voteType == "Nays":  # To mark Nay votes
        whileLoopNum = voteLine + 5
        idx = voteLine
        actualVote = "Nay"
        substring = "nays"
    if voteType == "Absent":  # To mark Absent votes
        whileLoopNum = voteLine + 5
        idx = voteLine
        actualVote = "Absent"
        substring = "absent"
    if voteType == "Not Voting":  # To mark Not voting
        whileLoopNum = voteLine + 5
        idx = voteLine
        actualVote = "Not Voting"
        substring = "notvoting"
    if voteType == "Excused":  # To mark Excused
        whileLoopNum = voteLine + 5
        idx = voteLine
        actualVote = "Excused"
        substring = "excused"
    # Error check if line before string equals last line of previous string
    if (idx - 1) != lastname["lastLine"]:
        # print(idx - 1, "=/=", lastname["lastLine"])
        print(page_number, "Bill: ", bill)
    voteNames = ""

    # Creates a string that contains the numbers of members voting this way and their names way by scanning lines
    # until "."
    while idx != whileLoopNum and idx != len(text):
        voteNames = voteNames + text[idx]
        if "." not in voteNames:
            idx = idx + 1
            continue
        else:
            # lastname["lastLine"] = idx
            break
    # Clean the string of vote names to replace extraneous characters.
    voteNames = voteNames.replace(" ", "")
    voteNames = voteNames.replace("-", "")
    voteNames = voteNames.replace(":", "")
    voteNames = voteNames.replace(",", "")
    number = voteNames[-5:-1]

    # Logic to count how many members voted in this specific type of way.

    if similar(number, "None") > .7:  # When no members voted this way
        naycount = 0

    elif number[-2].isdigit() is False and number[-1].isdigit() is True:  # When 2 through 9  members voted this way
        naycount = number[-1]
        voteNames = voteNames.replace(naycount, "")
        naycount = int(naycount)

    elif number[-2].isdigit() is True and number[-1].isdigit() is True:  # When greater than 9 members voted this way
        naycount = number[-2:]
        voteNames = voteNames.replace(naycount, "")
        naycount = int(naycount)

    else:  # When one member voted this way
        naycount = 1

    # Declare variables
    countNames = 0
    voteNames = voteNames.lower()
    # Logic to mark the specific members as voting this way
    for name, value in lastname.items():
        if name.lower() in voteNames:
            countNames += 1
            value["vote"] = actualVote
            voteNames = voteNames.replace(name.lower(), "")

    # Cleaning the vote names to do error check
    voteNames = voteNames.replace(substring, "")
    voteNames = voteNames.replace("mr.", "")

    # Error check to see if the number of votes is equal to the number of names
    numMissing = (naycount - countNames)

    # Check to see if there is 1 missing member it didn't register
    if numMissing == 1:
        voteNames = voteNames.replace(".", "")
        countForLoop = 0

        # Use "similar" function to capture more names that OCR didn't register
        for name, value in lastname.items():
            if similar(name, voteNames) > .6:
                # print(name, " = ", voteNames, page_number, bill)
                value["vote"] = actualVote
                countForLoop += 1
                break
            countForLoop += 1
            # Broad error check if after similar function still unable to register names
            if countForLoop == 20:
                print("Error finding name match: ", voteNames, "page:", page_number, "Bill: ", value["bill"])
    # Error check if there is more than one name missing
    elif numMissing > 1:
        print("More than 1 names failed to parse, remaining names: ", numMissing, " Names: ", voteNames, " Bill: ",
              (lastname["May"])["bill"], " Vote: ", voteType, "page:", page_number)

    return lastname


# Function to capture and assign date
def findDate(text, date):
    if text[2] is None:  # When there is no date
        return date
    dstring = (text[2])[0:12]  # Edit string to just capture the date
    if dstring.lower() == "carson  city":  # Fixed date, if OCR parsed incorrectly
        date = (text[2])[12:]
        date = date.strip()
    return date

# Make Dictionary that has legislator info in preparation to create each row
def makeDict(date, page, bill):
    lastname = {
        "Thomas": {"date": date, "bill": bill, "name": "Alan H. Glover", "party": "R", "county": "Carson City",
                   "vote": "Yea",
                   "page": page},
        "Kovacs": {"date": date, "bill": bill, "name": "Edward J. Kovacs", "party": "R", "county": "Clark No. 1",
                   "vote": "Yea",
                   "page": page},
        "DuBois": {"date": date, "bill": bill, "name": "John B. DuBois", "party": "D", "county": "Clark No. 2",
                   "vote": "Yea",
                   "page": page},
        "Bremner": {"date": date, "bill": bill, "name": "Roger Bremner", "party": "D", "county": "Clark No. 3",
                    "vote": "Yea",
                    "page": page},
        "Malone": {"date": date, "bill": bill, "name": "Mike Malone", "party": "D", "county": "Clark No. 4",
                   "vote": "Yea",
                   "page": page},
        "Brady": {"date": date, "bill": bill, "name": "William D. Brady", "party": "D", "county": "Clark No. 5",
                  "vote": "Yea",
                  "page": page},
        "Joerg": {"date": date, "bill": bill, "name": "Charles W. Joerg", "party": "R", "county": "Carson City",
                  "vote": "Yea",
                  "page": page},
        "Chaney": {"date": date, "bill": bill, "name": "Lonie Chaney", "party": "D", "county": "Clark No. 7",
                   "vote": "Yea",
                   "page": page},
        "Collins": {"date": date, "bill": bill, "name": "Gene Collins", "party": "D", "county": "Clark No. 6",
                    "vote": "Yea",
                    "page": page},
        "Zimmer": {"date": date, "bill": bill, "name": "Barbara Zimmer", "party": "R", "county": "Clark No. 8",
                   "vote": "Yea",
                   "page": page},
        "Speaker": {"date": date, "bill": bill, "name": "John M. Vergiels", "party": "R", "county": "Clark No. 10",
                    "vote": "Yea",
                    "page": page},
        "Banner": {"date": date, "bill": bill, "name": "James J. Banner", "party": "R", "county": "Clark No. 11",
                   "vote": "Yea",
                   "page": page},
        "Schofield": {"date": date, "bill": bill, "name": "James W. Schofield", "party": "D", "county": "Clark No. 12",
                      "vote": "Yea",
                      "page": page},
        "Coffin": {"date": date, "bill": bill, "name": "Bob Coffin", "party": "D", "county": "Clark No. 9",
                   "vote": "Yea",
                   "page": page},
        "Stewart": {"date": date, "bill": bill, "name": "Janson F. Stewart", "party": "D", "county": "Clark No. 14",
                    "vote": "Yea",
                    "page": page},
        "Berkley": {"date": date, "bill": bill, "name": "Shelley L. Berkley", "party": "D", "county": "Clark No. 13",
                    "vote": "Yea",
                    "page": page},
        "Ham": {"date": date, "bill": bill, "name": "Jane F. Ham", "party": "R", "county": "Clark No. 16",
                "vote": "Yea",
                "page": page},
        "Price": {"date": date, "bill": bill, "name": "Robert E. Price", "party": "D", "county": "Clark No. 17",
                  "vote": "Yea",
                  "page": page},
        "Sedway": {"date": date, "bill": bill, "name": "Marvin M. Sedway", "party": "D", "county": "Clark No. 15",
                   "vote": "Yea",
                   "page": page},
        "May": {"date": date, "bill": bill, "name": "Paul W. May", "party": "R", "county": "Clark No. 19",
                "vote": "Yea",
                "page": page},
        "Craddock": {"date": date, "bill": bill, "name": "Robert G. Craddock", "party": "D", "county": "Clark No. 20",
                     "vote": "Yea",
                     "page": page},
        "Thompson": {"date": date, "bill": bill, "name": "Danny L. Thompson", "party": "R", "county": "Clark No. 21",
                     "vote": "Yea",
                     "page": page},
        "Jeffrey": {"date": date, "bill": bill, "name": "John E. Jeffrey", "party": "D", "county": "Clark No. 22",
                    "vote": "Yea",
                    "page": page},
        "Bergevin": {"date": date, "bill": bill, "name": "Louis W. Bergevin", "party": "D", "county": "Douglas",
                     "vote": "Yea",
                     "page": page},
        "Fay": {"date": date, "bill": bill, "name": "Robert W. Fay", "party": "D", "county": "Clark No. 18",
                "vote": "Yea",
                "page": page},
        "Redelsperger": {"date": date, "bill": bill, "name": "Kenneth K. Redelsperger", "party": "R",
                         "county": "Esmeralda-Mineral-Nye",
                         "vote": "Yea",
                         "page": page},
        "Marvel": {"date": date, "bill": bill, "name": "John W. Marvel", "party": "D",
                   "county": "Eureka-Humboldt-Lander-Carlin Township",
                   "vote": "Yea",
                   "page": page},
        "Francis": {"date": date, "bill": bill, "name": "Steven C. Francis", "party": "R", "county": "Clark No. 41",
                    "vote": "Yea",
                    "page": page},
        "Dini": {"date": date, "bill": bill, "name": "Joseph E. Dini", "party": "R", "county": "Lyon-Storey-Churchill",
                 "vote": "Yea",
                 "page": page},
        "Perry": {"date": date, "bill": bill, "name": "Charles C. Perry", "party": "D", "county": "Clark No. 42",
                  "vote": "Yea",
                  "page": page},
        "Nicholas": {"date": date, "bill": bill, "name": "David D. Nicholas", "party": "R", "county": "Washoe No. 23",
                     "vote": "Yea",
                     "page": page},
        "Beyer": {"date": date, "bill": bill, "name": "Erik Beyer", "party": "R", "county": "Washoe No. 24",
                  "vote": "Yea",
                  "page": page},
        "Bilyeu": {"date": date, "bill": bill, "name": "Byron Bilyeu", "party": "R", "county": "Elko-Eureka",
                   "vote": "Yea",
                   "page": page},
        "Kerns": {"date": date, "bill": bill, "name": "Bob L. Kerns", "party": "R", "county": "Washoe No. 25",
                  "vote": "Yea",
                  "page": page},
        "Humke": {"date": date, "bill": bill, "name": "David E. Humke", "party": "R", "county": "Washoe No. 26",
                  "vote": "Yea",
                  "page": page},
        "Bogaert": {"date": date, "bill": bill, "name": "Bruce R. Bogaert", "party": "R", "county": "Washoe No. 27",
                    "vote": "Yea",
                    "page": page},
        "Swain": {"date": date, "bill": bill, "name": "Courtenary C. Swain", "party": "D", "county": "Washoe No. 28",
                  "vote": "Yea",
                  "page": page},
        "Bourne": {"date": date, "bill": bill, "name": "Charles G. Bourne", "party": "D", "county": "Washoe No. 29",
                   "vote": "Yea",
                   "page": page},
        "Sader": {"date": date, "bill": bill, "name": "Robert M. Sader", "party": "R", "county": "Washoe No. 32",
                  "vote": "Yea",
                  "page": page},
        "Stone": {"date": date, "bill": bill, "name": "James A. Stone", "party": "R", "county": "Washoe No. 30",
                  "vote": "Yea",
                  "page": page},
        "Nevin": {"date": date, "bill": bill, "name": "Leonard V. Nevin", "party": "D", "county": "Washoe No. 31",
                  "vote": "Yea",
                  "page": page},
        "Getto": {"date": date, "bill": bill, "name": "Virgil M. Getto", "party": "R",
                  "county": "White Pine-Churchill-Eureka-Lander",
                  "vote": "Yea",
                  "page": page},
        # "lastLine": 0
    }
    return lastname

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
