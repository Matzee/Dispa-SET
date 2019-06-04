import dispaset as ds



def test_excel_config():
    config=ds.load_config_excel('../ConfigFiles/ConfigTest.xlsx')
    config[""] == "Simulations/simulation_test"
    config['SimulationDirectory'] = sheet.cell_value(17, 2)
    config['WriteExcel'] = sheet.cell_value(18, 2)
    config['WriteGDX'] = sheet.cell_value(19, 2)
    config['WritePickle'] = sheet.cell_value(20, 2)
    config['GAMS_folder'] = sheet.cell_value(21, 2)
    config['cplex_path'] = sheet.cell_value(22, 2)
    
    try: 
        config["CEP"] = sheet.cell_value(151, 2)
    except: # config sheet without CEP cell leads to out of bounds error
        config["CEP"] = None

    config['StartDate'] = xlrd.xldate_as_tuple(sheet.cell_value(30, 2), wb.datemode)
    config['StopDate'] = xlrd.xldate_as_tuple(sheet.cell_value(31, 2), wb.datemode)
    config['HorizonLength'] = int(sheet.cell_value(32, 2))
    config['LookAhead'] = int(sheet.cell_value(33, 2))

    config['SimulationType'] = sheet.cell_value(46, 2)
    config['ReserveCalculation'] = sheet.cell_value(47, 2)
    config['AllowCurtailment'] = sheet.cell_value(48, 2)
    #! TODO WRITE THE EXCEL CONFIG!