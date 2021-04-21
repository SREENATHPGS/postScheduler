source venv/bin/activate
#export FLASK_ENV=development
export FLASK_APP=scheduler

function killProcesses() {
    echo "Killing existing processes."

    if [ -e ./flask_server.pid ];then
        kill -9 $(cat ./flask_server.pid)
    fi

    if [ -e ./beats.pid ];then
        kill -9 $(cat ./beats.pid)
    fi

    if [ -e ./celery.pid ];then
        kill -9 $(cat ./celery.pid)
    fi

}

function startProcesses() {

    killProcesses

    echo "Starting flask server."
    nohup flask run & #1>> ./server_out.log 2>> ./server_err.log &
    echo $! > ./flask_server.pid

    echo "Starting celery beats."
    nohup celery -A scheduler.celery beat --schedule=./celerybeat-schedule --loglevel=INFO 1>> ./beats_out.log 2>> ./beats_err.log &
    echo $! > ./beats.pid

    echo "Starting celery worker."
    nohup celery -A celery_worker.celery worker --loglevel=info --concurrency=1 1>> ./celery_out.log 2>> ./celery_err.log &
    echo $! > ./celery.pid

}


function show_help() {
    cat << EOF
        Usage: 
            --start or -s - start processe.
            --kill  or -k - kill processes.
            --help  or -h - display this message.
    
        Report bugs to: 
            sreenath@shiftbytes.co.in
EOF
}


while :; do
    case $1 in
        -h|-\?|--help)
            show_help    # Display a usage synopsis.
            exit
            ;;
        -k|--kill)       # Takes an option argument; ensure it has been specified.
            echo "Killing processes."
            killProcesses
	    break
            shift
            ;;
        -s|--start)       # Takes an option argument; ensure it has been specified.
            echo "Starting processes."
            startProcesses
	    break
            shift
            ;;
        # --file=?*)
        #     file=${1#*=} # Delete everything up to "=" and assign the remainder.
        #     ;;
        # --file=)         # Handle the case of an empty --file=
        #     die 'ERROR: "--file" requires a non-empty option argument.'
        #     ;;
        # -v|--verbose)
        #     verbose=$((verbose + 1))  # Each -v adds 1 to verbosity.
        #     ;;
        --)              # End of all options.
            shift
            break
            ;;
        -?*)
            printf 'WARN: Unknown option (ignored): %s\n' "$1" >&2
            ;;
        *)               # Default case: No more options, so break out of the loop.
            break
    esac

    shift
done
