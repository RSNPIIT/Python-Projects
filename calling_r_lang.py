import rpy2.robjects as robj

# Assigning R functions to Python
# R is a Brother of Python -- Python R Bridge (reticulate rpy2 bridge)
robj.r('msg <- "Hello World from R inside Python" ')
robj.r('print(msg)')
