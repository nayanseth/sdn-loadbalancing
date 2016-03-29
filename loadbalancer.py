#!/usr/bin/env python

import requests
import json
import unicodedata
from subprocess import Popen, PIPE
import time
from sys import exit

# Method To Get REST Data In JSON Format
def getResponse(url,choice):

	response = requests.get(url)

	if(response.ok):
		jData = json.loads(response.content)
		if(choice=="deviceInfo"):
			deviceInformation(jData)
		elif(choice=="findSwitchCluster"):
			switchCluster(jData)
		elif(choice=="findSwitchLinks"):
			findSwitchLinks(jData,switch[h2])
		elif(choice=="findSwitchRoute"):
			findSwitchRoute(jData,switchRoute)
		elif(choice=="linkTX"):
			linkTX(jData,portKey)

	else:
		response.raise_for_status()

# Parses JSON Data To Find Switch Connected To H4
def deviceInformation(data):
	global switch
	global deviceMAC
	global hostPorts
	switchDPID = ""
	for i in data:
		if(i['ipv4']):
			ip = i['ipv4'][0].encode('ascii','ignore')
			mac = i['mac'][0].encode('ascii','ignore')
			deviceMAC[ip] = mac
			for j in i['attachmentPoint']:
				for key in j:
					temp = key.encode('ascii','ignore')
					if(temp=="switchDPID"):
						switchDPID = j[key].encode('ascii','ignore')
						switch[ip] = switchDPID
					elif(temp=="port"):
						portNumber = j[key]
						switchShort = switchDPID.split(":")[7]
						hostPorts[ip+ "::" + switchShort] = str(portNumber)

# Parses JSON Data To Find Switch Connections To Switch 1
def switchCluster(data):
	for i in data['00:00:00:00:00:00:00:01']:
		temp = i.encode('ascii','ignore')
		global switchConnections
		switchConnections.append(temp)

# Finding Switch Links Of Common Switch Of H3, H4

def findSwitchLinks(data,s):
	global switchLinks
	global linkPorts
	links=[]
	for i in data:
		src = i['src-switch'].encode('ascii','ignore')
		dst = i['dst-switch'].encode('ascii','ignore')

		srcPort = str(i['src-port'])
		dstPort = str(i['dst-port'])

		srcTemp = src.split(":")[7]
		dstTemp = dst.split(":")[7]

		tempSrcToDst = srcTemp + "::" + dstTemp
		tempDstToSrc = dstTemp + "::" + srcTemp

		portSrcToDst = str(srcPort) + "::" + str(dstPort)
		portDstToSrc = str(dstPort) + "::" + str(srcPort)

		linkPorts[tempSrcToDst] = portSrcToDst
		linkPorts[tempDstToSrc] = portDstToSrc

		if (src==s):
			links.append(dst)
		elif (dst==s):
			links.append(src)
		else:
			continue

	switchID = s.split(":")[7]
	switchLinks[switchID]=links

# Finds The Path To A Switch

def findSwitchRoute(data,s):
	srcShortPathID = s.split(":")[7]
	dstShortPathID = switch[h1].split(":")[7]
	shortPathID = srcShortPathID + "::" + dstShortPathID
	temp = []
	for i in data:
		temp.append(i['switch'].encode('ascii','ignore'))

	del temp[0]
	del temp[len(temp)-1]
	path[shortPathID] = temp

# Computes Link TX

def linkTX(data,key):
	global cost
	port = linkPorts[key]
	port = port.split("::")[0]
	for i in data:
		if i['port']==port:
			cost = cost + (int)(i['bits-per-second-tx'])


# Method To Compute Link Cost

def getLinkCost():
	global portKey
	global cost

	for key in path:
		start = switch[h2]
		src = switch[h2]
		srcShortID = src.split(":")[7]
		mid = path[key][0].split(":")[7]
		for link in path[key]:
			temp = link.split(":")[7]

			if srcShortID==temp:
				continue
			else:
				portKey = srcShortID + "::" + temp
				stats = "http://localhost:8080/wm/statistics/bandwidth/" + src + "/0/json"
				getResponse(stats,"linkTX")
				srcShortID = temp
				src = link
		portKey = start.split(":")[7] + "::" + mid + "::" + switch[h1].split(":")[7]
		finalLinkTX[portKey] = cost
		cost = 0
		portKey = ""

def systemCommand(cmd):
	terminalProcess = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
	terminalOutput, stderr = terminalProcess.communicate()
	print "\n***", terminalOutput, "\n"

def flowRule(currentNode, flowCount, inPort, outPort, staticFlowURL):
	flow = {
		'switch':"00:00:00:00:00:00:00:" + currentNode,
	    "name":"flow" + str(flowCount),
	    "cookie":"0",
	    "priority":"32768",
	    "in_port":inPort,
		"eth_type": "0x0800",
		"ipv4_src": h2,
		"ipv4_dst": h1,
		"eth_src": deviceMAC[h2],
		"eth_dst": deviceMAC[h1],
	    "active":"true",
	    "actions":"output=" + outPort
	}

	jsonData = json.dumps(flow)

	cmd = "curl -X POST -d \'" + jsonData + "\' " + staticFlowURL

	systemCommand(cmd)

	flowCount = flowCount + 1

	flow = {
		'switch':"00:00:00:00:00:00:00:" + currentNode,
	    "name":"flow" + str(flowCount),
	    "cookie":"0",
	    "priority":"32768",
	    "in_port":outPort,
		"eth_type": "0x0800",
		"ipv4_src": h1,
		"ipv4_dst": h2,
		"eth_src": deviceMAC[h1],
		"eth_dst": deviceMAC[h2],
	    "active":"true",
	    "actions":"output=" + inPort
	}

	jsonData = json.dumps(flow)

	cmd = "curl -X POST -d \'" + jsonData + "\' " + staticFlowURL

	systemCommand(cmd)

