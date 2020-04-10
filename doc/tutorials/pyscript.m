fprintf(1,'Executing %s at %s:\n',mfilename(),datestr(now));
ver,
try,
        out_path = pwd
        out_file = fullfile(out_path, 'reref_grids')
        fpath = '/usr/local/MATLAB/R2018a/toolbox/MEEG/fieldtrip-20200327/'
        addpath(fpath)
        disp(fpath)
        ft_defaults
        load('/home/pasca/Tools/python/packages/neuropycon/ephypype/examples/ieeg/SubjectUCI29_data.mat');
        cfg             = [];
        cfg.channel     = {'LPG*', 'LTG*'};
        cfg.reref       = 'yes';
        cfg.refchannel  = 'all';
        cfg.refmethod   = 'avg';
        reref_grids = ft_preprocessing(cfg, data);
        save(out_file, 'reref_grids')
        
,catch ME,
fprintf(2,'MATLAB code threw an exception:\n');
fprintf(2,'%s\n',ME.message);
if length(ME.stack) ~= 0, fprintf(2,'File:%s\nName:%s\nLine:%d\n',ME.stack.file,ME.stack.name,ME.stack.line);, end;
end;