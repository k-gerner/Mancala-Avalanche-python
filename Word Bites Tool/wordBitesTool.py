# Kyle Gerner
# 3.12.2021
# Tool for Game Pigeon's 'Word Bites' puzzle game

from functools import cmp_to_key

# directional constants
HORIZONTAL = 'H'
VERTICAL = 'V'

# display mode constants
LIST = 0
DIAGRAM = 1

# globals
MAX_LENGTHS = {HORIZONTAL: 8, VERTICAL: 9} # max length of the words in each direction
horizPieces = [] # list of horizontal letter groupings
vertPieces = []  # list of vertical letter groupings
singleLetterPieces = [] # list of letter groupings made up of a single letter
englishWords = set() # LARGE set that will contain every possible word. Using set for O(1) lookup
wordStarts = set() # set that holds every valid part of every word from beginning to some point in the middle
validWordsOnly = set() # set of only the valid word strings (no tuple pairing)
validsWithDetails = set() # contains the words and direction in LIST mode, as well as index of list of pieces from piecesList in DIAGRAM mode
piecesList = [] # used to keep the list of pieces for a valid word (in DIAGRAM mode), since lists cannot be hashed in the set
DISPLAY_MODE = LIST # default display mode

# read in the user's input for the board pieces
def readInBoard():
	versions = [('Single Letter', singleLetterPieces), 
				('Horizontal', horizPieces), 
				('Vertical', vertPieces)]
	for pair in versions:
		if versions.index(pair) + 1 < len(versions):
			nextInput = "start inputting %s pieces." % versions[versions.index(pair) + 1][0]
		else :
			nextInput ="calculate best piece combinations."
		print("\nPlease enter each %s piece, with each piece on its own line.\n" % pair[0]+ 
			  "When you are done with %s pieces, press 'enter' on an empty line\n" % pair[0]+ 
			  "to %s\n" % nextInput)
		count = 1
		pieceStr = input("%s piece #1:\t" % pair[0]).lower().strip()
		while len(pieceStr) != 0:
			if not pieceStr.isalpha():
				print("Please make sure your input only contains letters.")
			else:
				if len(pieceStr) != 2 and pair[0] != 'Single Letter':
					print("All %s pieces should be 2 letters long." % pair[0])
				elif pair[0] == 'Single Letter' and len(pieceStr) > 1:
					print("You should be entering a single letter right now.")
				else:
					pair[1].append(pieceStr)
					count += 1
			pieceStr = input("%s piece #%d:\t" % (pair[0], count)).lower().strip()

# calls the recursive findWordsHelper method for each direction (H and V)
def findWords():
	findWordsHelper(singleLetterPieces, horizPieces, vertPieces, "", HORIZONTAL, [])
	findWordsHelper(singleLetterPieces, horizPieces, vertPieces, "", VERTICAL, [])

# find all the valid words for a board in a certain direction
def findWordsHelper(singles, horiz, vert, currStr, direction, currTuples):
	if len(currStr) > MAX_LENGTHS[direction]:
		# word too long
		return
	if len(currStr) >= 3 and currStr not in wordStarts:
		# not the beginning of a word so stop searching this expansion
		return
	if currStr in englishWords and currStr not in validWordsOnly:
		# valid word that hasn't been found yet
		validWordsOnly.add(currStr)
		if DISPLAY_MODE == DIAGRAM:
			piecesListIndex = len(piecesList)
			piecesList.append(currTuples)
			tup = currStr, direction, piecesListIndex
		else:
			tup = currStr, direction
		validsWithDetails.add(tup)
	for i in range(len(singles)):
		# copyTuples will keep track of the pieces for a word in DIAGRAM mode, is unnecessary in LIST mode
		if DISPLAY_MODE == DIAGRAM:
			copyTuples = currTuples.copy()
			copyTuples.append(singles[i])
		else:
			copyTuples = []
		findWordsHelper(singles[:i] + singles[i+1:], horiz, vert, currStr + singles[i], direction, copyTuples)
	for j in range(len(horiz)):
		if DISPLAY_MODE == DIAGRAM:
			copyTuples = currTuples.copy()
			copyTuples.append(horiz[j])
		else:
			copyTuples = []
		if direction == HORIZONTAL:
			findWordsHelper(singles, horiz[:j] + horiz[j+1:], vert, currStr + horiz[j], direction, copyTuples)
		else:
			for horizLetter in horiz[j]:
				findWordsHelper(singles, horiz[:j] + horiz[j+1:], vert, currStr + horizLetter, direction, copyTuples)
	for k in range(len(vert)):
		if DISPLAY_MODE == DIAGRAM:
			copyTuples = currTuples.copy()
			copyTuples.append(vert[k])
		else:
			copyTuples = []
		if direction == HORIZONTAL:
			for vertLetter in vert[k]:
				findWordsHelper(singles, horiz, vert[:k] + vert[k+1:], currStr + vertLetter, direction, copyTuples)
		else:
			findWordsHelper(singles, horiz, vert[:k] + vert[k+1:], currStr + vert[k], direction, copyTuples)

