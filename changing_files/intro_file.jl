using Dates

# ── Directory Intro Script ──────────────────────────────────────────────
println("=" ^ 55)
println("  Welcome to the changing_files directory")
println("=" ^ 55)

println("\n📁 Directory Purpose:")
println("   This directory contains files used for bulk renaming")
println("   and file management experiments.\n")

println("🐍 Main Script:")
println("   changer.py  →  A Python bulk file renamer")
println("               →  Renames all non-.py files in the directory")
println("               →  Custom name + extension support\n")

println("📄 Files Present:")
for f in readdir(".")
    ext = splitext(f)[2]
    tag = ext == ".py"  ? "Python Script" :
          ext == ".jl"  ? "Julia Script"  :
          ext == ".txt" ? "Text File"     :
          ext == ".c"   ? "C Source"      :
          ext == ".cpp" ? "C++ Source"    :
          ext == ".rb"  ? "Ruby File"     : "File"
    println("   → $f  [$tag]")
end

println("\n📌 Placeholder Info:")
println("   Owner   :  Ramrup Satpati (RSNPIIT)")
println("   Project :  changing_files utility")
println("   Version :  0.1-dev")
println("   Status  :  Work In Progress")

println("\n🕐 Script run at: ", Dates.format(now(), "dd-mm-yyyy HH:MM:SS"))
println("=" ^ 55)