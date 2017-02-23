#/bin/sh
function log_info(){
    info=$*
    log_echo 'info' "$info" $log_file
}
function log_warn(){
    info=$*
    log_echo 'warn' "$info" $log_file
}
function log_err(){
    info=$*
    log_echo 'err' "$info" $log_file
    exit 1
}