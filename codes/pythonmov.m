function pythonmov(pythonOutputFolder)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Get Python Data
arr_size=150;
nTime = 10;
source_dir = pythonOutputFolder;
[pythonVm,pythonTimes,nodeLocs]=collectPythonData(source_dir, arr_size,nTime);

pythonR = readmatrix(sprintf('%s/diam.txt',source_dir));
pythonMarker = 20.*pythonR./max(pythonR);

% this will set the size of the window frame
fig=figure('units','normalized','outerposition',[0 0 0.35 0.75]);

% this is for recording the movie
v = VideoWriter(sprintf('%s/python_%s.mp4',source_dir,source_dir),'MPEG-4');
open(v)

for i=1:2:length(pythonTimes)
        scatter3(nodeLocs(:,1),nodeLocs(:,2),nodeLocs(:,3),pythonMarker,'filled','CData',pythonVm(i,:));
        xlabel('um')
        ylabel('um')
        set(gca,'Color', [0.5 0.5 0.5])
        caxis([-5 50 ])
        title(sprintf('Python, t = %0.3f',pythonTimes(i)))
        colormap('jet')
        colorbar
        c = colorbar;  
        c.Label.String="mV";
        view(2)
        
        thisframe=getframe(fig);
        writeVideo(v, thisframe);

        drawnow
        fprintf('frame = %i\n',i)
end

save(sprintf('%s/%s_Vm.mat',source_dir,source_dir),'pythonVm','-v7.3')
save(sprintf('%s/%s_times.mat',source_dir,source_dir),'pythonTimes','-v7.3')
save(sprintf('%s/%s_nodes.mat',source_dir,source_dir),'nodeLocs','-v7.3')

close(v)