nohup python pet_bustm.py > ./output/bustm/run.log 2>&1 &
nohup python pet_chid.py > ./output/chid/run.log 2>&1 &
nohup python pet_csl.py > ./output/csl/run.log 2>&1 &
nohup python pet_csldcp.py > ./output/csldcp/run.log 2>&1 &
nohup python pet_iflytek.py > ./output/iflytek/run.log 2>&1 &
nohup python pet_eprstmt.py > ./output/eprstmt/run.log 2>&1 &
nohup python pet_ocnli.py > ./output/ocnli/run.log 2>&1 &
nohup python pet_tnews.py > ./output/tnews/run.log 2>&1 &
nohup python pet_wsc.py > ./output/wsc/run.log 2>&1 &

nohup python pet_bustm.py -tt predict > ./output/bustm/eval.log 2>&1 &
nohup python pet_chid.py -tt predict > ./output/chid/eval.log 2>&1 &
nohup python pet_csl.py -tt predict > ./output/csl/eval.log 2>&1 &
nohup python pet_csldcp.py -tt predict > ./output/cslscp/eval.log 2>&1 &
nohup python pet_eprstmt.py -tt predict > ./output/eprstmt/eval.log 2>&1 &
nohup python pet_iflytek.py -tt predict > ./output/iflytek/eval.log 2>&1 &
nohup python pet_tnews.py -tt predict > ./output/tnews/eval.log 2>&1 &
nohup python pet_wsc.py -tt predict > ./output/wsc/eval.log 2>&1 &
