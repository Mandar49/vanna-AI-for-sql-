
def calculate_revenue(sales, costs):
    '''Calculate net revenue.'''
    return sales - costs

def growth_rate(current, previous):
    '''Calculate growth rate percentage.'''
    return ((current - previous) / previous) * 100
            