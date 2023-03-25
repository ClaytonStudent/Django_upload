from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import pandas as pd
import numpy as np
import lxml
def handle_uploaded_file(f):
    print(f.name)
    pd.set_option('mode.chained_assignment', None)
    df = pd.read_html(f)[0]
    df.rename(columns = {list(df)[0]:'product_type', list(df)[1]:'product_name', list(df)[2]:'product_stock',list(df)[3]:'product_number',list(df)[4]:'product_price_1',list(df)[5]:'product_sum',list(df)[6]:'product_price_2'}, inplace=True)
    # drop the last 1 rows
    df.drop(df.tail(1).index,inplace=True)
    df = df[~df['product_name'].isnull()]
    # seach for the key words
    searchfor = ['EasyTab', 'RAYOVAC','OCCHIAli','charro']
    df_iva_4 = df[df['product_name'].str.contains('|'.join(searchfor),case=False)]
    # filter out ART.1393 EXPO EL CHARRO OCCHIALI MISTI 169PZ
    out_index = df_iva_4.index[df_iva_4['product_type'] == '30IOI0000002000'].to_list()[0]
    df_iva_4.drop(index=out_index,inplace=True)
    # get the rest rows as iva 22
    df_iva_22 = df.drop(df_iva_4.index)
    # get the iva 4 / iva 22 / total record
    iva_4_number = df_iva_4.shape[0]
    iva_22_number = df_iva_22.shape[0]
    total_stock_number = df.shape[0]
    
    iva_4_stock_amount = df_iva_4['product_stock'].sum()
    iva_22_stock_amount = df_iva_22['product_stock'].sum()
    total_stock_amount = df['product_stock'].sum()

    iva_4_value = int(df_iva_4['product_sum'].sum() * 1.04)
    iva_22_value = int(df_iva_22['product_sum'].sum() * 1.22)
    total_stock_value = iva_4_value + iva_22_value
    print("---------------START------------------")
    print("IVA 4% stock amount:",iva_4_stock_amount)
    print("IVA 4% stock value:", iva_4_value)
    print("------------------------------------")
    print("IVA 22% stock amount:",iva_22_stock_amount)
    print("IVA 22% stock value:", iva_22_value)
    print("------------------------------------")
    print("Total stock amount:",total_stock_amount)
    print("Total stock value:", total_stock_value)
    print("----------------END----------------")
    data = ["IVA 4% stock amount: " + str(iva_4_stock_amount),
            "IVA 4% stock value: " + str(iva_4_value), 
            "IVA 22% stock amount: " + str(iva_22_stock_amount), 
            "IVA 22% stock value: " + str(iva_22_value), 
            "Total stock amount: " + str(total_stock_amount), 
            "Total stock value: " + str(total_stock_value)
            ]
    return data


def upload_file(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        data = handle_uploaded_file(myfile)
        return render(request, 'upload.html', {'uploaded_file_url': uploaded_file_url, 'data':data})
    return render(request, 'upload.html')