# for custom sorting of valid words; sorts longest to shortest, and alphabetically
def word_compare(a, b):
	if len(a[0]) < len(b[0]):
		return 1
	elif len(a[0]) == len(b[0]):
		if a[0] > b[0]: 
			return 1
		elif a[0] < b[0]:
			return -1
		return 0
	return -1

# print the valid words in whichever mode the user selected
def printOutput(words):
	count = 1
	print("\n%d word%s found.\n" % (len(words), '' if len(words) == 1 else 's'))
	if DISPLAY_MODE == LIST:
		print("   X  |   Word \t|  Direction\n" + 
			  "-------------------------------")
		cmd = ''
		while cmd != 'q':
			if cmd == 'a':
				while count <= len(words):
					dirSpacing = " "*5 + " "*(9-len(words[count - 1][0]))
					print("%d.\t%s%s(%s)" % (count, words[count - 1][0], dirSpacing, words[count - 1][1]))
					count += 1
				print()
				return
			for i in range(10):
				dirSpacing = " "*5 + " "*(9-len(words[count - 1][0]))
				print("%d.\t%s%s(%s)" % (count, words[count - 1][0], dirSpacing, words[count - 1][1]))
				count += 1
				if count - 1 == len(words):
					# if reached the end of the list
					print("\nNo more words. ", end='')
					return
			if count + 8 < len(words):
				grammar = "next 10 words"
			else:
				wordsLeft = len(words) - count + 1
				if wordsLeft > 1:
					grammar = "final %d words" % wordsLeft
				else:
					grammar = "final word"
			cmd = input("Press enter for %s, or 'q' to quit, or 'a' for all:\t" % grammar).strip()
	else:
		# DISPLAY_MODE = DIAGRAM
		# NOTE: This display mode was written to conform with the Game Pigeon Word Bites 
		# 		pieces standards, which means all pieces are either length 1 or 2
		wordNum = 1
		for wordItem in words:
			if wordNum > 1:
				# if not first time through
				if input("\nPress enter for next word, or 'q' to quit\t").strip() == 'q':
					break
			# create copies of the pieces lists because they will be edited in the next part
			singePiecesCopy, horizPiecesCopy, vertPiecesCopy = singleLetterPieces.copy(), horizPieces.copy(), vertPieces.copy()
			word, direction, pieces = wordItem[0], wordItem[1], piecesList[wordItem[2]]
			wordWithNumber = "%d:   %s" % (wordNum, word)
			print()
			if direction == HORIZONTAL:
				# if word is horizontal
				indexInWord = 0
				lineAbove, line, lineBelow = "\t", "\t", "\t"
				for piece in pieces:
					if piece in vertPiecesCopy:
						# if the piece is a vertical piece
						vertPiecesCopy.remove(piece)
						if piece.index(word[indexInWord]) == 0:
							# if top letter is in word
							above, cur, below = "  ", piece[0] + " ", piece[1] + " "
						else:
							# bottom letter in word
							above, cur, below = piece[0] + " ", piece[1] + " ", " "
						indexInWord += 1
					elif piece in horizPiecesCopy:
						# if the piece is a horizontal piece
						horizPiecesCopy.remove(piece)
						above, cur, below = "   ", piece + " ", "   "
						indexInWord += 2
					else:
						# piece is a single letter
						singePiecesCopy.remove(piece)
						above, cur, below = "  ", piece  + " ", "  "
						indexInWord += 1
					lineAbove += above
					line += cur 
					lineBelow += below
				afterWordTabs = "\t" * (3 - int(len(line)/8))
				print("%s\n%s%s%s\n%s\n" % (lineAbove, line, afterWordTabs, wordWithNumber,lineBelow))
			else:
				# if word is vertical
				indexInWord = 0
				lineLeft, line, lineRight = "", "", ""
				for piece in pieces:
					if piece in horizPiecesCopy:
						# if the piece is a horizonal piece
						horizPiecesCopy.remove(piece)
						if piece.index(word[indexInWord]) == 0:
							# if left letter is in word
							left, cur, right = " ", piece[0], piece[1]
						else:
							# right letter in word
							left, cur, right = piece[0], piece[1], " "
						indexInWord += 1
					elif piece in vertPiecesCopy:
						# if the piece is a vertical piece
						vertPiecesCopy.remove(piece)
						left, cur, right = "  ", piece, "  "
						indexInWord += 2
					else:
						# piece is a single letter
						singePiecesCopy.remove(piece)
						left, cur, right = " ", piece, " "
						indexInWord += 1
					lineLeft += left
					line += cur 
					lineRight += right
				verticalOutputs = rotateStringsToVertical(lineLeft, line, lineRight)
				indexOfFullWordOuptut = max(int(len(verticalOutputs) / 2) - 1, 1)
				count = 0
				for line in verticalOutputs:
					if count == indexOfFullWordOuptut:
						line += "\t\t\t%s" % wordWithNumber
					print("%s" % line) # 3\t
					count += 1
			wordNum += 1
		# print("this tuple list: %s" % str(piecesList[words[count-1][2]]))

