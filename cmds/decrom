#!/bin/bash

DEXTRA=dextra
JADX=jadx
AOSP_FRAMWROKDIR=

function get_abs_path() {
    readlink -f $1 
}

function oat2smali() {
    local oat=$1
    local _outdir=$(basename $1)
    local outdir=${_outdir%.*}
    baksmali x -c boot.oat -d ${AOSP_FRAMWROKDIR} ${oat} -o ${outdir}
}

function smali2dex() {
    local smalidir=$1
    local outdex=${2:-classes.dex}
    smali a ${smalidir} -o ${outdex}
}

function oat2dex() {
    local oat=$1
    local _outdir=$(basename $1)
    local smalidir=${_outdir%.*}
    local outdex=${2:-classes.dex}
    echo "oat/odex -> smali"
    baksmali x -c boot.oat -d ${AOSP_FRAMWROKDIR} ${oat} -o ${smalidir}
    echo "smali -> dex"
    smali a ${smalidir} -o ${outdex}
    rm -rf ${smalidir}
}

function get_classesdex_in_oat() {
    local oat=$1
    dextra -l ${oat} 2> /dev/null | sed -n "s/Dex header.*.jar:\(classes.*.dex\)/\1/p"
}

function check_has_multidex() {
    local lists=$(find $1 -name "*.oat" -o -name "*.odex")
    for i in ${lists[*]}; do
        local out=$(get_classesdex_in_oat $i)
        if [ x"${out}" != x ]; then
            echo "$i has multi dexes!"
        fi
    done
}

function extract_dex_from_frameworks() {
    local oatdir=$(get_abs_path $1)
    local suffix=$2
    local lists=$(find ${oatdir} -name "*.${suffix}")
    for file in ${lists[*]}
    do
        echo "-----> $file"
        local base=$(basename "$file")
        local tmp=${base#boot-}
        local package=$(basename ${tmp%.*})
        oat2dex ${file} ${package}.dex
        echo "jadx: $dex -> to java"
        $JADX --show-bad-code ${package}.dex

        local lists_more=($(get_classesdex_in_oat ${file}))
        for more in ${lists_more[*]}
        do
            oat2dex ${file}/${more} ${package}-${more}
            echo "jadx: $dex -> to java"
            $JADX --show-bad-code ${package}-${more} -d ${package}
        done
    done
}

function extract_dex_from_frameworks_jars() {
    local framework_dir=$(get_abs_path $1)
    local lists=$(find ${framework_dir} -name "*.jar")
    for file in ${lists[*]}
    do
        echo "jadx: $file -> to java"
        $JADX --show-bad-code ${file}
    done
}

function decompile_framework() {
    local rom_dir=$(get_abs_path $1)
    mkdir -p framework
    HERE=$(pwd)
    cd framework
    extract_dex_from_frameworks ${rom_dir}/framework/arm64 oat
    extract_dex_from_frameworks ${rom_dir}/framework/oat/arm64 odex
    cd $HERE
}

function decompile_app() {
    local app_dir=$(get_abs_path $1)
    local app_name=$(basename ${app_dir})
    local subdir=arm64
    if [ ! -f ${app_dir}/oat/arm64/${app_name}.odex ]; then
        if [ ! -f ${app_dir}/oat/arm/${app_name}.odex ]; then
           jadx -e --show-bad-code ${app_dir}/${app_name}.apk
           return
        else
            subdir=arm
        fi
    fi
    HERE=$(pwd)
    cd ${app_dir}
    oat2dex oat/${subdir}/*.odex classes.dex
    jar -uvf ${app_name}.apk classes.dex
    cd $HERE
    jadx -e --show-bad-code ${app_dir}/${app_name}.apk
}

action=$1
shift 1
case $action in
    all-jar)
        extract_dex_from_frameworks_jars $1/framework/
        ;;
    all)
        AOSP_FRAMWROKDIR=$(get_abs_path $1/framework/arm64)
        decompile_framework "$@"
        ;;
    app)
        AOSP_FRAMWROKDIR=$(get_abs_path $1/framework/arm64)
        decompile_app $2
        ;;
    check)
        check_has_multidex $1
        ;;
    *)
        ;;
esac
