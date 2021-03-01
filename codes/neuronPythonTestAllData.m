function neuronPythonTestAllData(geomFolder,matlaboutputFolder)

% this gets the names of the geometry files in .swc format
% it is an array of strings for each refinement level
% the geomFolder would be something like: D:\FinalHHSimulator\ReferenceGeometry\cell228-13MG
geomFiles = getGeomFilePrefix(geomFolder);

% I choose the 5th refinement level geometry it does the job in a good
% amount of time
geomfilename = [geomFiles(1).folder filesep geomFiles(1).name];

% run the yale neuron simulation in python only writing the voltages at the
% branch points which is sent as nodeLststr
pythonOutputFolder = sprintf('%s_pythonSimAllData',matlaboutputFolder);
commandString = sprintf('python3 part1.py %f %f %s %s',4,0.002,pythonOutputFolder,geomfilename);
system(commandString)

end