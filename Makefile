PYTHON = python3

# Output directory
OUTPUT_DIR = outputs

# Targets
all: $(OUTPUT_DIR) run

$(OUTPUT_DIR):
	mkdir -p $(OUTPUT_DIR)

run:
	$(PYTHON) mdp.py -tol 0.001 -iter 100 -i inputs/input1.txt > $(OUTPUT_DIR)/output1.txt
	$(PYTHON) mdp.py -tol 0.001 -iter 100 -i inputs/input2.txt > $(OUTPUT_DIR)/output2.txt
	$(PYTHON) mdp.py -min -tol 0.001 -iter 100 -i inputs/input3.txt > $(OUTPUT_DIR)/output3.txt
	$(PYTHON) mdp.py -tol 0.001 -iter 100 -i inputs/input4.txt > $(OUTPUT_DIR)/output4.txt
	$(PYTHON) mdp.py -tol 0.001 -iter 100 -i inputs/input5.txt > $(OUTPUT_DIR)/output5.txt
	$(PYTHON) mdp.py -df 0.9 -tol 0.001 -iter 100 -i inputs/input6.txt > $(OUTPUT_DIR)/output6.txt

clean:
	rm -f *.pyc
	rm -rf outputs