def addFlow():
	print "KAAM CHALU HAI"

	# Deleting Flow
	#cmd = "curl -X DELETE -d \'{\"name\":\"flow1\"}\' http://127.0.0.1:8080/wm/staticflowpusher/json"
	#systemCommand(cmd)

	#cmd = "curl -X DELETE -d \'{\"name\":\"flow2\"}\' http://127.0.0.1:8080/wm/staticflowpusher/json"
	#systemCommand(cmd)

	flowCount = 1
	staticFlowURL = "http://127.0.0.1:8080/wm/staticflowpusher/json"

	shortestPath = min(finalLinkTX, key=finalLinkTX.get)
	print "\n\nShortest Path: ",shortestPath

	currentNode = shortestPath.split("::",1)[0]
	nextNode = shortestPath.split("::")[1]

	# Port Computation

	port = linkPorts[currentNode+"::"+nextNode]
	outPort = port.split("::")[0]
	inPort = hostPorts[h2+"::"+switch[h2].split(":")[7]]

	flowRule(currentNode,flowCount,inPort,outPort,staticFlowURL)

	flowCount = flowCount + 2

	pathKey = shortestPath.split("::",1)[1]
	bestPath = path[pathKey]
	previousNode = currentNode

	for currentNode in range(0,len(bestPath)):
		port = linkPorts[bestPath[currentNode].split(":")[7]+"::"+previousNode]
		inPort = port.split("::")[0]
		outPort = ""
		if(currentNode+1<len(bestPath) and bestPath[currentNode]==bestPath[currentNode+1]):
			currentNode = currentNode + 1
			continue
		elif(currentNode+1<len(bestPath)):
			port = linkPorts[bestPath[currentNode].split(":")[7]+"::"+bestPath[currentNode+1].split(":")[7]]
			outPort = port.split("::")[0]
		elif(bestPath[currentNode]==bestPath[-1]):
			outPort = str(hostPorts[h1+"::"+switch[h1].split(":")[7]])

		flowRule(bestPath[currentNode].split(":")[7],flowCount,str(inPort),str(outPort),staticFlowURL)
		flowCount = flowCount + 2
		previousNode = bestPath[currentNode].split(":")[7]

# Method To Perform Load Balancing
def loadbalance(s3,s4):
	# Perform Load Balancing Only If H3 and H4 Are Connected To Same Switch
	if s3==s4:

		# Finds The Switches To Which H3's and H4's Switch Is Connected
		linkURL = "http://localhost:8080/wm/topology/links/json"
		getResponse(linkURL,"findSwitchLinks")

		keys = switchLinks.keys()

		for i in keys:
			for link in switchLinks[i]:
				global path
				global switchRoute
				route = "http://localhost:8080/wm/topology/route/"+link+"/0/"+switch[h1]+"/0/json"
				switchRoute = link
				getResponse(route,"findSwitchRoute")

		getLinkCost()
		addFlow()
	else:
		return 0


# Main

while True:

	# Stores Info About H3 And H4's Switch
	switch = {}

	# Mac of H3 And H4
	deviceMAC = {}

	# Store Switch 1 Connections
	switchConnections=[]
	# Stores Switch Links To H3 and H4's Switch
	switchLinks = {}

	# Stores Host Switch Ports
	hostPorts = {}

	# Stores Switch To Switch Path
	path = {}
	# Stores Link Ports
	linkPorts = {}
	# Stores Final Link Rates
	finalLinkTX = {}
	# Store Port Key For Finding Link Rates
	portKey = ""
	# Stores Link Cost
	cost = 0

	# Stores H1 and H2 from user
	global h1,h2,h3

	h1 = ""
	h2 = ""

	try:

		print "Enter Host 1"
		h1 = str(input())
		print "\nEnter Host 2"
		h2 = str(input())
		print "\nEnter Host 3 (H2's Neighbour)"
		h3 = str(input())

		# Enables Statistics Like B/W, etc
		enableStats = "http://localhost:8080/wm/statistics/config/enable/json"
		requests.put(enableStats)

		# Device Info (Switch To Which The Device Is Connected & The MAC Address Of Each Device)
		deviceInfo = "http://localhost:8080/wm/device/"
		getResponse(deviceInfo,"deviceInfo")

		# Calls Method To Find Switch 1 Connections
		switch1Cluster = "http://localhost:8080/wm/topology/switchclusters/json"
		getResponse(switch1Cluster,"findSwitchCluster")

		# Load Balancing

		loadbalance(switch[h3],switch[h2])

		# -------------- PRINT --------------

		print "\n\n############ RESULT ############\n\n"

		# Print Switch To Which H4 is Connected
		print "Switch H4: ",switch[h3], "\tSwitchH3: ", switch[h2]

		print "\n\nSwitch H1: ", switch[h1]

		# IP & MAC
		print "\nIP & MAC\n\n", deviceMAC

		# Host Switch Ports
		print "\nHost::Switch Ports\n\n", hostPorts

		# Print Connections to Switch 1
		print "\nSwitch 1 Connections\n\n", switchConnections

		# Print H3 And H4's Switch's Links
		print "\nH3 & H4 Switch Links\n\n", switchLinks

		# Link Ports
		print "\nLink Ports (SRC::DST - SRC PORT::DST PORT)\n\n", linkPorts

		# Alternate Paths
		print "\nPaths (SRC TO DST)\n\n",path

		# Final Link Cost
		print "\nFinal Link Cost (First To Second Switch)\n\n",finalLinkTX

		print "\n\n#######################################\n\n"

		time.sleep(60)

	except KeyboardInterrupt:
		break
		exit()
