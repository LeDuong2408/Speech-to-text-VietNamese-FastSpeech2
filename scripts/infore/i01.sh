#wget https://huggingface.co/datasets/ntt123/infore/resolve/main/infore_16k_denoised.zip -O ./raw_data/infore.zip
mkdir ./raw_data/
mkdir ./raw_data/infore
unzip ./raw_data/infore.zip -d ./raw_data/infore
rename 's/\.txt$/.lab/' ./raw_data/infore/*.txt
rm ./raw_data/infore.zip