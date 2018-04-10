#!/usr/bin/env python3
import csv, copy, math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.mlab import griddata
from mpl_toolkits import axes_grid1
from scipy import stats
import pandas as ps
import time
import logging
import progressbar


progressbar.streams.wrap_stderr()
logging.basicConfig()

# Settings for libs
ps.set_option('display.max_rows', 500)
ps.set_option('display.max_columns', 500)
ps.set_option('display.width', 1000)

# Global variables


def import_and_scrub_data(raw_data_file):
    """
    Returns the dataset as a single pandas table,
    and scrubs
    """
    data = ps.read_csv(raw_data_file)
    # Drop nan values
    data = data[data.name.notnull()]
    # remove enteries where tests where not finished
    counter = data['name'].value_counts()
    not_done_data = counter[counter < counter.max()]
    print("removing beacuse of low entery count:")
    print(not_done_data)
    data = data[~data.name.isin(not_done_data.keys())]
    print("fixing thumb size")
    data.loc[data.thumb<20, 'thumb'] = data.loc[data.thumb<20, 'thumb'] * 10
    data.loc[data.thumb>200, 'thumb'] = data.loc[data.thumb>200, 'thumb'] / 10
    return data

def eucl_dist(x1,y1,x2,y2):
    """
    Simple function to calulate the euclidian distance
    """
    return (math.sqrt((x2-x1)**2 + (y2-y1)**2))

def analyze_and_cadegorize_data(df):
    # Counts the time it took for the user to press the point
    df['time'] = df.apply(lambda x: x['timeEnd'] - x['timeStart'], axis=1)

    # Calulate the distance
    df['distance'] = df.apply(lambda x: eucl_dist(x['targetX'],x['targetY'],x['touchX'],x['touchY']), axis=1)
    return df


