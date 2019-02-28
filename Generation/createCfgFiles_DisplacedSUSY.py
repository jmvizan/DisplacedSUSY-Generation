import argparse
import os
from string import Template

def computeWidth(ctau):

    # Function which receives a decay length value in (mm) and returns the width of the particle

    HSLAH = 6.582119624E-25 # hslash value in GeV*s
    tau = ctau*1.0E-3/3.0E8 # lifetime in seconds
    width = HSLAH/tau # width in GeV

    return width


def formatParameters(heading, parameters_string):

    # Receives a string of the form 'M_SQUARK	M_CHI	CTAU'
    heading = heading.split('\t')
    parameters_string = parameters_string.split('\t')

    # Format stuff:
    if '' in heading: heading.remove('') # supress empty values
    if '' in parameters_string: parameters_string.remove('') # supress empty values
 
    params = {}
    for j in range(0, len(heading)):
        if '\n' in heading[j]: heading[j] = heading[j].replace('\n', '')
        params[heading[j]] = float(parameters_string[j])

    # Derived quantities and format fixing
    if 'CTAU' in heading and 'WIDTH' not in heading:
        params['WIDTH'] = computeWidth(params['CTAU']) 
    if 'N' in heading: params['N'] = int(params['N'])


    return params


def createCfgFile(params_dict):

    ### Create the python config file
    # filename
    GEN_CFF_DIR = 'GEN_cff_files/'
    GEN_ROOT_DIR = '../GEN_root_files/'
    cfg_filename_Template = Template(GEN_CFF_DIR + 'DisplacedSUSY_squarkToQuarkChi_MSquark_${MSQUARK}_MChi_${MCHI}_ctau_${CTAU}mm_TuneCP5_14TeV_pythia8_cff.py')
    root_filename_Template = Template(GEN_ROOT_DIR+'EXO-DisplacedSUSY_squarkToQuarkChi_MSquark_${MSQUARK}_MChi_${MCHI}_ctau_${CTAU}mm_TuneCP5_14TeV_pythia8_GEN.root')
    cfg_filename = cfg_filename_Template.safe_substitute(params_dict)
    root_filename = root_filename_Template.safe_substitute(params_dict)
    cfg_filename = cfg_filename.replace(".0", "")
    root_filename = root_filename.replace(".0", "")    
    params_dict['GEN_ROOT_NAME'] = root_filename

    # config file
    input_filename = open("Templates/TEMPLATE_DisplacedSUSY_squarkToQuarkChi_MSquark_MSQUARK_MChi_MCHI_ctau_CTAUmm_TuneCP5_14TeV_pythia8_cff.py", 'r')
    cfg_text = input_filename.read()
    cfg_Template = Template(cfg_text)
    cfg_text = cfg_Template.safe_substitute(params_dict)

    output_filename = open(cfg_filename, 'w')
    output_filename.write(cfg_text)
    
    input_filename.close()
    output_filename.close()


