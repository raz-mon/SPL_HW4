import sys
import os
import Repository as rp
import DTO


# read the config text, build from it DTO objects and creating the database with the DAO
def build_db(args):
    if os.path.isfile(args[1]):  # check if config.txt exists
        config_file = args[1]
        with open(config_file) as input_file:
            entries = input_file.readline().split(',')
            num_vaccines = int(entries[0])  #
            num_suppliers = int(entries[1])
            num_clinics = int(entries[2])
            num_logistics = int(entries[3][:-1])

            Vaccine_DTO_list = []
            Supplier_DTO_list = []
            Clinic_DTO_list = []
            Logistic_DTO_list = []

            # save all DTOs
            for i in range(num_vaccines):  # read each line from config.txt (only vaccines)
                line = input_file.readline().split(',')
                vac_DTO = DTO.Vaccine(line[0], line[1], line[2], line[3][:-1])  # Creating vaccine DTO
                Vaccine_DTO_list.insert(len(Vaccine_DTO_list), vac_DTO)
            for i in range(num_suppliers):  # read each line from config.txt (only suppliers)
                line = input_file.readline().split(',')
                sup_DTO = DTO.Supplier(line[0], line[1], line[2][:-1])  # Creating supplier DTO
                Supplier_DTO_list.insert(len(Supplier_DTO_list), sup_DTO)
            for i in range(num_clinics):  # read each line from config.txt (only clinics)
                line = input_file.readline().split(',')
                clin_DTO = DTO.Clinic(line[0], line[1], line[2], line[3][:-1])  # Creating clinic DTO
                Clinic_DTO_list.insert(len(Clinic_DTO_list), clin_DTO)
            for i in range(num_logistics):  # read each line from config.txt (only logistics)
                line = input_file.readline().split(',')
                if line[3].find('\n') != -1:  # dealing the case of last row (ends without \n)
                    log_DTO = DTO.Logistic(line[0], line[1], line[2], line[3][:-1])  # Creating logistic DTO
                else:
                    log_DTO = DTO.Logistic(line[0], line[1], line[2], line[3])
                Logistic_DTO_list.insert(len(Logistic_DTO_list), log_DTO)

            rp.repo.create_tables()

            for i in range(num_logistics):
                rp.repo.Logistics.insert(Logistic_DTO_list[i])  # inserting logistics DTO to database via DAO

            for i in range(num_suppliers):
                rp.repo.Suppliers.insert(Supplier_DTO_list[i])  # inserting suppliers DTO to database via DAO

            for i in range(num_vaccines):
                rp.repo.Vaccines.insert(Vaccine_DTO_list[i])  # inserting vaccines DTO to database via DAO

            for i in range(num_clinics):
                rp.repo.Clinics.insert(Clinic_DTO_list[i])  # inserting clinics DTO to database via DAO


def main(args):
    build_db(args)  # void function that builds the db, from the data gotten in the config file.
    open(args[3], 'w').close()
    if os.path.isfile(args[2]):  # check if order.txt exists
        with open(args[2]) as inputfile:
            for line in inputfile:  # reading each line from orders
                content = line.split(',')
                if len(content) == 2:  # i.e send shipment message
                    if content[1].find('\n') != -1:
                        send_shipment(content[0], int(content[1][:-1]))
                        update_output(1, args[3])
                    else:  # this is the last line
                        send_shipment(content[0], int(content[1]))
                        update_output(0, args[3])
                else:  # i.e receive shipment message
                    if content[2].find('\n') != -1:
                        receive_shipment(content[0], int(content[1]), content[2][:-1])
                        update_output(1, args[3])
                    else:  # this is the last line
                        receive_shipment(content[0], int(content[1]), content[2])
                        update_output(0, args[3])


def receive_shipment(name_, amount, date):
    # 1. Insert a line in to the vaccines table.
    max_id = rp.repo.Vaccines.get_max_id()

    # get the id of the supplier
    name_id = rp.repo.Suppliers.get_id(name_)
    vac_dto = DTO.Vaccine(max_id + 1, date, name_id, amount)
    vac_dao = rp.repo.Vaccines
    vac_dao.insert(vac_dto)

    # 2. update count_received at the logistics table where name = name
    #  Note: This maybe should be done by a DAO. Check this out.
    log_id = rp.repo.Suppliers.get_logistic(name_)

    current_amount = rp.repo.Logistics.get_current_amount_received(log_id)
    rp.repo.Logistics.update_count_received(current_amount, amount, log_id)


def send_shipment(location, amount):
    # Reduce demand field at the relevant clinic.
    clinic_id = rp.repo.Clinics.get_clinic_id_by_location(location)
    rp.repo.Clinics.reduce_demand(clinic_id, amount)

    # increase count_sent at the relevant logistic (the one that the specidied clinic works with
    log_id = rp.repo.Clinics.get_logistic(clinic_id)
    rp.repo.Logistics.update_count_sent(amount, log_id)

    # Update vaccines table
    curr_amount = amount
    while curr_amount > 0:  # need vaccines
        #   Creating the current vaccines list, and calculating the oldest vaccine
        #   in the inventory
        inventory_list = rp.repo.Vaccines.get_vaccines()
        dates = rp.repo.Vaccines.get_vaccines_dates()
        oldest_date = min(dates)[0]

        #   finding the oldest vaccine index in the list
        index = 0
        for i in range(len(inventory_list)):
            if inventory_list[i].date == oldest_date:
                index = i
                break
        # current vaccine has enough quantity for the amount
        if inventory_list[index].quantity > curr_amount:
            rp.repo.Vaccines.update_quantity(inventory_list[index], inventory_list[index].quantity - curr_amount)
            curr_amount = 0
        else:  # Delete current vaccine due to zero quantity and updating current amout
            curr_amount = curr_amount - inventory_list[index].quantity
            rp.repo.Vaccines.delete_vac(inventory_list[index])


#   write new line in output file
def update_output(a, path):
    output = open(path, "a")
    total_inventory = 0
    total_demand = 0
    total_received = 0
    total_sent = 0

    inventory = rp.repo.Vaccines.get_vaccines_quantities()  # receiving vaccines quantities from database
    demand = rp.repo.Clinics.get_clinics_demands()  # receiving clinic's demand quantities from database
    received = rp.repo.Logistics.get_logistics_count_received()  # receiving logistic's count received from database
    sent = rp.repo.Logistics.get_logistics_count_sent()  # receiving logistic's count sent from database

    # summation of all lists into a total sum
    for i in range(len(inventory)):
        total_inventory += inventory[i][0]
    for i in range(len(demand)):
        total_demand += demand[i][0]
    for i in range(len(received)):
        total_received += received[i][0]
    for i in range(len(sent)):
        total_sent += sent[i][0]

    if a == 1:
        output.write(str(total_inventory) + ',' + str(total_demand) +
                     ',' + str(total_received) + ',' + str(total_sent) + '\n')
    elif a == 0:
        output.write(str(total_inventory) + ',' + str(total_demand) + ',' + str(total_received) + ',' + str(total_sent))


if __name__ == '__main__':
    main(sys.argv)
