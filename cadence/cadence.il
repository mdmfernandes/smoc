;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Simulation related functions     ;;
;;  - Load the simulator            ;;
;;  - Update design variables       ;;
;;  - Run simulaions                ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
procedure( loadSimulator(filePath)
    load(filePath)
    ;; TODO
    msg = "loadSimulator_OK"
    
)

procedure( updateAndRun(filePath resultPath)
    load(filePath)

    ;; Set results file path
    setShellEnvVar(resultPath)

    runSimulation()
    ;; TODO
    msg = "updateAndRun_OK"
)

procedure( runSimulation()
    runPath = getShellEnvVar("SCRIPT_PATH")
    print(runPath)
    runFile = strcat(runPath "/run.ocn")
    load(runFile)
    ;; TODO
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Server related functions         ;;
;;  - Start python server           ;;
;;  - Handle server requests        ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;; Send data to server. First it sends the data size and then the message
;; 
;; @param {number} cid - Server handle
;; @param {string} msg - data to send
;;
procedure( sendData(cid msg)
    
    printf("[INFO] Sending message to server: %s\n" msg)
    ; First sends the size of the data to send
    ipcWriteProcess(cid sprintf(nil "%d\n" strlen(msg)))
    ; Then sends the data
    ipcWriteProcess(cid msg)
)

;; Handles requests from the server (through stdout)
;; 
;; @param {number} cid - Server handle
;; @param {string} request - Request received from the server
;;
procedure( requestHandler(cid request)
	let( (result resultStr)
        if( serverHasStarted <= 0 then
            if( request == "Python server has started!" then
                serverHasStarted = 1
                printf("[INFO] Cadence is connected to server!\n")
            else
                printf("[INFO] Waiting for server... Message: %s\n" request)
            )
        else    ; if server has started
            ; if the request is to call a function
            if( rexMatchp("(.*)" request) then
                ; The "errsetstring" evaluates the request and returns the result,
                ; if valid, or an error message. E.g. if the request is a function,
                ; it executes the function and returns the result.
                if( result = errsetstring(request 't) then
                    sprintf(resultStr "%L\n" car(result))
                else
                    sprintf(resultStr "%s\n" car(nthelem(5 errset.errset)))
                )
                sendData(cid resultStr)
            else
                printf("[INFOs] %s\n" request)
            )
        )
    )
)

;; Handles server errors (through the stderr)
;; 
;; @param {number} cid - Server handle
;; @param {string} errorMessage - Error message received from the server
;;
procedure( errorHandler(cid errorMessage)
	warn("%s\n" errorMessage)
)

;; Handles the server shutdown
;; 
;; @param {number} cid - Server handle
;; @param {number} exitStatus - Server exit status
;;
procedure( exitHandler(cid exitStatus)
	printf("Server has stopped with the exit code %d. I'm out!!!\n" exitStatus)
    hiRegTimer("exit()", 10)    ; exit Cadence
)

;; Starts the python server as child process for inter-process communication
;;
;; @param {string} serverPath - The server path
;;
procedure( startServer()
	printf("[INFO] Starting server process...\n")
    serverHasStarted = 0
	cid = ipcBeginProcess("./run_server.sh" "" 'requestHandler 'errorHandler 'exitHandler "")
    msg = "Python server has started!\n"
    ipcWriteProcess(cid sprintf(nil "%d\n" strlen(msg)))
	ipcWriteProcess(cid msg)
)

serverHasStarted = 0
; Starts the server
startServer()