def createListOfCommands(params_dict):

    ### Define the names of the config and root files 
    cfg_filename_Template = Template('DisplacedSUSY_squarkToQuarkChi_MSquark_${MSQUARK}_MChi_${MCHI}_ctau_${CTAU}mm_TuneCP5_14TeV_pythia8_cff_${STEP}.py')
    root_filename_Template = Template('EXO-DisplacedSUSY_squarkToQuarkChi_MSquark_${MSQUARK}_MChi_${MCHI}_ctau_${CTAU}mm_TuneCP5_14TeV_pythia8_${STEP}.root')

    step_list = ['PRPremix_Step1', 'PRPremix', 'miniAOD', 'nanoAOD']

    for step in step_list:
        params_dict['STEP'] = step # Update with every step
        params_dict[step+'_CFG_NAME'] = cfg_filename_Template.safe_substitute(params_dict).replace('.0', '')
        params_dict[step+'_ROOT_NAME'] = root_filename_Template.safe_substitute(params_dict).replace('.0', '')

    ### Define the commands
    PRPremix_Step1_command = """cmsDriver.py step1 --filein file:${GEN_ROOT_NAME} --fileout file:${PRPremix_Step1_ROOT_NAME}  --pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer17PrePremix-MCv2_correctPU_94X_mc2017_realistic_v9-v1/GEN-SIM-DIGI-RAW" --mc --eventcontent PREMIXRAW --datatier GEN-SIM-RAW --conditions 94X_mc2017_realistic_v11 --step DIGIPREMIX_S2,DATAMIX,L1,DIGI2RAW,HLT:2e34v40 --nThreads 8 --datamix PreMix --era Run2_2017 --python_filename ${PRPremix_Step1_CFG_NAME} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 1751 || exit $? ;"""
    PRPremix_command = """cmsDriver.py step2 --filein file:${PRPremix_Step1_ROOT_NAME} --fileout file:${PRPremix_ROOT_NAME} --mc --eventcontent AODSIM --runUnscheduled --datatier AODSIM --conditions 94X_mc2017_realistic_v11 --step RAW2DIGI,RECO,RECOSIM,EI --nThreads 8 --era Run2_2017 --python_filename ${PRPremix_CFG_NAME} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 1751 || exit $? ;"""
    miniAOD_command = """cmsDriver.py step1 --filein file:${PRPremix_ROOT_NAME} --fileout file:${miniAOD_ROOT_NAME} --mc --eventcontent MINIAODSIM --runUnscheduled --datatier MINIAODSIM --conditions 94X_mc2017_realistic_v14 --step PAT --nThreads 4 --scenario pp --era Run2_2017,run2_miniAOD_94XFall17 --python_filename ${miniAOD_CFG_NAME} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 4800 || exit $? ;"""
    nanoAOD_command = """cmsDriver.py step1 --filein file:${miniAOD_ROOT_NAME} --fileout file:${nanoAOD_ROOT_NAME} --mc --eventcontent NANOEDMAODSIM --datatier NANOAODSIM --conditions 94X_mc2017_realistic_v14 --step NANO --nThreads 2 --era Run2_2017,run2_nanoAOD_94XMiniAODv2 --python_filename ${nanoAOD_CFG_NAME} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 10000 || exit $? ;"""

    params_dict['PRPremix_Step1_COMMAND'] = Template(PRPremix_Step1_command).safe_substitute(params_dict)
    params_dict['PRPremix_COMMAND'] = Template(PRPremix_command).safe_substitute(params_dict)
    params_dict['miniAOD_COMMAND'] = Template(miniAOD_command).safe_substitute(params_dict)
    params_dict['nanoAOD_COMMAND'] = Template(nanoAOD_command).safe_substitute(params_dict)


    ### Write them into a file
    filename = Template('RunningCommands/DisplacedSUSY_squarkToQuarkChi_MSquark_${MSQUARK}_MChi_${MCHI}_ctau_${CTAU}mm_TuneCP5_14TeV_pythia8_running_commands.txt').safe_substitute(params_dict).replace('.0', '')
    command_file = open(filename, 'w')
    for step in step_list: 
        command_file.write(params_dict[step+'_COMMAND'])
        command_file.write('\n')
        command_file.write('\n')
    command_file.close()
     

if __name__ == '__main__':

    ##########  Parser object  ################################################# 
    desc = """ > Usage: \n 
               >> python createCfgFiles_DisplacedSUSY.py --parameters [parameters file] (-- verbose)
           """
    parser = argparse.ArgumentParser(description = desc)
    parser.add_argument('--parameters', action = 'store', type = str, dest = 'parameters', help = 'Get the parameters of the SUSY model')
    parser.add_argument('-v', '--verbose', action = 'store_true', dest = 'verbose', help = 'Turn on the verbose mode')
    args = parser.parse_args()


    ##########  Config file creation  ########################################## 
    parameters_file = open(args.parameters, 'r')
    parameters_list = parameters_file.readlines()
    heading = parameters_list[0]

    if args.verbose:
        print('>>> Parameters of the model parameters file:')
        print('>>>')
        output_text = ""
        for element in heading.split('\t'):
            output_text += str(element) + ', '
        print('>>> '+output_text[-2])


    for n in range(1, len(parameters_list)):
        line = parameters_list[n]
        params = formatParameters(heading, line) # returns an object with the parameters of the model
        print(params)
        createCfgFile(params)
        createListOfCommands(params)
