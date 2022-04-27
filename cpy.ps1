
$dir = $PSScriptRoot

if ($args[0] -eq "-nstd") {
    # No standard library + C
    python3 $dir\c-nostd.py $args[1]
} else {
    # Standard library + C++
    python3 $dir\c.py $args[0]
}