class PlotHandeler:
    def __init__(self, data, plotcnf):
        self.data = data
        self.x_size , self.y_size = plotcnf["scrsize"]['x'] , plotcnf["scrsize"]['y']
        self.plot_scale = plotcnf["plot_scale"]

    def update(self,data):
        self.data = data

    def show(self):
        plt.show()

    def saveplot(self,fig,title):
        titlepath = title
        for target in [" ","\n",":",",","--"]:
            titlepath = titlepath.replace(target, "-")
        fig.savefig('imgs/png/'+ titlepath + '.png', dpi = 300,bbox_inches='tight',format='png')
        fig.savefig('imgs/pdf/'+ titlepath + '.pdf', dpi = 300,bbox_inches='tight',format='pdf')
        plt.draw()
        fig.clf()
        # plt.close()

    def _heatmap_plot(self,heatmap,title):
        """
        plotwrapper for the heatmap type, needs title beacuse of supplot colorbar
        """
        fig, ax = plt.subplots(figsize=(self.plot_scale,self.plot_scale*(self.y_size/self.x_size)))
        plt.title(title)
        plt.xlabel("X")
        plt.ylabel("Y")
        im = plt.imshow(heatmap.T, extent=[0, plotcnf["scrsize"]["x"], 0, plotcnf["scrsize"]["y"]], origin='lower')
        plt.gca().invert_yaxis()
        divider = axes_grid1.make_axes_locatable(ax)
        cax = divider.append_axes('right', size='5%', pad=0.05)
        fig.colorbar(im, cax=cax)

        return fig


    def _point_plot(self,data_this):
        """
        Plots the target points
        """
        fig = plt.figure(figsize=(self.plot_scale,self.plot_scale*(self.y_size/self.x_size)))

        xvals_target = list(data_this['targetX'])
        yvals_target = list(data_this['targetY'])

        plt.scatter(xvals_target, yvals_target,s=plotcnf["plot_scale"],zorder=10,label = "Targets")

        plt.ylim(0, self.y_size)
        plt.xlim(0, self.x_size)
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.gca().invert_yaxis()
        plt.legend()

        return fig

    def _delta_point_plot(self,data_this):
        """
        Plots the touch point and the target point, and adds a line between them
        """
        fig = plt.figure(figsize=(self.plot_scale,self.plot_scale*(self.y_size/self.x_size)))

        xvals_target = list(data_this['targetX'])
        yvals_target = list(data_this['targetY'])
        xvals_touch = list(data_this['touchX'])
        yvals_touch = list(data_this['touchY'])

        for x,y,xx,yy in zip(xvals_target,yvals_target,xvals_touch,yvals_touch):
            plt.plot([x,xx], [y,yy], '-',c="black", alpha=0.2, zorder=1)

        plt.scatter(xvals_target, yvals_target,s=7,zorder=10,label = "Targets")
        plt.scatter(xvals_touch, yvals_touch,s=7,zorder=10,label = "Touch")

        plt.ylim(0, self.y_size)
        plt.xlim(0, self.x_size)
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.gca().invert_yaxis()
        plt.legend()

        return fig


    def _create_heatmap(self,data_this,f_inside,f_represent,max_bins=(5,9),single=True):
        """
        f_inside takes a bin and the current data row,
        f_represent takes a data row. and the current containter dict, the val is shown in the 
                    graph
        max_bins are the bins to sort after
        single is if only one element is per bin

        Returns an array with the heatmap, and a container for additional information about the data
        """
        container = {}
        xx,yy = max_bins
        seen = False
        # Create the lookup dict
        print("Heatmap generator")

        print("Generating container")
        for x in range(0,xx):
            for y in range(0,yy):
                container[(x,y)] = {"val":np.NaN,"ent":[],"id_total":0,"id_count":0}
        
        # iterate over the data, and put them in their respective dict
        print("Sorting input values based on f_inside")
        for index, row in progressbar.progressbar(data_this.iterrows(),max_value=len(data_this)):
            for this_bins in sorted(container.keys()):
                if f_inside(max_bins,this_bins,row):
                    container[this_bins]["ent"].append(index)
                    if single:
                        break
        
        # calculate the value for the respected area
        print("\nCalculating their respective values based on f_represent")
        for this_bins in progressbar.progressbar(sorted(container.keys())):
            container[this_bins]["id_total"] = len(container[this_bins]["ent"])
            for index in container[this_bins]["ent"]:
                f_represent(container[this_bins],data_this.ix[index])
                container[this_bins]["id_count"] += 1
        
        # Fill the heatmap array
        print("\nGenerating heatmap")
        heatmap = np.zeros(max_bins)
        for x in range(0,xx):
            for y in range(0,yy):
                heatmap[x,y] = container[(x,y)]["val"]
        return heatmap, container

    def distance_errors(self,distance,title):
        data_this = self.data[self.data.distance > distance]
        fig =  self._delta_point_plot(data_this)
        plt.title(title)
        self.saveplot(fig,title)

    def high_latency(self,latency,title):
        data_this = self.data[self.data.time > latency]
        fig = self._delta_point_plot(data_this)
        plt.title(title)
        self.saveplot(fig,title)

    def relation_points(self,title):
        fig = self._delta_point_plot(self.data)
        plt.title(title)
        self.saveplot(fig,title)

    def simple_points(self,title):
        data_this = self.data
        fig = self._point_plot(data_this)
        plt.title(title)
        self.saveplot(fig,title)

    def count_heatmap(self,bins,title):
        # Square classifier
        def f_inside(max_bins,this_bins,row):
            max_x,max_y = row['totalX'] ,row['totalY']
            m_x,m_y = max_bins
            t_x,t_y = this_bins
            s_x,s_y = max_x/(m_x) , max_y/(m_y)
            p_x,p_y = row['targetX'],row['targetY']
            #Within grid
            if((s_x*t_x <= p_x < s_x*(t_x+1)) and
               (s_y*t_y <= p_y < s_y*(t_y+1))):
                return True
            return False
        # Count classifier
        def f_represent(container,row):
            # count the enteries
            if np.isnan( container['val']):
                container['val'] = 1
            else:
                container['val'] += 1
         

        heatmap,container = self._create_heatmap(self.data,f_inside,f_represent,bins)
        fig = self._heatmap_plot(heatmap,title)
        self.saveplot(fig,title)
        return container


    def distance_heatmap(self,bins,title):
        # Square classifier
        def f_inside(max_bins,this_bins,row):
            max_x,max_y = row['totalX'] ,row['totalY']
            m_x,m_y = max_bins
            t_x,t_y = this_bins
            s_x,s_y = max_x/(m_x) , max_y/(m_y)
            p_x,p_y = row['targetX'],row['targetY']
            #Within grid
            if((s_x*t_x <= p_x < s_x*(t_x+1)) and
               (s_y*t_y <= p_y < s_y*(t_y+1))):
                return True
            return False
        # Count classifier
        def f_represent(container,row):
            val = row['distance']
            # Create temp storage
            if not "tmp" in container:
                container["tmp"] = []
            container["tmp"].append(val)

            # If we are the last, and we want to commit
            if container["id_count"] >= container["id_total"] - 1:
                # Get the average, remove higest and lowest value
                container["tmp"].sort()
                container['val'] = np.average(container["tmp"])
         

        heatmap, container = self._create_heatmap(self.data,f_inside,f_represent,bins)
        fig = self._heatmap_plot(heatmap,title)
        self.saveplot(fig,title)
        return container

    def time_heatmap(self,bins,title):
        # Square classifier
        def f_inside(max_bins,this_bins,row):
            max_x,max_y = row['totalX'] ,row['totalY']
            m_x,m_y = max_bins
            t_x,t_y = this_bins
            s_x,s_y = max_x/(m_x) , max_y/(m_y)
            p_x,p_y = row['targetX'],row['targetY']
            #Within grid
            if((s_x*t_x <= p_x < s_x*(t_x+1)) and
               (s_y*t_y <= p_y < s_y*(t_y+1))):
                return True
            return False
        # Count classifier
        def f_represent(container,row):
            val = row['time']
            # Create temp storage
            if not "tmp" in container:
                container["tmp"] = []
            container["tmp"].append(val)

            # If we are the last, and we want to commit
            if container["id_count"] >= container["id_total"] - 1:
                # Get the average, remove higest and lowest value
                container["tmp"].sort()
                container['val'] = np.average(container["tmp"])
         

        heatmap, container = self._create_heatmap(self.data,f_inside,f_represent,bins)
        fig = self._heatmap_plot(heatmap,title)
        self.saveplot(fig,title)
        return container


