import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import matplotlib.pyplot as plt

def fetch_income_sheet(ticker):
    # Define the URL for the Yahoo Finance page of the company
    url = f"https://finance.yahoo.com/quote/{ticker}/financials?p={ticker}"
    
    # Print the URL for debugging
    print(f"Fetching data from URL: {url}")

    # Set a User-Agent header to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Make the HTTP request to get the webpage content
    response = requests.get(url, headers=headers)
    

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        return None

    # Print the response text for debugging
    print("Response content:")
    #print(response.text[:1000])  # Print the first 1000 characters to avoid clutter

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    soup1 = soup.prettify()
    #print(soup1[626000:666000])

    # Extract the table containing the financial data
    data_text = soup.get_text()
    #print(data_text)
    #Splitting the text from Total revenue to Tax rate for calcs (where financial sheet is)
    result1 = data_text.split("Total Revenue", 1)[1].split("Normalized EBITDA", 1)[0]



    #Taking Dates Data which always occurs between words Breakdown and Total Revenue
    dates_data = data_text.split("Breakdown", 1)[1].split("Total Revenue", 1)[0]
    #Checking Dates Data
    

    dates_data1 = dates_data.strip().split('\n')

    for dates in dates_data1:
        dates_data1 = dates.split(" ")

    #Prints the dates - creating column headers.
    #print(dates_data1)
    #calculating length of dates
    dates_length = (len(dates_data1))

    #Adding back in Total Revenue to beginning
    result1 = "Total Revenue" + result1

    
    lines = result1.strip().split('\n')
   # print(lines)

    for line in lines:
        lines = line.split(" ")
        

    new = data_text.strip().split('\n')
   # print(lines)

    for ne in new:
        new = ne.split(" ")

        


    #print(lines)   

    # Define the keywords
    keywords = ["Normalized", "EBITDA"]

    # Split the string into tokens
    tokens = new

    # Initialize the index to None
    start_index = None

    # Iterate over the tokens to find the consecutive keywords
    for i in range(len(tokens) - len(keywords) + 1):
        if tokens[i:i + len(keywords)] == keywords:
            start_index = i
            break
    
    #Global_NormalizedEBITDA = None
    # Check if the consecutive keywords were found
    if start_index is not None:
        # Collect the next 4 strings after the second keyword
        global Global_NormalizedEBITDA
        Normalized_EBITDA = ["Normalized"] + ["EBITDA"] + tokens[start_index + len(keywords): start_index + len(keywords) + dates_length]
        Global_NormalizedEBITDA = Normalized_EBITDA
        # Print the result
        
    else:
        print("Consecutive keywords not found in the text")

    
    #print(Global_NormalizedEBITDA)
    lines.extend(Global_NormalizedEBITDA)
    #print(lines)
    # Example list of strings

    concatenated_strings = []
    numbers = []

    # Index variable to track position in the list
    i = 0

    # Define a function to check if a string is alpha or special character
    def is_alpha_or_special(s):
        return s.isalpha() or s in "&"

    # Define a function to check if a string is a numeric value, including negative numbers
    def is_numeric(s):
        s = s.replace(',', '')
        return s.replace('.', '', 1).lstrip('-').isdigit() or s == "--"

    while i < len(lines):
        if is_alpha_or_special(lines[i]):
            concatenated = lines[i]
            i += 1
            while i < len(lines) and is_alpha_or_special(lines[i]):
                concatenated += lines[i]
                i += 1
            concatenated_strings.append(concatenated)
        elif is_numeric(lines[i]):
            numbers.append(lines[i])
            i += 1
        else:
            i += 1


    #print("Concatenated Strings:", concatenated_strings)
    #print("Numbers:", numbers)
    #print(numbers[79])
    #print(len(numbers))
    #print(len(concatenated_strings))
    # Dates for columns
    dates = dates_data1

    # Ensure the length of numbers is a multiple of the number of dates
    num_dates = len(dates)
    if len(numbers) % num_dates != 0:
        raise ValueError("The length of the numbers list is not a multiple of the number of dates.")

    # Reshape numbers list to match the dimensions of concatenated_strings
    reshaped_numbers = [numbers[i:i + num_dates] for i in range(0, len(numbers), num_dates)]
    #print(len(reshaped_numbers))

    # Create DataFrame
    global df
    df = pd.DataFrame(reshaped_numbers, columns=dates, index=concatenated_strings)

    # Display DataFrame
    print(df)



    
   


# Main program
ticker = "V"


fetch_income_sheet(ticker)

#https://finance.yahoo.com/quote/MMM/cash-flow/

#############################################################################
####VISUALS

