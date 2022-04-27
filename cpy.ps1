
$dir = $PSScriptRoot

if ($args[0] -eq "-nstd") {
    # No standard library + C
    python $dir\c-nostd.py $args[1]
} else {
    # Standard library + C++
    python $dir\c.py $args[1]
}