if __name__ == "__main__":
    raw_data_file = "data/data.csv"
    data = import_and_scrub_data(raw_data_file)
    data = analyze_and_cadegorize_data(data)
    plotcnf ={"scrsize":{"x":data['totalX'].iloc[0],
                         "y":data['totalY'].iloc[0]},
              "plot_scale":4}
    max_latency = 2000
    max_distance = 200


    PlotHandeler = PlotHandeler(data,plotcnf)
    
    # show the distance errors and high latency
    PlotHandeler.distance_errors(max_distance,"Distances over "+str(max_distance) + "px")
    PlotHandeler.high_latency(max_latency,"Latencies over "+str(max_latency) + "ms")
    

    # update with removed errors
    data = data[data.time < max_latency]
    data = data[data.distance < max_distance]
    PlotHandeler.update(data)


    PlotHandeler.simple_points("Points after filtering")
    PlotHandeler.relation_points("All points and their relation")
    
    thumb_limit = np.floor(np.average(data.thumb.value_counts().index.values.tolist()))
    print("Thumb cutoff limit:",thumb_limit)
    data_small = data[data.thumb <= thumb_limit]
    data_big   = data[data.thumb  > thumb_limit]
    

    for bins in [(6,10),(5,9),(4,8),(10,15),(25,40)]:
        PlotHandeler.update(data)
        PlotHandeler.count_heatmap(bins,"Total observations per area:" + str(bins))
        PlotHandeler.distance_heatmap(bins,"Total average distance per area:" + str(bins))
        PlotHandeler.time_heatmap(bins,"Total average delay per area:" + str(bins))

        PlotHandeler.update(data_small)
        PlotHandeler.count_heatmap(bins,"Small thumbs observations per area:" + str(bins))
        PlotHandeler.distance_heatmap(bins,"Small thumbs average distance per area:" + str(bins))
        PlotHandeler.time_heatmap(bins,"Small thumbs average delay per area:" + str(bins))

        PlotHandeler.update(data_big)
        PlotHandeler.count_heatmap(bins,"Big thumbs observations per area:" + str(bins))
        PlotHandeler.distance_heatmap(bins,"Big thumbs average distance per area:" + str(bins))
        PlotHandeler.time_heatmap(bins,"Big thumbs average delay per area:" + str(bins))

    # Analysis part
    print(data['thumb'].describe())