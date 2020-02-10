# Analysing the possibilities of AIS shipping data

The scripts in this repository are used for processing AIS data in the waterway between Lemmer and Delfzijl in the north of the Netherlands.

The waterway between Lemmer and Delfzijl (a.k.a. the HLD) functions as an important transport corridor in the north of the Netherlands. In the past, each bridge and lock served as a checkpoint for all passing vessels due to the local operation of these structures. However, due to advances in technology, the local operation of bridges became redundant, for which reason ships are now only counted at the entry points of the HLD: the locks at Lemmer and Gaarkeuken. This development causes the shipping behaviour to be largely unknown to Rijkswaterstaat, which is since 2019 the managing authority of this waterway. Therefore, the aim of the research is to create a method for updating the view on shipping behaviour in the waterway, for which data from the Automatic Identification System (AIS) is used. 

AIS is a relatively new system that transmits location data every few seconds, and is intended as a means of ship-to-ship and ship-to-land communications. It has only been mandatory for inland shipping in The Netherlands as of 2019, for which reason it is not used for waterway monitoring in the HLD yet. The advantages of using AIS for the monitoring of the waterway are that AIS data entries come with contextual information, such as amongst others speed, ship length, vessel type and level of hazardous cargo. 

In this research, a flexible and scalable methodology is developed in Python and SQL for PostgreSQL with PostGIS extension. The methodology is also applicable for the analysis of other waterways. The methodology is focussed on extracting the following information from the dataset:
-	The spatial data quality of the dataset;
-	An assessment of privacy implications of the dataset;
-	The distribution of ships within a time frame as a time series (see GIF);
-	The amount of ships that cross a certain digital counting line;
-	The extraction of stops and moves from a track, and the duration of stops.

The timeseries shown below is a result of the select_by_property.py script. It shows the amount of ships that cross each square of 2 by 2 square kilometers per time span of 2 hours.

![AIS time series on June 10th](https://github.com/bkronemeijer/internship/blob/master/AIS_10_2.gif)

