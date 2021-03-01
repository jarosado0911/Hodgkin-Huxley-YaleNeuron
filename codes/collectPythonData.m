function [pythonVm,pythonTimes,nodeLocs]=collectPythonData(source_dir, arr_size,nTime)
% This script with organize the output data from the Yale Neuron PYTHON 
% simulations. The output is located in the data folder
% 1) source_dir  = folder where the data is located you should put it in 
% somewhere we you distringuish between refinement levels i.e.
% blah...blah/4ref
%
% 2) arr_size = this is the size of the output .mat matrices
% 3) nTime = every n-time points save the data

% set the data directory and counts the number of vm files in the data
% directory, this is the data from PYTHON
data_dir = sprintf('%s/dataV',source_dir);
d = dir([data_dir, '\*.dat']);
n=length(d);

% this loop will form a lst of arrays with indices in each array.
% each array in the list is of size arr_size, except probably the last
% array
% so for instance ...1.mat file will have the 1-100 node data
% and ...2.mat file will have 101-201 node data and so on
lst={};
j=1; tmp_array=[];
for i=0:(n-1)
 tmp_array=[tmp_array,i];
 if (mod(i+1,arr_size)==0)
     % if you reach an index that is multiple of arr_size, then
     % save the array to lst, and increment the list
    lst{j}=tmp_array;
    tmp_array=[];   % reset the array
    j = j+1;        % increase lst by 1
 end
end
%this takes care of any left overs
%NOTE: j is the number of .mat file produced!
lst{j}=setdiff((0:(n-1)),(0:lst{j-1}(end)));

% initialize empty python data array
pythonVm=[];

% here we go through the python data and start saving data in .mat files
% according to the lst we made previously
for k=1:j
    for i=lst{k}(1):lst{k}(end)
        %this loop reads the data corresponding to list{k}
        filename = sprintf('%s/vm_x_%i.dat',data_dir,i);
        tmp = readmatrix(filename);
        tmp = tmp(1:nTime:end);         % only save every n-time point
        pythonVm = [pythonVm, tmp];
        fprintf(sprintf('read x =  %i\n',i));
    end
    fprintf(sprintf('Read Batch %i\n',k));
    
    % save the python data to a .mat file
    save(sprintf('%s/pythonVm_%i.mat',source_dir,k),'pythonVm','-v7.3');
    pythonVm=[];
end

% loads data into pythonVm for output
pythonVm=[];
tmp=[];
for k=1:j
    load(sprintf('%s/pythonVm_%i.mat',source_dir,k),'pythonVm');
    fprintf(sprintf('Got batch %i\n',k));
    tmp=[tmp, pythonVm]; 
    pythonVm=[];
end
pythonVm=tmp;

% loads time data according to nTime
pythonTimes = readmatrix(sprintf('%s/pythonTimes.dat',source_dir)); pythonTimes = pythonTimes(1:nTime:end);
nodeLocs = readmatrix(sprintf('%s/allLocs.txt',source_dir)); nodeLocs = nodeLocs(:,1:end)';
end