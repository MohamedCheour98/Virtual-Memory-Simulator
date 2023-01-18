import collections
import argparse

pageTable = [None] * 256
#An order dictionary is used instead of a regular dict in order to remember the order in which the page numbers are inserted.
translationLookasideBuffer = collections.OrderedDict()
memorySort = collections.OrderedDict()
backingStore = open("BACKING_STORE.bin", 'r')


def memSim():
    
    index = 0
    misses = 0
    hits = 0
    pageFaults = 0
    addressesList = []

    parser = argparse.ArgumentParser()
    parser.add_argument("ReferenceSequenceFile")
    parser.add_argument("FRAMES", nargs = "?", default = 256, type = frameCountParsing)
    parser.add_argument("PRA", nargs = "?", default = "FIFO", type = PageReplacementAlgorithm)
    
    args = parser.parse_args()
    referenceSequenceFile = args.ReferenceSequenceFile
    frameCount = args.FRAMES
    pra = args.PRA

    memory = [None] * frameCount

    with open(referenceSequenceFile, 'r') as inputFile:
        for line in inputFile:
            inputAddress = int(line.strip('\n'))
            addressesList.append(inputAddress)
        inputFile.close()

    for inputAddress in addressesList:
        #converting the address into a 16 bit binary address with leading zeros.
        binary = format(inputAddress, '016b') 
        
        #translating the page and offset numbers back to decimals. 
        pageNumber = int(binary[0:8], 2)
        offsetNumber = int(binary[8:], 2)
        frameNumber = TLBSearch(pageNumber)

        if frameNumber is None:            
            frameNumber = pageTableSearch(pageNumber)
            misses += 1

        else:
            hits += 1

        if frameNumber is None:
            backingStore.seek(pageNumber * 256)
            content = backingStore.read(256)
            oldContent = memory[index]
            
            if oldContent is not None:
                for page, frame in enumerate(pageTable):
                    if frame == index:
                        pageTable[page] = None

            memory[index] = content
            frameNumber = index
            pageTable[pageNumber] = index
            insert(pageNumber, index)
            pageFaults += 1
            index = next(index, pra, memory, frameCount)
        
        else:
            content = memory[frameNumber]

        if pra == "LRU":
            if frameNumber in memorySort:
                del memorySort[frameNumber]
            memorySort[frameNumber] = 0

        byte = ord(content[offsetNumber]) #returning te unicode of the data. 
        if byte > 127:
            byte = (256-byte) * (-1)

        print(str(inputAddress) + ", " + str(byte) + ", " + str(frameNumber) + ",\n" + ''.join(["%02X" % ord(data) for data in content]).strip())


    print("Number of Translated Addresses = {}".format(len(addressesList)))
    print("Page Faults = {} ".format(pageFaults))
    print("Page Fault Rate = %.3f" % (float(pageFaults) / float(len(addressesList))))
    print("TLB Hits = {}".format(hits))
    print("TLB Misses = {}".format(misses))
    print("TLB Hit Rate = %.3f" % (float(hits) / float(len(addressesList))))


    backingStore.close()

def frameCountParsing(var):
    
    frameCount = int(var)
    
    if frameCount < 1 or frameCount > 256:
        print("usage: prog2.py [-h] ReferenceSequenceFile [FRAMES] [PRA]\n"
            "error: %s is not a valid number for framesCount.\n"
            "Please enter a number between 1 and 256." % frameCount)
        exit(1)
    
    return frameCount


def PageReplacementAlgorithm(PRA):
    
    if PRA == "LRU" or PRA == "FIFO" or PRA == "OPT":
        return PRA
    
    else:
        print("usage: prog2.py [-h] ReferenceSequenceFile [FRAMES] [PRA]\n"
            "error: %s is not a valid PRA (Page Replacement Algorithm).\n"
            "Please enter 'FIFO', 'LRU', or 'OPT'." % PRA)
        exit(1)


def TLBSearch(pageNumber):
    
    if pageNumber in translationLookasideBuffer:
        frameNumber = translationLookasideBuffer[pageNumber]
        del translationLookasideBuffer[pageNumber]
        translationLookasideBuffer[pageNumber] = frameNumber
        
        return frameNumber
    
    else:
        return None


def pageTableSearch(pageNumber):
    
    frameNumber = pageTable[pageNumber]
    if frameNumber is not None:
        insert(pageNumber, frameNumber)
    
    return frameNumber


def insert(pageNumber, frameNumber):
    
    if len(translationLookasideBuffer) == 16:
        #setting last to False so that the first item is popped from the TLB 
        translationLookasideBuffer.popitem(last=False) 
    
    translationLookasideBuffer[pageNumber] = frameNumber


def next(index, pra, memory, frameCount):
    memEntry = 0
    for entry in memory:
        if entry is not None:
            memEntry += 1
    
    if pra == "FIFO" or memEntry < frameCount:
        return (index + 1) % frameCount
    
    elif pra == "LRU":
        leastUsed = memorySort.popitem(last=False)
        return leastUsed[0]

    elif pra == "OPT":
        OPTCache(frameCount) 

class InsignificantPage:
    def __init__(self, pageNumber, count, num):
        self.pageNumber = pageNumber
        self.num = num
        self.count = count
        
class OPTCache:
    
    def __init__(self, limit):
        self.limit = limit
        self.memCache = collections.OrderedDict()
        self.order = {}
        self.replaced = []
        
    def set(self, key, value):
        try:
            self.memCache.pop(key)
        except KeyError:
            if len(self.memCache) >= self.limit:
                self.pop()
        self.memCache[key] = value


    def get(self, key):
        try:
            value = self.memCache.pop(key)
            self.memCache[key] = value
            return value
        except KeyError:
            return None


    def prep(self, input_addresses):
        num = 0
        for address in input_addresses:
            pageNumber, offset = hide(address)
            try:
                x = self.order[pageNumber]
                self.order[pageNumber].count += 1
            except KeyError:
                x = InsignificantPage(pageNumber, 1, num)
                self.order[pageNumber] = x
            num += 1


    def pop(self):
        for x in self.replaced:
            y = self.memCache.get(x[0])
            if y is None:
                continue
            else:
                self.memCache.pop(x[0])


    def compute(self):
        for (i, v) in self.order.iteritems():
            self.replaced.append((v.page_number, v.count, v.num))
        self.replaced = sorted(self.replaced, key=lambda x: (x[1], -x[2]))

def hide(address):
    return (address >> 8), (address & 0xFF)


        

if __name__ == '__main__':
    memSim()