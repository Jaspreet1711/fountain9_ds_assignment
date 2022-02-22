# Setting up the Environment
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# Loading the Data Sets
sales = pd.read_excel("Fountain9 DS Assignment Data.xlsx", sheet_name = "Sales")
product_master = pd.read_excel("Fountain9 DS Assignment Data.xlsx", sheet_name = "Product Master")
branch_master = pd.read_excel("Fountain9 DS Assignment Data.xlsx", sheet_name = "Branch Master")
purchase_orders_1 = pd.read_excel("Fountain9 DS Assignment Data.xlsx", sheet_name = "Purchase Orders 1")
supplier_product_branch = pd.read_excel("Fountain9 DS Assignment Data.xlsx", sheet_name = "Supplier-Product-Branch")
select = pd.read_excel("Fountain9 DS Assignment Data.xlsx", sheet_name = "Select", )

# Data Description (Data Types, DF Shape, Checking Missing Values & Detecting Duplication)
tables = [sales, product_master, branch_master, purchase_orders_1, supplier_product_branch, supplier_product_branch, select] 
    
def df_brief(dataframe, describe = 0):
    
    # -- Extracting Dataframe Name defined
    def df_name(df):
        name = [i for i in globals() if globals()[i] is df][0]
        return str(name)
    
    # -- Getting Info, Shape, Missing Values and Duplicates
    Name = df_name(dataframe)
    print("DF Name: " + Name)
    print(" ")
    print(dataframe.info())
    print(" ")
    print("Shape of "+ Name + " DF " + str(dataframe.shape))
    print(" ")
    print("Missing values columns wise:")
    print(dataframe.isnull().sum())
    print(" ")
    dup_count = dataframe.duplicated().sum() 
    if dup_count == 0:
        print("No Duplicates in DataFrame based on all columns")
    else:
        print("Number of Duplicate row(s) found in " + Name + " DF is/are: " + str(dup_count))
    print(" ")
    
    # -- If we want to describe dataframe (mean, median, etc.)
    if describe == 1:
        print("Described")
        print(dataframe.describe())
        print(" ")
    else:
        pass
    print("#-------#-------#-------#-------#-------#-------#-------#")
    print(" ")
        
# -- tables data types info, shape, Missing Values and Duplicates    
for table in tables:
    df_brief(table)

# -- Data type format looks fine.
# -- There are some missing values in "purchase orders 1" Table.
# -- "Product Master" has 1 duplicate row based on above Description.

Break_line = "*----------------------****----------------------*"

#----------------------*----------------------*----------------------*----------------------*#
#----------------------*----------------------*----------------------*----------------------*#

# Question - 1

# -- Treating Duplicate Value in Product Master 1
print("#-----------------------------------------------#")
print("Treating Duplicate Value in Product Master 1")
print(product_master.head())
print(" ")
# ---- Product ID is the Primary Key in table Product Master
product_master.drop_duplicates(subset = ['Product ID'], keep = 'last', inplace = True)
print("Duplication after the treatment of Product Master: " + str(product_master.duplicated().sum())) 
print("#-----------------------------------------------#")
print(" ")

# -- Joining Sales with Product Master (on Product ID) and Branch Master (on Branch ID)
sales_prod = sales.merge(product_master, how = 'left', left_on = 'Product ID', right_on = 'Product ID')
sales_prod_bran = sales_prod.merge(branch_master, how = 'left', left_on = 'Branch ID', right_on = 'Branch ID')

print("Output of Question - 1")
Oues1_Output = sales_prod_bran
pd.set_option('display.max_columns', None)
print(Oues1_Output.head())
print(Break_line)
print(" ")

#----------------------*----------------------*----------------------*----------------------*#
#----------------------*----------------------*----------------------*----------------------*#
  
# Question - 2

# -- Missing Value in "Purchase Orders 1" are in "Received Quantity" and "Received Date"
# -- I am assuming that Missing Values in the above table mentioned represents order not received yet.
# -- Imputing Missing Values in both the columns with "NR"(Not Received Yet).
purchase_orders_1["Received Quantity"].fillna("NR", inplace = True)
purchase_orders_1["Received Date"].fillna("NR", inplace = True)

# -- Creating Lead Time Column 
def lead_time(r):
    if r['Received Date'] == 'NR':
        return "NR"
    else:
        date_diff = r['Received Date'] - r['Ordered Date']
        day_diff = int(date_diff.days)
        return day_diff 

purchase_orders_1["lead time"] = purchase_orders_1.apply(lambda x: lead_time(x), axis = 1)

# -- Group by using composite key (Product ID-Branch ID-Supplier ID)
# -- Filtering out NR from the data
purchase_orders_1_wo_nr = purchase_orders_1[purchase_orders_1["lead time"] != "NR"]
# -- converting the lead time into numeric format after removing "NR"
purchase_orders_1_wo_nr["lead time"] = pd.to_numeric(purchase_orders_1_wo_nr["lead time"])
# -- Calculating Average
purchase_orders_1_average = purchase_orders_1_wo_nr.groupby(by=["Product ID", "Branch ID", "Supplier ID"]).mean()
purchase_orders_1_average.rename(columns={'lead time':'avg lead time'}, inplace = True)
purchase_orders_1_average = purchase_orders_1_average["avg lead time"].to_frame()
# -- Calculating Variance
purchase_orders_1_variance = purchase_orders_1_wo_nr.groupby(by=["Product ID", "Branch ID", "Supplier ID"]).var()
purchase_orders_1_variance.rename(columns={'lead time':'var lead time'}, inplace = True)
purchase_orders_1_variance = purchase_orders_1_variance["var lead time"].to_frame()

# -- Group by function by default makes index of column(s) on which group by is performed.
print("Output of Question - 2")
Oues2_Output = purchase_orders_1_average.merge(purchase_orders_1_variance, how = 'left', left_index=True, right_index=True)
print(Oues2_Output.head())
print(Break_line)
print(" ")

#----------------------*----------------------*----------------------*----------------------*#
#----------------------*----------------------*----------------------*----------------------*#

# Question - 3

Week_num = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}

# -- Days are mentioned inside a list structure but whole list is a string (or object) format.
def week_num_conv(r):
    r = r.replace('[', '').replace(']', '').replace('"', '').replace(',', '')
    r = r.lower()
    r_ls = r.split(' ')
    day_ls = []
    for day in r_ls:
        n = Week_num[day]
        day_ls.append(int(n)) 
    days = str(day_ls)
    days = days.replace('[', '').replace(']', '').replace(' ', '')    
    return days

supplier_product_branch['Schedule Days'] = supplier_product_branch['Schedule Days'].apply(lambda x: week_num_conv(x)) 


print("Output of Question - 3")
Oues3_Output = supplier_product_branch
print(Oues3_Output.head())
print(Break_line)
print(" ")

#----------------------*----------------------*----------------------*----------------------*#
#----------------------*----------------------*----------------------*----------------------*#

# Question - 4
def Result(r):
    if r['Product Category'] == "Biscuits":
        return r['Quantity']
    else:
        return r['Price']

select['Result'] = select.apply(lambda x: Result(x), axis = 1)

print("Output of Question - 4")
Oues4_Output = select
print(Oues4_Output.head())
print(Break_line)
print(" ")

#----------------------*----------------------*----------------------*----------------------*#
#----------------------*----------------------*----------------------*----------------------*#