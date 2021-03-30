#!/bin/bash


# Get the path of the scripts
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"

recipe__init(){
    command python "$DIR/recipe_init.py" "$@"
}

recipe__taste(){
    # Check if file specified exists
    if [ $# -eq 0 ]; then
        echo "Please provide the path to metadata.yaml file"
        return 1
    fi

    echo "Taste recipe with $1."
}

recipe__test(){
    # Check if file exists in the current working directory
    if [ ! -d "tests/" ]; then
        echo "Please cd to the project directory and make sure the 'tests/' folder exists."
    else
        echo "Test recipe."
    fi
}

# Implements subcommand calling paradigm
recipe(){
    local cmdname=$1; shift
    case $cmdname in
        init|taste|test)
            if type "recipe__$cmdname" >/dev/null 2>&1; then
                "recipe__$cmdname" "$@"
            else
                echo "Unimplemented command: recipe $cmdname"
            fi
            ;;
        *)
            echo "Unrecognized recipe command: recipe $cmdname"
            ;;
    esac
}