def plot_financial_metric(df, metric_name):
    # Check if the metric is in the DataFrame
    if metric_name not in df.index:
        print(f"Metric '{metric_name}' not found in DataFrame.")
        return
    
    # Filter out the TTM column
    columns_to_plot = [col for col in df.columns if col != 'TTM']
    
    # Extract the relevant data
    data_to_plot = df.loc[metric_name, columns_to_plot]
    
    # Convert the column names to datetime for better plotting
    dates = pd.to_datetime(columns_to_plot, format='%m/%d/%Y')
    
    # Plot the data
    plt.figure(figsize=(12, 8))
    plt.plot(dates, data_to_plot, marker='o', linestyle='-', linewidth=3, color='b', markersize=8, markerfacecolor='r')
    plt.title(f'{metric_name} Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=14)
    plt.ylabel(metric_name, fontsize=14)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.axhline(0, color='black', linewidth=0.7)
    plt.gca().yaxis.tick_right()
    plt.gca().invert_yaxis()  # Invert the Y-axis to ensure it increases from the origin
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    plt.show()

# Example usage:
# plot_financial_metric(df, 'TotalRevenue')
# plot_financial_metric(df, 'CostofRevenue')
# plot_financial_metric(df, 'GrossProfit')
# plot_financial_metric(df, 'OperatingExpense')


def plot_financial_metric_bar(df, metric_name):
    # Check if the metric is in the DataFrame
    if metric_name not in df.index:
        print(f"Metric '{metric_name}' not found in DataFrame.")
        return
    
    # Filter out the TTM column
    columns_to_plot = [col for col in df.columns if col != 'TTM']
    
    # Extract the relevant data
    data_to_plot = df.loc[metric_name, columns_to_plot]
    
    # Convert the column names to datetime for better plotting
    dates = pd.to_datetime(columns_to_plot, format='%m/%d/%Y')
    
    # Plot the data
    plt.figure(figsize=(12, 8))
    plt.bar(dates, data_to_plot, color='b', edgecolor='k', linewidth=1.5)
    plt.title(f'{metric_name} Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=14)
    plt.ylabel(metric_name, fontsize=14)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.axhline(0, color='black', linewidth=0.7)
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    plt.show()

# Example usage:
#plot_financial_metric_bar(df, 'TotalRevenue')



def plot_financial_metrics1_bar(df, metric_names):
    # Filter out the TTM column
    columns_to_plot = [col for col in df.columns if col != 'TTM']
    
    # Check if all the metrics are in the DataFrame
    for metric in metric_names:
        if metric not in df.index:
            print(f"Metric '{metric}' not found in DataFrame.")
            return
    
    # Extract the relevant data
    data_to_plot = df.loc[metric_names, columns_to_plot]
    
    # Convert the column names to datetime for better plotting
    dates = pd.to_datetime(columns_to_plot, format='%m/%d/%Y')
    
    # Plot the data
    x = range(len(dates))  # the label locations
    width = 0.2  # the width of the bars
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Generate bars for each metric
    for i, metric in enumerate(metric_names):
        bars = ax.bar(
            [p + width * i for p in x], 
            data_to_plot.loc[metric], 
            width, 
            label=metric
        )
    
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_xlabel('Date', fontsize=14)
    ax.set_ylabel('Value', fontsize=14)
    ax.set_title('Financial Metrics Over Time', fontsize=16, fontweight='bold')
    ax.set_xticks([p + width for p in x])
    ax.set_xticklabels(dates.strftime('%Y-%m'), rotation=45)
    ax.legend()
    
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    # Ensure y-axis increases from the origin
    y_min, y_max = data_to_plot.min().min(), data_to_plot.max().max()
    plt.ylim(y_min, y_max)
    plt.tight_layout()
    
    # Show the plot
    plt.show()

# Example usage:
plot_financial_metrics1_bar(df, ['TotalRevenue', 'CostofRevenue', 'GrossProfit'])




# def plot_financial_metric(df, metric_name):
#     # Check if the metric is in the DataFrame
#     if metric_name not in df.index:
#         print(f"Metric '{metric_name}' not found in DataFrame.")
#         return
    
#     # Filter out the TTM column
#     columns_to_plot = [col for col in df.columns if col != 'TTM']
    
#     # Extract the relevant data
#     data_to_plot = df.loc[metric_name, columns_to_plot]
    
#     # Convert the column names to datetime for better plotting
#     dates = pd.to_datetime(columns_to_plot, format='%m/%d/%Y')
    
#     # Plot the data
#     plt.figure(figsize=(10, 6))
#     plt.plot(dates, data_to_plot, marker='o', linestyle='-', color='b')
#     plt.title(f'{metric_name} Over Time')
#     plt.xlabel('Date')
#     plt.ylabel(metric_name)
#     plt.grid(True)
#     plt.xticks(rotation=45)
#     plt.tight_layout()
#     plt.show()

# # Example usage:

# plot_financial_metric(df, 'TotalRevenue')











#############################################################################
######FORMULAS############

