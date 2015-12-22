#!/usr/bin/python

## TODO explain code EM.

import urllib, urllib2, re, sys, os, string, cgi
import cgitb; cgitb.enable()
import glob
import calendar,datetime,time

if __name__=='__main__':
    	form = cgi.FieldStorage()
	print "Content-Type: text/html"     # HTML is following
    	print                               # blank line, end of headers
    	print "<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01//EN\">"
	#Gather Monthly data
	arr_acc=['Month']
	location='/opt/tools/aws/scripts-billing/monthly-invoice/'
	acc_dic={}
	month=[]
	month_dic={}
	available_month=[]
	mapping=open('acc_mapping.txt','r').readlines()
	
	for acc in glob.glob(location+'*'):
		account=acc.split("/")[-1]
		arr_acc.append(account)
		files=glob.glob(acc+"/20*")	
		month_dic={}
		for fil in files:
			#if "Estimate" not in fil:
			file_month=fil.split("/")[-1].split("-")[0]	
			if file_month not in month:
				month.append(file_month)	
			with open (fil,"r") as infile:
				data = infile.read().split(",")[-1].replace("\n","")
			if "Estimate" not in fil:
				if file_month in month_dic:month_dic[file_month]+= float(data)
				else:month_dic[file_month]= float(data)
			else:
				days=calendar.monthrange(int(file_month[0:4]),int(file_month[4:6]))[1]
				today=time.gmtime(os.path.getmtime(fil))[2]
				data_estimate=(float(data)*days)/today
				if file_month in month_dic:month_dic[file_month]+= data_estimate
				else: month_dic[file_month]=data_estimate
		acc_dic[account]=month_dic
	output=""
	output_h="['Month'"
	for mont in sorted(month):
		output+="['"+mont+"'"
		for acc in acc_dic:
			try:acc_map=[s for s in mapping if acc in s][0].split(",")[1]
                        except:acc_map=acc		
			if acc_map not in output_h:
				output_h+=",'"+acc_map+"'"
			if mont in acc_dic[acc]:
				output+=","+str(acc_dic[acc][mont])
			else:
				output+=",0"
		output+="],"
	output_h+="],"
	output=output_h+output[:-1]
	#Gather daily data
	location='/opt/tools/aws/scripts-billing/daily/'
	days=[]
	acc_day_val={}
	acc_dic={}
	for acc in glob.glob(location+'*'):
		account=acc.split("/")[-1]
                arr_acc.append(account)
		acc_day_val={}
                files=sorted(glob.glob(acc+"/20*"))[-8:]
		#print files
		cost1=0
		if len(files) > 1:
			for fil in files:
				file_name=fil.split("/")[-1].split(".")[0]
				if file_name not in days: days.append(file_name)
				
				cost=0
				with open (fil,"r") as infile:
					data=infile.read().split("\n")
					for reg in data[:-1]:
						if "AccountID" not in reg:
							cost+=float(reg.split(",")[4])
					try:
						if len(files) < 8 and files.index(fil) == 0:
							acc_day_val[file_name]=0
						else:
							acc_day_val[file_name]=cost-cost1
						cost1=cost
					except:
						acc_day_val[file_name]=cost
						cost1=cost
			acc_dic[account]=acc_day_val
	output2=""
	output_h2="['Day'"
	for day in sorted(days)[1:]:
		output2+="['"+day+"'"
		for acc in acc_dic:
			try:acc_map=[s for s in mapping if acc in s][0].split(",")[1]
                       	except:acc_map=acc
			if acc_map not in output_h2:
				output_h2+=",'"+acc_map+"'"
			if day in acc_dic[acc]:
				output2+=","+str('%.0f'%acc_dic[acc][day])
			else:
				output2+=",0"
		output2+="],"
	output_h2+="],"
	output2=output_h2+output2[:-1]

	# Individual account graphs



	#print HTML
	#<h1 style="font-family:arial;text-align:center;">AWS Accounts Report</h1>
  	print """ 
<html>
  <head>
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.load("visualization", "1.1", {packages:["bar"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = google.visualization.arrayToDataTable(["""+output+"""]);
        var options = {
          title: 'Individual Accounts Expenditure',
          hAxis: { titleTextStyle: {color: '#333'}, textStyle: {fontSize: 12, bold: true}},
          vAxis: {minValue: 0, textStyle: {fontSize: 12, bold: true}},
          isStacked: false,
	  chartArea: {left: 50, top: 50},
          height: 500,  
	  width: 900,
	  selectionMode: 'multiple',
  	  tooltip: {trigger: 'selection'},
  	  aggregationTarget: 'category',
	  legend: {position: 'right', textStyle: {color: 'black', fontSize: 12}},
        };
    
        var chart = new google.visualization.AreaChart(document.getElementById('chart_div'));
        chart.draw(data, options);
	
	var options = {
          title: 'Stacked Accounts Expenditure',
          hAxis: { titleTextStyle: {color: '#333'}, textStyle: {fontSize: 12, bold: true}},
          vAxis: {minValue: 0, textStyle: {fontSize: 12, bold: true}},
          isStacked: true,
	  chartArea: {left: 50, top: 50},
          height: 500,  
          width: 900,
	  legend: {position: 'right', textStyle: {color: 'black', fontSize: 12}},
        };   
	var chart = new google.visualization.AreaChart(document.getElementById('chart_div2'));
        chart.draw(data, options);
 

	var data2 = google.visualization.arrayToDataTable(["""+output2+"""]);
	var options2 = {
	  title: 'Stacked daily, last 7 days',
	  hAxis: {title: 'Last 7 days',  titleTextStyle: {color: '#333',fonrSize: 12}, textStyle: {fontSize: 12, bold: true}},
          vAxis: {minValue: 0, textStyle: {fontSize: 12, bold: true}},
	  isStacked : true,
	  chartArea: {left: 50, top: 50},
	  height: 500,  
          width: 900,
          legend: {position: 'right', textStyle: {color: 'black', fontSize: 12}},
	}; 
	var chart = new google.visualization.ColumnChart(document.getElementById('chart_div3'));
        chart.draw(data2, options2);


        }
    </script>
  </head>
  <body>
   <table>
    <tr>
     <td>
       <div id="chart_div" style="width: 850px; height: 450px;"></div>
     </td>
     <td>
       <div id="chart_div2" style="width: 850px; height: 450px;"></div>
     </td>
    </tr>
    <tr>
     <td>
      <div id="chart_div3" style="width: 850px; height: 450px;"></div>
     </td>
     <td>
     </td>
    </tr>"""
    #<tr>

    #</tr>
  	print """ </table>  

</body>
</html>
"""
