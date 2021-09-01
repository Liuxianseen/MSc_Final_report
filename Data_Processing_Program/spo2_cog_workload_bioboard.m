% % % finger and ear spO2 script harry davies 31/01/2020
clear all
close all

%%
fname = 'ppgData.bin';
BLOCKSIZE_1 = 0;
    BLOCKSIZE_2 = 116;
    BLOCKSIZE_3 = 0;
    offset = 0;
     sensorWordSize = 4;
    keywordSize =4;
    timestampSize = 4;
    timestep = 30e-6;

    fid = fopen(fname,'r');
    ppg_raw = fread(fid,'uint8');
    ppg_raw = ppg_raw';
    %get file size
    fseek(fid,0,1);
    fsize = ftell(fid);
    frewind(fid);
    %work out how many blocks and read them in
    fclose(fid)

    keyword = 'Time';
    keywordHex = [84 105 109 101];

    a = strfind(ppg_raw, keywordHex);
    if a(1) > 5
        disp('offset found');
        offset = a(1)-4;
        ppg_raw = ppg_raw(a(1)-4:end);
        a=strfind(ppg_raw, keywordHex);
    end
    b = diff(a);
    c = diff(b);
    if sum(c) >0
        error('There may be a problem in the data - timestamps are irregular');
    end

    blockSize = b(1);
    if blockSize== BLOCKSIZE_1
        Number_of_LEDs = 1;
    elseif blockSize== BLOCKSIZE_2
        Number_of_LEDs = 2;
    elseif blockSize== BLOCKSIZE_3
        Number_of_LEDs = 3;
    else
            error('unknown blocksize');
    end

    nBlocks = floor(length(ppg_raw)/blockSize );
    ppg_raw = ppg_raw(1:nBlocks*blockSize);
    ppgBlock = reshape(ppg_raw,[blockSize,nBlocks])';
    ppgBlock(:,1:sensorWordSize) = [];
    blockSize = blockSize - sensorWordSize;
