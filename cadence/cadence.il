procedure( handler( cid data )
	
	;rescmp = strncmp(data "oc" 3)

	printf("-> %s\n" data)
	
	; send back the data plus current time
	currentTime = buildString(parseString(getCurrentTime()))
	;printf("Current time: %s\n" currentTime)
	ipcWriteProcess(cid sprintf(nil "%s\n" data))
	
	/*if((rescmp == 1) then
		file = substring(data 4 strlen(data))
		printf("\nfile: %s\n" file)
		load(file)
	)*/
)

handlerError = (lambda (cid data) printf("[INFO] %s\n" data))

handlerExit = (lambda (cid exitStatus) printf("\nServer has stoped with the exit code %d. I'm out!!!\n" exitStatus)  hiRegTimer("exit()", 50))

cmd = simplifyFilename("server.py")
printf("\n PATH: %s\n", cmd)

cid = ipcBeginProcess(cmd "" 'handler handlerError handlerExit)

ipcWriteProcess(cid "Server connected to Cadence\n")
