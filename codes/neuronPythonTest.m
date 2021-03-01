function neuronPythonTest(geomFolder,matlaboutputFolder)

% this gets the names of the geometry files in .swc format
% it is an array of strings for each refinement level
% the geomFolder would be something like: D:\FinalHHSimulator\ReferenceGeometry\cell228-13MG
geomFiles = getGeomFilePrefix(geomFolder);

% % here is where we execute the python script for running the simulation
% % python output folder name is based on the outputFolder name you specify
% % right now this call will only evaluate voltages at the branch points
% matlaboutputFolder = name of folder where you want output to go, i.e.
% 'runCell228-13MG
pythonOutputFolder = sprintf('%s_pythonSim',matlaboutputFolder);
executePythonSim(geomFiles,pythonOutputFolder,0.125,0.001);
end