%     ppgBlock = zeros(nBlocks,blockSize);
%     for i=1: nBlocks
%     ppgBlock(i,:) = fread(fid,blockSize);
%     end
%     fclose(fid);
    %Break each block up into segments (assumes fixed length rather than
    %looking for 'Time' keyword





    segSize = 17*3 * Number_of_LEDs + keywordSize + timestampSize;
    nSegs = floor((blockSize )/segSize);

    blockDataSize = 17*3 * Number_of_LEDs * nSegs;

    ppgTs = zeros(nSegs*nBlocks,1);
    template = 1:blockSize;
    %Create a logical array with 1s where the timestamps are
    TStemplate = (mod(template-1,segSize) >= (keywordSize)) & (mod(template-1,segSize) < (timestampSize+keywordSize)) & (template <= nSegs*segSize);
    %create a logical array with 1s where the data is
    dataTemplate = (mod(template-1,segSize) >= (timestampSize+keywordSize)) & (template <= nSegs*segSize);
    ppgData = zeros(blockDataSize*nBlocks,1);
    blockData = zeros(blockDataSize,1);
    for i=1:nBlocks
    %For each block get the data into the blockData vector, then remove it all leaving timestamps
        block = ppgBlock(i,:);
        blockData = block(dataTemplate); 
        block(~TStemplate) = [];
    %convert 4 little endian bytes into 32 bit value
        blockTs = block(1:4:end) + 2^8*(block(2:4:end)) + 2^16*(block(3:4:end)) + 2^24*(block(4:4:end));


        ppgData((i-1)*blockDataSize+1:(i-1)*blockDataSize+blockDataSize) = blockData;
        ppgTs((i-1)*nSegs+1:i*nSegs) = blockTs;
    end
    dPpgTs = diff(ppgTs);
    figure;
     subplot(2,1,1); plot(ppgTs*timestep); title('PPG timestamps (should be a nice diagonal line)');
     subplot(2,1,2); plot(dPpgTs*timestep);title('PPG differential timestamps ( should be ~flat line <10% variation)');

    d1 = bitshift(ppgData(1:3:end),16);
    d2 = bitshift(ppgData(2:3:end),8);
    d3 = ppgData(3:3:end);

    d = d1+d2+d3;


    if Number_of_LEDs == 1
        red = d;
    end
    if Number_of_LEDs == 2
        red = d(1:2:end);
        ir = d(2:2:end);
        figure; plot (red/median(red));hold on; plot(ir/median(ir));
        title('raw normalised red and ir data');
        aWin = 1;
        wsize2 = 5;
        bWin2 = (1/wsize2)*ones(1,wsize2);
        smooth_raw_red = filter(bWin2,aWin,d(1:2:end));
        figure; try; findpeaks(smooth_raw_red,'MinPeakProminence',5,'Annotate','extents','MinPeakDistance',round((60/200)*(1000/32))); catch; end;
        title('annotated peaks on smoothed red data');
        try;
        [pks,locs,w,p] = findpeaks(smooth_raw_red,'MinPeakProminence',5,'Annotate','extents','MinPeakDistance',round((60/200)*(1000/32)));
        gaps = diff(locs)*32/1000;
        figure; plot (locs(1:end-1)*32/1000,60./gaps);
        title('heart rate estimate');

        catch;
        end;
    end

    if Number_of_LEDs ==3 
        red = d(1:3:end);
        ir = d(2:3:end);
        green = d(3:3:end);
        figure; plot (red/median(red));hold on; plot(ir/median(ir)); plot(green/median(green));
        title('raw normalised red, ir and green data');
        legend('red','ir','green');
    end
    
    ir_ear_raw = ir;
    red_ear_raw = red;
    
    ppgStartTime = ppgTs(1)-round(mean(diff(ppgTs)));
    ppgTimeStampVector_ear_raw = interp1(1:17:length(red_ear_raw)-2, (ppgTs(1:end)), 1:length(red_ear_raw));
    ppgTimeStampVectorSeconds_ear_raw = (ppgTimeStampVector_ear_raw /31250);

    %% process PPG data
    trig_s = 0;
    for ind = 1:length(ir_ear_raw)-100
        if trig_s == 0
            start_cond = sum(ir_ear_raw(ind:ind+100)<20000,1);
            if start_cond == 0
                ear_start = ind;
                trig_s = 1;
            end
        end
    end
    
    
    ir_ear = ir_ear_raw(ear_start:end);
    red_ear = red_ear_raw(ear_start:end);
    ppgTimeStampVectorSeconds_ear = ppgTimeStampVectorSeconds_ear_raw(ear_start:end);
    
    % corrections for offset jumps
    start_ear = 1;
    increment = 2.6e05;
    
    for i = start_ear:length(ir_ear) - 1
        ir_ear(i) = ir_ear(i) - floor(ir_ear(i)/262200)*262200;
    end
    
    for i = start_ear:length(red_ear) - 1
        red_ear(i) = red_ear(i) - floor(red_ear(i)/262200)*262200;
    end
    
    % filtering
    av = 16;
    fs = 1000/av;
    ma_window = (av*1000)/16;
    lp = 0.9;
    hp = 30;
    

  % figure;
    % hold on
    % plot(time_point_store);
    % plot(ppgTimeStampVectorSeconds_ear(time_index_store_PPG));
    %% extract peaks from ppg data
    
    
    red_ear_filt = bandpass(detrend(red_ear),[lp, hp],fs);
    ir_ear_filt = bandpass(detrend(ir_ear),[lp, hp],fs);
    
    ir_ear_resp = zeros(length(ir_ear_filt),1);
    ir_ear_resp(50:end) = bandpass(detrend(ir_ear(50:end)),[0.2, hp],fs);
    
%     figure;
%     plot(ir_ear_resp)
%     figure;
%     plot(up);
%     title('Resp filtered');
%     
        figure;
        hold on
        title('Ear AC');
        plot(ppgTimeStampVectorSeconds_ear,ir_ear_filt);
        plot(ppgTimeStampVectorSeconds_ear,red_ear_filt);
        ylim([-2000 2000]);
    
    red_ear_filt_raw = red_ear_filt;
    ir_ear_filt_raw = ir_ear_filt;
    
    prominence1 = 100;
 
    [ir_ear_pks_max, ir_ear_locs_max, ir_ear_widths_max, ir_ear_proms_max] = findpeaks(ir_ear_filt,'MinPeakDistance',30,'MinPeakProminence',prominence1);
    [ir_ear_pks_min, ir_ear_locs_min, ir_ear_widths_min, ir_ear_proms_min] = findpeaks(movmean(-ir_ear_filt,5),'MinPeakDistance',30,'MinPeakProminence',prominence1);
    
    %%
    %figure; plot(ir_ear_pks_max);
%     switch_t = 0;
%     for t = 1:length(ir_ear_locs_max)
%         if ir_ear_locs_max(t) > time_index_store_PPG(1) && switch_t == 0
%             t_start = t;
%             switch_t = 1;
%         end
%     end
    t_start = 60;
    for t = t_start:length(ir_ear_pks_max)
        if ir_ear_pks_max(t) > 2*(mean(ir_ear_pks_max(t-4:t-1)))
            ir_ear_pks_max(t) = mean(ir_ear_pks_max(t-4:t-1));
        end
        if ir_ear_pks_max(t) < 0.3*(mean(ir_ear_pks_max(t-4:t-1)))
            ir_ear_pks_max(t) = mean(ir_ear_pks_max(t-4:t-1));
        end
    end
    figure; plot(ir_ear_pks_max);
    figure; plot(ir_ear_pks_min);
    for t = t_start:length(ir_ear_pks_min)
        if ir_ear_pks_min(t) > 2*(mean(ir_ear_pks_min(t-4:t-1)))
            ir_ear_pks_min(t) = mean(ir_ear_pks_min(t-4:t-1));
        end
        if ir_ear_pks_min(t) < 0.3*(mean(ir_ear_pks_min(t-4:t-1)))
            ir_ear_pks_min(t) = mean(ir_ear_pks_min(t-4:t-1));
        end
    end
    %figure; plot(ir_ear_pks_min);
    
    %%
    
    ir_ear_peak_max = interp1(ir_ear_locs_max, ir_ear_pks_max, 1:length(ir_ear_filt));
    ir_ear_peak_min = -interp1(ir_ear_locs_min, ir_ear_pks_min, 1:length(ir_ear_filt));
    ir_ear_width_max_sig = interp1(ir_ear_locs_max, ir_ear_widths_max, 1:length(ir_ear_filt));
    ir_ear_width_min_sig = interp1(ir_ear_locs_min, ir_ear_widths_min, 1:length(ir_ear_filt));
    ir_ear_proms_max_sig = interp1(ir_ear_locs_max, ir_ear_proms_max, 1:length(ir_ear_filt));
    
    prominence2 = 30;
    [red_ear_pks_max, red_ear_locs_max,red_ear_widths,red_ear_proms] = findpeaks(movmean(red_ear_filt,1),'MinPeakDistance',30,'MinPeakProminence',prominence2);
    [red_ear_pks_min, red_ear_locs_min] = findpeaks(movmean(-red_ear_filt,5),'MinPeakDistance',30,'MinPeakProminence',prominence2);
    
        %%
%        figure; plot(red_ear_pks_max);
    for t = t_start:length(red_ear_pks_max)
        if red_ear_pks_max(t) > 2*(mean(red_ear_pks_max(t-4:t-1)))
            red_ear_pks_max(t) = mean(red_ear_pks_max(t-4:t-1));
        end
        if red_ear_pks_max(t) < 0.3*(mean(red_ear_pks_max(t-4:t-1)))
            red_ear_pks_max(t) = mean(red_ear_pks_max(t-4:t-1));
        end
    end
    %figure; plot(red_ear_pks_max);
    %figure; plot(red_ear_pks_min);
    for t = t_start:length(red_ear_pks_min)
        if red_ear_pks_min(t) > 2*(mean(red_ear_pks_min(t-4:t-1)))
            red_ear_pks_min(t) = mean(red_ear_pks_min(t-4:t-1));
        end
        if red_ear_pks_min(t) < 0.3*(mean(red_ear_pks_min(t-4:t-1)))
            red_ear_pks_min(t) = mean(red_ear_pks_min(t-4:t-1));
        end
    end
    %figure; plot(red_ear_pks_min);
    
    %%
    figure;
    hold on
    plot(ppgTimeStampVectorSeconds_ear,-1*ir_ear_filt);
    plot(ppgTimeStampVectorSeconds_ear-0.05,-1*red_ear_filt);
    %xlim([115 125])
    xlabel('Time (s)');
    ylabel('Amplitude (a.u)');
    legend('Infrared PPG','Red PPG');
    
    
    figure;
        hold on
        title('Ear AC');
        plot(ir_ear_filt);
        plot(red_ear_filt);
        plot(red_ear_locs_max,red_ear_pks_max,'r');
        plot(red_ear_locs_min,-red_ear_pks_min,'r');
        plot(ir_ear_locs_max,ir_ear_pks_max,'b');
        plot(ir_ear_locs_min,-ir_ear_pks_min,'b');
        ylim([-2000 2000]);
    
    red_ear_peak_max = interp1(red_ear_locs_max, red_ear_pks_max, 1:length(red_ear_filt));
    red_ear_peak_min = -interp1(red_ear_locs_min, red_ear_pks_min, 1:length(red_ear_filt));
    red_ear_proms_max_sig = interp1(red_ear_locs_max, red_ear_proms, 1:length(red_ear_filt));
    
    red_ear_base = movmean((red_ear_peak_max+red_ear_peak_min)/2,10);
    ir_ear_base = movmean((ir_ear_peak_max+ir_ear_peak_min)/2,10);
    
    red_ear_filt = movmean((abs(red_ear_peak_max)+abs(red_ear_peak_min))/2,1);
    ir_ear_filt = movmean((abs(ir_ear_peak_max)+abs(ir_ear_peak_min))/2,1);
    
    %     figure;
    %     subplot(2,1,1);
    %     title('AC ear');
    %     hold on
    %     plot(ppgTimeStampVectorSeconds_ear,red_ear_filt);
    %     plot(ppgTimeStampVectorSeconds_ear,ir_ear_filt);
    %     ylim([-1000 1000]);
    % dc filtering
    lpf = 0.1;
    ir_ear_dc = lowpass(ir_ear,lpf,fs);
    red_ear_dc = lowpass(red_ear,lpf,fs);
    
    %     subplot(2,1,2);
    %     title('DC ear');
    %     hold on
    %     plot(ppgTimeStampVectorSeconds_ear,ir_ear_dc)
    %     plot(ppgTimeStampVectorSeconds_ear,red_ear_dc);
    %     plot(ppgTimeStampVectorSeconds_ear,green_ear);
    %% spo2 calculation
    w_rms = 1;
    rms_red_ear = zeros(1,length(red_ear)-w_rms);
    rms_ir_ear = zeros(1,length(red_ear)-w_rms);
    mean_redw_ear = zeros(1,length(red_ear)-w_rms);
    mean_irw_ear = zeros(1,length(red_ear)-w_rms);
    
    for i = 1:(length(red_ear) - w_rms)
        rms_red_ear(i) = rms(red_ear_filt(i:(i+w_rms)));
        rms_ir_ear(i) = rms(ir_ear_filt(i:(i+w_rms)));
        mean_redw_ear(i) = mean(red_ear_dc(i:(i+w_rms)));
        mean_irw_ear(i) = mean(ir_ear_dc(i:(i+w_rms)));
    end
    
    %norm_red_ear = mean(rms_red_ear(10000:20000));
    %norm_ir_ear = mean(rms_ir_ear(10000:20000)) %calculate this again later when we have slots and do full normalisation
    spo2_ear = ((rms_red_ear./mean_redw_ear)./(rms_ir_ear./mean_irw_ear));
    spo2_ear_final = movmean((104 - 17*(spo2_ear)),1);
    
    red_ratio = rms_red_ear./mean_redw_ear;
    ir_ratio = rms_ir_ear./mean_irw_ear;
    
    load('baseline_comp.mat');
    seconds_start = 350;
    figure;
    hold on
    plot(ppgTimeStampVectorSeconds_ear(1:end-1)-seconds_start,medfilt1(spo2_ear_final,1000),'LineWidth',1,'Color',[0.749019622802734 0 0.749019622802734]);
    plot(ppgTimeStampVectorSeconds_ear_base(1:end-1)-210,medfilt1(spo2_ear_final_base,1000),'LineWidth',1,'Color',[1 0 0]);
    %plot(time_fin,spo2_fin,'Marker','*','LineWidth',1,'LineStyle','--',...
    %'Color',[0 0.447058826684952 0.74117648601532])
    title('In-ear SpO_{2} of Cognitive Workload Task in Altitude 1');
    xlabel('Time(s)');
    ylabel('SpO_{2} (%)');
    xlim([10 310]);
    legend('Workload','Baseline');
    ylim([85 98]);
%     title(num2str(file_ind-2));
    
    %plot(ppgTimeStampVectorSeconds_ear(((w_rms/2)+1):end-(w_rms/2)),spo2_ear_final);
    %plot(ppgTimeStampVectorSeconds_ear(((w_rms/2)+1):end-(w_rms/2)),(rms_red_ear/norm_red_ear)./(rms_ir_ear/norm_ir_ear));
    %ylim([90 100]);
%     ylim([0.5 1.5])
%     xlabel('Time (s)');
%     ylabel('SpO_{2} (%)');
%     grid on
%     title('Spo2')
    %% HR calculation
    peak_locs = ppgTimeStampVectorSeconds_ear(ir_ear_locs_max);
    rri = diff(peak_locs);
    HR_sig = 60./rri;
    
    %     figure;
    %     plot(peak_locs(2:end),HR_sig);
    %     title('Heart Rate');
    %     xlabel('Time(s)');
    %     ylabel('HR (BPM)');
    
    HR_sig_interp = interp1(peak_locs(2:end-1),HR_sig(1:end-1),ppgTimeStampVectorSeconds_ear);
    
    % figure;
    % plot(ppgTimeStampVectorSeconds_ear,HR_sig_interp)
    %% BR calculation
    %
    ppgTimeStampVectorSeconds_ear_resp = rmmissing(ppgTimeStampVectorSeconds_ear);
    resp_prom = 10;
%     if strcmp(directory,'devyani2_rand') == 1
%         resp_prom = 5;
%     end
    [pks_resp,locs_resp] = findpeaks((movmean(ir_ear_resp(1:length(ppgTimeStampVectorSeconds_ear_resp)),150)),ppgTimeStampVectorSeconds_ear_resp,'MinPeakDistance',1,'MinPeakWidth',0.5,'MinPeakProminence',resp_prom);
    figure;
    hold on
    plot(ppgTimeStampVectorSeconds_ear,ir_ear_resp);
    plot(ppgTimeStampVectorSeconds_ear,(movmean(ir_ear_resp,150)));
    plot(locs_resp,pks_resp,'o')
    % figure;
    % plot(locs_resp,pks_resp);
    % figure;
    % plot(locs_resp(2:end),diff(locs_resp));
    BRI = diff(locs_resp);
    BRI_sig_interp = interp1(locs_resp(2:end-1),BRI(1:end-1),ppgTimeStampVectorSeconds_ear);
    figure;
    hold on
    plot(ppgTimeStampVectorSeconds_ear,BRI_sig_interp)
    plot(locs_resp(2:end),diff(locs_resp),'o');
    
    
    Breathing_mag_interp = interp1(locs_resp,pks_resp,ppgTimeStampVectorSeconds_ear);
    BRI_sig_interp = (60./BRI_sig_interp);
    figure; plot(BRI_sig_interp);
    %     figure;
    %     plot(ppgTimeStampVectorSeconds_ear,Breathing_mag_interp)
    % figure;
    % subplot(2,1,1);
    % plot(ppgTimeStampVectorSeconds_ear(7.1e04:7.4e04),ir_ear(7.1e04:7.4e04));
    % xlim([1119 1166]);
    % ylabel('Amplitude');
    % xlabel('Time (s)');
    % title('Raw ear-PPG');
    % subplot(2,1,2);
    % plot(ppgTimeStampVectorSeconds_ear(7.1e04:7.4e04),ir_ear_resp(7.1e04:7.4e04));
    % xlim([1119 1166]);
    % ylabel('Filtered amplitude');
    % xlabel('Time (s)');
    % title('Envelope change due to breathing');
    
    
    resp_signal_plot = bandpass(ir_ear_resp,[0.18 0.3],62.5);
    figure;
    hold on
    plot(ppgTimeStampVectorSeconds_ear,-1*ir_ear_resp);
    plot(ppgTimeStampVectorSeconds_ear,-1.5*resp_signal_plot,'LineWidth',2);
    xlim([110 130]);
    xlabel('Time (s)');
    ylabel('Amplitude (a.u)');
    legend('In-ear PPG','Respiration modulation');

