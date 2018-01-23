;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Simulation related functions     ;;
;;  - Load the simulator            ;;
;;  - Update design variables       ;;
;;  - Run simulaions                ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(procedure loadSimulator()
    load("loadSim.ocn")
    ;; TODO
)

(procedure updateVariables()
    load("varsSim.ocn")
    ;; TODO
)

(procedure runSimulation()
    load("runSim.ocn")
    ;; TODO
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Server related functions         ;;
;;  - Start python server           ;;
;;  - Handling of server requests   ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

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
            printf("[INFO] Evaluating expression from server: %s\n" request)

            msg = "Enviando de volta para o cliente\n"

            ipcWriteProcess(cid sprintf(nil "%d\n" strlen(msg)))
            ipcWriteProcess(cid msg)


            ; The "errsetstring" evaluates the request and returns the result,
            ; if valid, or an error message. E.g. if the request is a function,
            ; it executes the function and returns the result.
            /*
            if( result = errsetstring(request 't) then
                ; VER ISTO!!
                sprintf(resultStr "%A\n" car(result))
            else
                sprintf(resultStr "%s\n" car(nthelem(5 errset.errset)))
            )
            printf("[INFO] Sending result to server: %s\n" resultStr)
            ; First sends the size of the data to send
            ipcWriteProcess(cid sprintf(nil "%d\n" strlen(resultStr)))
            ; Then sends the data
            ipcWriteProcess(cid resultStr)
            */
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
    hiRegTimer("exit()", 50)    ; exit Cadence
)

;; Starts the python server as child process for inter-process communication
;;
;; @param {string} serverPath - The server path
;;
procedure( startServer()
	printf("[INFO] Starting server process...\n")
    serverHasStarted = 0
	cid = ipcBeginProcess("bash run_server.sh" "" 'requestHandler 'errorHandler 'exitHandler "")
    msg = "Python server has started!\n"
    ipcWriteProcess(cid sprintf(nil "%d\n" strlen(msg)))
	ipcWriteProcess(cid msg)
)

serverHasStarted = 0
; Starts the server
startServer()
