# Generating the Array for the prices of goods
val = range(10, 101, length=10)

# Generating an Array for the Items List
items = ["Cola", "Fritters", "Fryums", "Waffles", "Coffee",
         "Papadams", "Ice-Cream", "Burger", "Pizza", "Pasta"]

# Displaying the Output
println("The Prices Array is :-")
println(collect(val))
println("\nAccordingly the Items Array is :-")
println(items)

# Displaying the items where price >= 50 OR item is 'Cola'
arr = items[(val .>= 50) .| (items .== "Cola")]
println("\nThe Said Array containing the prices greater than 50 INR OR Cola is :-")
println(arr)

# Shipping cost: 0 if val >= 60 else 5
shipping_cost = ifelse.(val .>= 60, 0, 5)

println("\nThe Shipping cost array consisting of Free Shipping above 60 INR and 5 INR Otherwise is :->")
println(shipping_cost)

println("\nThe Summation of the Array (i.e the total shipping cost) is $(sum(shipping_cost))")