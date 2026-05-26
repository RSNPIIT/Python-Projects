println("="^70)
println("FLASK + SQLALCHEMY LEARNING PROJECT")
println("="^70)

apps = [
    "Flask Routing",
    "Jinja Templates",
    "Sessions",
    "Flash Messages",
    "SQLite",
    "SQLAlchemy",
    "Alembic Migrations",
    "HTML Forms"
]

println("\nCurrently Learning :-\n")

for (i, app) in enumerate(apps)

    println("[$i] => $app")

end

println("\n" * "="^70)

folders = [
    "templates/",
    "static/",
    "migrations/",
    "instance/"
]

println("Important Directories :-\n")

for folder in folders

    println("-> $folder")

end

println("\n" * "="^70)

println("Current Status :-")

features = Dict(
    "Flask App" => true,
    "Database" => true,
    "Sessions" => true,
    "Frontend Forms" => true,
    "Admin Panel" => false,
    "Authentication System" => false
)

for (key, value) in features

    if value == true

        println("[DONE] $key")

    else

        println("[TODO] $key")

    end

end

println("\n" * "="^70)

println("="^70)