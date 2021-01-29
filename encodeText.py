import os
import Repository as rp
import DTO
import DAO

def encode(args):
    if(os.path.isfile(args[1])):
        configFile = args[1]
        with open(configFile) as inputfile:
            entries = inputfile.readline().split(',')
            numVaccines = int(entries[0])
            numSuppliers = int(entries[1])
            numClinics = int(entries[2])
            numLogistics = int(entries[3][:-1])

            repo = rp._Repository()
            repo.create_tables()

            for i in range(numVaccines):
                line = inputfile.readline().split(',')
                vac_DTO = DTO.Vaccine(line[0], line[1], line[2], line[3][:-1])
                repo.Vaccines.insert(vac_DTO)

            for i in range(numSuppliers):
                line = inputfile.readline().split(',')
                sup_DTO = DTO.Supplier(line[0], line[1], line[2][:-1])
#                sup_DAO = repo.Suplliers
                repo.Suppliers.insert(sup_DTO)

            for i in range(numClinics):
                line = inputfile.readline().split(',')
                clin_DTO = DTO.Clinic(line[0], line[1], line[2], line[3][:-1])
                repo.Clinics.insert(clin_DTO)

            for i in range(numLogistics):
                line = inputfile.readline().split(',')
                log_DTO = DTO.Logistic(line[0], line[1], line[2], line[3][:-1])
                repo.Logistics.insert(log_DTO)
