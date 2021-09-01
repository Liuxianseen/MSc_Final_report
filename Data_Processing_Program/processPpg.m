function processPpg(fname)

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
end