# takes in 3 strings and 'rotates' them so that they print vertically
def rotateStringsToVertical(leftStr, middleStr, rightStr):
	horizStrings = []
	for i in range(len(leftStr)):
		horizStr = "\t%s %s %s" % (leftStr[i], middleStr[i], rightStr[i])
		horizStrings.append(horizStr)
	return horizStrings


# show the user further information about the different modes available for printing word list
def printModeInfo():
	print("------------------------------------------------------------\n" + 
		  "------------------------------------------------------------")
	print("There are two available display modes:\n")
	print("List Mode is one large list, where each word has its own row:\n")
	print("   X  |   Word 	|  Direction\n" + 
		  "-------------------------------\n" + 
		  "1:\tathetised\t(V)\n" + 
		  "2:\tbirthdays\t(V)\n" + 
		  "3:\tdiameters\t(H)\n" +
		  " .\t    .\t\t .\n"*3)
	print("Diagram Mode feeds the user 1 word at a time, and displays a\n" + 
		  "visual representation of how to arrange the board pieces:\n")
	print("\t  a l\n\t  t\n\to h\n\t  e\t\t1:   athetised\n\t  t\n\t  i n\n\t  s\n\t  e\n\t  d\n")
	print("Press enter for next word.")

# main method - fills english words sets and calls other functions
def main():
	global DISPLAY_MODE
	# initial setup
	print("Welcome to the Word Bites Game Pigeon Solver!")
	filename = 'letters9.txt'
	# filename = input("What word list file would you like as input?\t")
	try :
		inputFile = open(filename, 'r')
	except:
		print("\nCould not open the file. Please make sure %s is in the current directory, and run this file from inside the current directory.\n" % filename)
		exit(0)
	for word in inputFile:
		strippedWord = word.rstrip() # removes newline char
		if len(strippedWord) > 9: # max vertical length
			continue
		englishWords.add(strippedWord)
		# add each word start to the set of word starts
		for i in range(3, len(strippedWord) + 1):
			wordStarts.add(strippedWord[:i])
	inputFile.close()

	# display mode select
	modeSelect = input("\nUse Diagram Mode? 'y' for yes, 'i' for more info:\n").rstrip()
	while modeSelect == 'i':
		printModeInfo()
		modeSelect = input("\nUse Diagram Mode? 'y' for yes, 'i' for more info:\n").rstrip()
	if modeSelect == 'y':
		DISPLAY_MODE = DIAGRAM
		print("\nWords will be displayed in Diagram Mode.")
	else:
		print("\nWords will be displayed in List Mode.")

	# read in user input and use it to calculate best piece combinations
	readInBoard()
	word_cmp_key = cmp_to_key(word_compare)
	findWords()
	validWords = sorted(list(validsWithDetails), key=word_cmp_key)
	if len(validWords) == 0:
		print("There were no valid words for the board.")
		exit(0)
	printOutput(validWords)


if __name__ == '__main__':
	main()
