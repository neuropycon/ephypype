fprintf(1,'Executing %s at %s:\n',mfilename(),datestr(now));
ver,
try,
        fpath = '/usr/local/MATLAB/R2018a/toolbox/MEEG/fieldtrip-20200327/'
        addpath(fpath)
        disp(fpath)
        ft_defaults
        load('/home/pasca/Tools/python/packages/neuropycon/ephypype/examples/ieeg/SubjectUCI29_data.mat');
        depths = {'RAM*', 'RHH*', 'RTH*', 'ROC*', 'LAM*','LHH*', 'LTH*'};
        for d = 1:numel(depths)
            cfg             = [];
            cfg.channel     = ft_channelselection(depths{d}, data.label);
            cfg.reref       = 'yes';
            cfg.refchannel  = 'all';
            cfg.refmethod   = 'bipolar';
            cfg.updatesens  = 'yes';
            reref_depths{d} = ft_preprocessing(cfg, data);
        end
        cfg            = [];
        cfg.appendsens = 'yes';
        reref_data = ft_appenddata(cfg, reref_depths{:});
        save('/home/pasca/Tools/python/packages/neuropycon/ephypype/examples/reref_data.mat', 'reref_data')
        
,catch ME,
fprintf(2,'MATLAB code threw an exception:\n');
fprintf(2,'%s\n',ME.message);
if length(ME.stack) ~= 0, fprintf(2,'File:%s\nName:%s\nLine:%d\n',ME.stack.file,ME.stack.name,ME.stack.line);, end;
end;