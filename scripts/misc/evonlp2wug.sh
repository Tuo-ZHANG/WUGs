echo $(tput bold)$BASH_SOURCE$(tput sgr0)
scriptsdir=${0%/*}

dir=.
mkdir -p $dir/source
wget https://codalab.lisn.upsaclay.fr/my/datasets/download/c018bcd6-7f4e-4e8e-95f9-8d29ef6ca6da -nc -P $dir/source/
mv $dir/source/c018bcd6-7f4e-4e8e-95f9-8d29ef6ca6da $dir/source/starting-kit.zip
tar xvzf $dir/source/starting-kit.zip -C $dir/source/

datadir=$dir/wugdata/
mkdir -p $datadir
python3 $dir/evonlp2wug.py $dir/source/TempoWiC_Starting_Kit/data/train.data.jl $dir/source/TempoWiC_Starting_Kit/data/train.labels.tsv $datadir