% (c) 2023 Northeastern University
% Institute for the Wireless Internet of Things
% Created by Davide Villa (villa.d@northeastern.edu)

clear all
close all
% clc

%% Display data

% h5info('measurements.hdf5')
% h5disp('measurements.hdf5')

%% Plotting measurements

nodes_name = ["RT-browning","RT-fm","RT-ustar","D-ebc","D-guesthouse","D-moran"];   % Hardcoded :(

fname = './measurements_3.json'; 
fid = fopen(fname); 
raw = fread(fid,inf); 
str = char(raw'); 
fclose(fid); 
data = jsondecode(str);

% Get tx names
tx_nodes = fieldnames(data);

% Get nodes name str
tx_nodes_str = string(tx_nodes);
for i=1:length(tx_nodes_str)
    tx_nodes_str(i) = strrep(tx_nodes_str(i),'_','-');  % Replacing "_" with "-"
end

% Data structures
all_rssi = cell(length(tx_nodes),length(tx_nodes));     % All rssi
avg_rssi = zeros(length(tx_nodes));                     % Avg rssi
all_sinr = cell(length(tx_nodes),length(tx_nodes));     % All sinr
avg_sinr = zeros(length(tx_nodes));                     % Avg sinr

% Get data
for tx=1:length(tx_nodes)       % Cycle for tx nodes
    rx_nodes = fieldnames(data.(tx_nodes{tx}));
    
    for rx=1:length(rx_nodes)   % Cycle for rx nodes
        
        % Cycle to get rx id to store data
        for i=1:length(tx_nodes)
            if strcmp(tx_nodes{i}, rx_nodes{rx})
                rx_id = i;
                break
            end
        end
        
        % Store data
        all_rssi{tx,rx_id} = data.(tx_nodes{tx}).(rx_nodes{rx})(:,1);
        avg_rssi(tx,rx_id) = mean(data.(tx_nodes{tx}).(rx_nodes{rx})(:,1));
        all_sinr{tx,rx_id} = data.(tx_nodes{tx}).(rx_nodes{rx})(:,2);
        avg_sinr(tx,rx_id) = mean(data.(tx_nodes{tx}).(rx_nodes{rx})(:,2));

    end


end

% Putting nan
for i=1:length(tx_nodes)
    avg_rssi(i,i) = nan;
    avg_sinr(i,i) = nan;
end

% Plot heatmap for sinr
h = heatmap(nodes_name, nodes_name, avg_sinr,'MissingDataColor','1.00,1.00,1.00','FontSize',11);%,'Colormap',cool);
colormap(flipud(summer))                 % Set colormap
old_warning_state = warning('off', 'MATLAB:structOnObject');
hxp = struct(h);                        % Generate a warning
warning(old_warning_state);
% hxp.Axes.XAxisLocation = 'top';         % Force x label to the top
h.XLabel = 'RX Node';
h.YLabel = 'TX Node';
h.CellLabelFormat = '%.2f';
h.Title = 'Average SINR';
% h.FontSize = 8;
% orient(fig,'landscape')
set(gca,'FontSize',15);


fprintf('Done!\n');
